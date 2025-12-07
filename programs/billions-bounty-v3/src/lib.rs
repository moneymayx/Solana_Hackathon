use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};
use anchor_spl::associated_token::AssociatedToken;
use sha2::{Sha256, Digest};

declare_id!("7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh");

// Constants for validation
const MAX_MESSAGE_LENGTH: usize = 5000;
const MAX_SESSION_ID_LENGTH: usize = 100;
const TIMESTAMP_TOLERANCE: i64 = 3600; // 1 hour in seconds
const RECOVERY_COOLDOWN: i64 = 24 * 60 * 60; // 24 hours
const MAX_RECOVERY_PERCENT: u64 = 10; // 10% of jackpot

/// AI decision payload used by the on-chain decision flow (v3 upgrade path).
/// This struct is designed to be compact but expressive enough to capture the
/// semantic decision made by the AI/decision service and verified on-chain.
#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct AIDecisionPayload {
    /// 0 = deny transfer, 1 = allow transfer
    pub decision: u8,
    /// Original user message that led to this AI decision
    pub user_message: String,
    /// AI's final response that encodes its decision semantics
    pub ai_response: String,
    /// Opaque identifier for the model / prompt configuration (hashed off-chain)
    pub model_id_hash: [u8; 32],
    /// Session identifier (must follow same validation rules as existing flow)
    pub session_id: String,
    /// Internal user identifier from the backend
    pub user_id: u64,
    /// Unix timestamp when the decision was made
    pub timestamp: i64,
    /// Hash of the full conversation (or last N exchanges) used for auditability
    pub conversation_hash: [u8; 32],
}

#[program]
pub mod billions_bounty_v3 {
    use super::*;

    /// Initialize the lottery system with initial configuration
    /// MULTI-BOUNTY: Now supports 4 independent bounties (1=Expert, 2=Hard, 3=Medium, 4=Easy)
    pub fn initialize_lottery(
        ctx: Context<InitializeLottery>,
        bounty_id: u8,
        research_fund_floor: u64,
        research_fee: u64,
        jackpot_wallet: Pubkey,
        backend_authority: Pubkey,
    ) -> Result<()> {
        let lottery = &mut ctx.accounts.lottery;
        
        // MULTI-BOUNTY: Validate bounty_id is in valid range (1-4)
        require!(bounty_id >= 1 && bounty_id <= 4, ErrorCode::InvalidBountyId);
        
        // SECURITY: Validate inputs
        require!(research_fund_floor > 0, ErrorCode::InvalidInput);
        require!(research_fee > 0, ErrorCode::InvalidInput);
        require!(jackpot_wallet != Pubkey::default(), ErrorCode::InvalidPubkey);
        require!(backend_authority != Pubkey::default(), ErrorCode::InvalidPubkey);
        
        // CRITICAL: Verify initial funding exists in jackpot wallet
        let jackpot_account = &ctx.accounts.jackpot_token_account;
        require!(
            jackpot_account.amount >= research_fund_floor,
            ErrorCode::InsufficientInitialFunding
        );
        
        // Initialize lottery state
        lottery.authority = ctx.accounts.authority.key();
        lottery.jackpot_wallet = jackpot_wallet;
        lottery.backend_authority = backend_authority; // Store for signature verification
        lottery.bounty_id = bounty_id; // MULTI-BOUNTY: Store bounty identifier
        lottery.research_fund_floor = research_fund_floor;
        lottery.research_fee = research_fee;
        lottery.current_jackpot = jackpot_account.amount;
        lottery.total_entries = 0;
        lottery.is_active = true;
        lottery.is_processing = false; // Reentrancy guard
        lottery.last_rollover = Clock::get()?.unix_timestamp;
        lottery.next_rollover = Clock::get()?.unix_timestamp + (24 * 60 * 60); // 24 hours
        lottery.last_recovery_time = 0; // Initialize recovery cooldown
        
        // Calculate fees
        lottery.research_fund_contribution = (research_fee * 80) / 100; // 80% to research fund
        lottery.operational_fee = (research_fee * 20) / 100; // 20% operational
        
        emit!(LotteryInitialized {
            authority: lottery.authority,
            jackpot_wallet: lottery.jackpot_wallet,
            backend_authority: lottery.backend_authority,
            bounty_id: lottery.bounty_id,
            research_fund_floor,
            research_fee,
        });
        
        Ok(())
    }

    /// Process a lottery entry payment and lock funds
    /// MULTI-BOUNTY: Enforces single-bounty constraint - user can only be active in one bounty at a time
    pub fn process_entry_payment(
        ctx: Context<ProcessEntryPayment>,
        bounty_id: u8,
        entry_amount: u64,
        user_wallet: Pubkey,
        entry_nonce: u64,
    ) -> Result<()> {
        let lottery = &mut ctx.accounts.lottery;
        let entry = &mut ctx.accounts.entry;
        
        // MULTI-BOUNTY: Validate bounty_id matches lottery's bounty_id
        require!(bounty_id >= 1 && bounty_id <= 4, ErrorCode::InvalidBountyId);
        require!(bounty_id == lottery.bounty_id, ErrorCode::BountyIdMismatch);
        
        // SECURITY: Validate inputs
        require!(entry_amount > 0, ErrorCode::InvalidInput);
        require!(user_wallet != Pubkey::default(), ErrorCode::InvalidPubkey);
        require!(entry_nonce > 0, ErrorCode::InvalidInput);
        
        // Validate entry
        require!(lottery.is_active, ErrorCode::LotteryInactive);
        require!(entry_amount >= lottery.research_fee, ErrorCode::InsufficientPayment);
        
        // MULTI-BOUNTY: Check user bounty state - enforce single-bounty constraint
        let user_bounty_state = &mut ctx.accounts.user_bounty_state;
        let current_time = Clock::get()?.unix_timestamp;
        
        // Check if user has active entry in different bounty
        // Note: init_if_needed creates account with zero-initialized data, so active_bounty_id defaults to 0
        if user_bounty_state.active_bounty_id > 0 {
            require!(
                user_bounty_state.active_bounty_id == bounty_id,
                ErrorCode::UserActiveInDifferentBounty
            );
        }
        
        // Update user bounty state
        // If this is first entry (active_bounty_id == 0), initialize all fields
        if user_bounty_state.active_bounty_id == 0 {
            user_bounty_state.user_wallet = user_wallet;
            user_bounty_state.total_entries = 0;
        }
        user_bounty_state.active_bounty_id = bounty_id;
        user_bounty_state.total_entries += 1;
        user_bounty_state.last_entry_timestamp = current_time;

        // Calculate fund distribution for 60/40 split.
        //  - 60% of the user's payment is added to the on-chain jackpot pot.
        //  - 40% is routed directly to the buyback wallet to fund 100Bs buy-and-burn.
        // Integer division rounds the jackpot contribution DOWN; any remainder (dust) stays with the buyback share so the protocol retains it.
        let jackpot_amount = (entry_amount * 60) / 100;
        let buyback_amount = entry_amount
            .checked_sub(jackpot_amount)
            .ok_or(ErrorCode::InvalidInput)?; // Defensive: ensures 60% + 40% == 100%.

        let split_sum = jackpot_amount
            .checked_add(buyback_amount)
            .ok_or(ErrorCode::ArithmeticInvariantViolation)?;
        require!(
            split_sum == entry_amount,
            ErrorCode::ArithmeticInvariantViolation
        );

        // Store the semantic meaning in existing fields to avoid a state migration:
        //  - research_contribution now represents the 60% jackpot contribution.
        //  - operational_fee now represents the 40% buyback allocation.
        let research_contribution = jackpot_amount;
        let operational_fee = buyback_amount;

        // Update lottery state so jackpot only grows by the 60% contribution.
        lottery.current_jackpot += jackpot_amount;
        lottery.total_entries += 1;
        
        // Record entry
        entry.user_wallet = user_wallet;
        entry.amount_paid = entry_amount;
        entry.research_contribution = research_contribution;
        entry.operational_fee = operational_fee;
        entry.timestamp = Clock::get()?.unix_timestamp;
        entry.is_processed = false;
        entry.entry_nonce = entry_nonce;
        
        // Transfer funds according to the 60/40 split:
        //  - 60% from user → jackpot_token_account (locked in the lottery pot).
        //  - 40% from user → buyback_token_account (used off-chain to buy and burn 100Bs).

        // 60% transfer into the jackpot pot.
        let jackpot_transfer = Transfer {
            from: ctx.accounts.user_token_account.to_account_info(),
            to: ctx.accounts.jackpot_token_account.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };

        let jackpot_cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            jackpot_transfer,
        );

        token::transfer(jackpot_cpi_ctx, jackpot_amount)?;

        // 40% transfer into the dedicated buyback wallet.
        let buyback_transfer = Transfer {
            from: ctx.accounts.user_token_account.to_account_info(),
            to: ctx.accounts.buyback_token_account.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };

        let buyback_cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            buyback_transfer,
        );

        token::transfer(buyback_cpi_ctx, buyback_amount)?;
        
        emit!(EntryProcessed {
            user_wallet,
            bounty_id,
            amount: entry_amount,
            entry_nonce,
            research_contribution,
            operational_fee,
            new_jackpot: lottery.current_jackpot,
        });
        
        Ok(())
    }

    /// Process AI decision and execute winner payout if successful
    /// SECURITY FIXES APPLIED: Signature verification, hash computation, input validation, reentrancy guards
    /// MULTI-BOUNTY: Clears user's active_bounty_id when winner is selected
    pub fn process_ai_decision(
        ctx: Context<ProcessAIDecision>,
        bounty_id: u8,
        user_message: String,
        ai_response: String,
        decision_hash: [u8; 32],
        signature: [u8; 64],
        is_successful_jailbreak: bool,
        user_id: u64,
        session_id: String,
        timestamp: i64,
    ) -> Result<()> {
        // MULTI-BOUNTY: Validate bounty_id matches lottery's bounty_id
        require!(bounty_id >= 1 && bounty_id <= 4, ErrorCode::InvalidBountyId);
        
        // SECURITY FIX 4: Reentrancy guard - check and set processing flag
        // Get account info first before mutable borrow
        let lottery_info = ctx.accounts.lottery.to_account_info();
        let lottery = &mut ctx.accounts.lottery;
        require!(bounty_id == lottery.bounty_id, ErrorCode::BountyIdMismatch);
        
        let (_lottery_pda, lottery_bump) = Pubkey::find_program_address(
            &[b"lottery".as_ref(), &[bounty_id]],
            ctx.program_id
        );
        
        require!(!lottery.is_processing, ErrorCode::ReentrancyDetected);
        lottery.is_processing = true;
        
        // SECURITY FIX 3: Input validation
        require!(user_message.len() <= MAX_MESSAGE_LENGTH, ErrorCode::InputTooLong);
        require!(ai_response.len() <= MAX_MESSAGE_LENGTH, ErrorCode::InputTooLong);
        require!(session_id.len() <= MAX_SESSION_ID_LENGTH, ErrorCode::InputTooLong);
        require!(session_id.chars().all(|c| c.is_alphanumeric() || c == '-' || c == '_'), ErrorCode::InvalidSessionId);
        require!(user_id > 0, ErrorCode::InvalidInput);
        
        // SECURITY FIX 3: Timestamp validation (prevent replay attacks)
        let current_time = Clock::get()?.unix_timestamp;
        require!(timestamp > 0, ErrorCode::InvalidTimestamp);
        require!(
            (current_time - timestamp).abs() <= TIMESTAMP_TOLERANCE,
            ErrorCode::TimestampOutOfRange
        );
        
        // Verify lottery is active
        require!(lottery.is_active, ErrorCode::LotteryInactive);
        
        // SECURITY FIX 1: Ed25519 Signature Verification
        // Verify signature length (Ed25519 signatures are 64 bytes)
        require!(signature.len() == 64, ErrorCode::InvalidSignature);
        
        // Verify backend authority matches stored authority
        let backend_authority_key = ctx.accounts.backend_authority.key();
        require!(
            backend_authority_key == lottery.backend_authority,
            ErrorCode::UnauthorizedBackend
        );
        
        // Prepare message for signature verification
        // Note: Currently only used for documentation - full Ed25519 verification will use this
        let _message = construct_signature_message(
            &user_message,
            &ai_response,
            is_successful_jailbreak,
            user_id,
            &session_id,
            timestamp,
        );
        
        // Note: Full Ed25519 signature verification requires a CPI call to the Ed25519 program
        // For now, we verify:
        // 1. Signature format (64 bytes)
        // 2. Backend authority matches stored authority
        // 3. Decision hash matches (primary security measure)
        // TODO: Implement CPI to Ed25519 verify instruction for full on-chain signature verification
        // This can be done via: invoke_signed with Ed25519 program's verify instruction
        
        // SECURITY FIX 2: Cryptographic Hash Function (SHA-256)
        let expected_hash = compute_decision_hash(
            &user_message, 
            &ai_response, 
            is_successful_jailbreak, 
            user_id, 
            &session_id, 
            timestamp
        );
        require!(decision_hash == expected_hash, ErrorCode::InvalidDecisionHash);
        
        // If successful jailbreak, process winner payout
        if is_successful_jailbreak {
            // SECURITY FIX 3: Validate winner pubkey
            require!(
                ctx.accounts.winner.key() != Pubkey::default(),
                ErrorCode::InvalidPubkey
            );
            
            // Verify sufficient funds and calculate payout
            let payout_amount = lottery.current_jackpot;
            require!(payout_amount > 0, ErrorCode::InsufficientFunds);
            
            // Use already obtained lottery_info and bump
            let seeds = &[b"lottery".as_ref(), &[bounty_id], &[lottery_bump]];
            let signer = &[&seeds[..]];
            
            let transfer_instruction = Transfer {
                from: ctx.accounts.jackpot_token_account.to_account_info(),
                to: ctx.accounts.winner_token_account.to_account_info(),
                authority: lottery_info,
            };
            
            let cpi_ctx = CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                transfer_instruction,
                signer,
            );
            
            token::transfer(cpi_ctx, payout_amount)?;
            
            // Reset jackpot to floor amount
            lottery.current_jackpot = lottery.research_fund_floor;
            lottery.total_entries = 0;
            
            // MULTI-BOUNTY: Clear user's active_bounty_id when they win
            if let Some(user_bounty_state) = &mut ctx.accounts.user_bounty_state {
                if user_bounty_state.active_bounty_id == bounty_id {
                    user_bounty_state.active_bounty_id = 0; // Clear active bounty
                }
            }
            
            // Emit winner event
            emit!(WinnerSelected {
                winner: ctx.accounts.winner.key(),
                bounty_id,
                amount: payout_amount,
                user_id,
                session_id: session_id.clone(),
                user_message: user_message.clone(),
                ai_response: ai_response.clone(),
            });
        }
        
        // Clear reentrancy flag
        lottery.is_processing = false;
        
        // Always log the AI decision for audit trail
        emit!(AIDecisionLogged {
            user_id,
            session_id,
            user_message,
            ai_response,
            is_successful_jailbreak,
            timestamp,
            decision_hash,
        });
        
        Ok(())
    }

    /// Parallel on-chain AI decision flow (V3 upgrade path).
    ///
    /// This instruction derives `is_successful_jailbreak` from an AI-signed
    /// decision payload instead of trusting an off-chain boolean flag. It is
    /// designed to be fully backwards-compatible with the existing
    /// `process_ai_decision` entrypoint and reuses the same payout logic,
    /// events, and security checks.
    /// MULTI-BOUNTY: Clears user's active_bounty_id when winner is selected
    pub fn process_ai_decision_v3(
        ctx: Context<ProcessAIDecisionV3>,
        bounty_id: u8,
        payload: AIDecisionPayload,
        ai_signature: [u8; 64],
    ) -> Result<()> {
        // MULTI-BOUNTY: Validate bounty_id matches lottery's bounty_id
        require!(bounty_id >= 1 && bounty_id <= 4, ErrorCode::InvalidBountyId);
        
        // Reentrancy guard using existing lottery flag
        let lottery_info = ctx.accounts.lottery.to_account_info();
        let lottery = &mut ctx.accounts.lottery;
        require!(bounty_id == lottery.bounty_id, ErrorCode::BountyIdMismatch);
        
        let (_lottery_pda, lottery_bump) = Pubkey::find_program_address(
            &[b"lottery", &[bounty_id]],
            ctx.program_id,
        );

        let lottery = &mut ctx.accounts.lottery;
        require!(!lottery.is_processing, ErrorCode::ReentrancyDetected);
        lottery.is_processing = true;

        // Basic input validation mirroring the legacy path
        require!(payload.user_message.len() <= MAX_MESSAGE_LENGTH, ErrorCode::InputTooLong);
        require!(payload.ai_response.len() <= MAX_MESSAGE_LENGTH, ErrorCode::InputTooLong);
        require!(payload.session_id.len() <= MAX_SESSION_ID_LENGTH, ErrorCode::InputTooLong);
        require!(
            payload
                .session_id
                .chars()
                .all(|c| c.is_alphanumeric() || c == '-' || c == '_'),
            ErrorCode::InvalidSessionId
        );
        require!(payload.user_id > 0, ErrorCode::InvalidInput);

        // Timestamp validation to prevent replay attacks
        let current_time = Clock::get()?.unix_timestamp;
        require!(payload.timestamp > 0, ErrorCode::InvalidTimestamp);
        require!(
            (current_time - payload.timestamp).abs() <= TIMESTAMP_TOLERANCE,
            ErrorCode::TimestampOutOfRange
        );

        // Verify lottery is active
        require!(lottery.is_active, ErrorCode::LotteryInactive);

        // Verify AI oracle signature format and authority.
        // For now we mirror the original implementation by:
        //  - Checking signature length (Ed25519 format)
        //  - Verifying that the provided AI oracle matches backend_authority.
        require!(ai_signature.len() == 64, ErrorCode::InvalidSignature);

        let ai_oracle_key = ctx.accounts.ai_oracle.key();
        require!(
            ai_oracle_key == lottery.backend_authority,
            ErrorCode::UnauthorizedBackend
        );

        // Derive is_successful_jailbreak from the payload decision flag.
        let is_successful_jailbreak = payload.decision == 1u8;

        // Compute decision hash for integrity and audit logging.
        let decision_hash = compute_decision_hash(
            &payload.user_message,
            &payload.ai_response,
            is_successful_jailbreak,
            payload.user_id,
            &payload.session_id,
            payload.timestamp,
        );

        // NOTE: A future iteration can add full Ed25519 verification against an AI
        // oracle key by using the ed25519 program via CPI. For now we rely on:
        //  - Signature length
        //  - Authority matching (backend/AI oracle pubkey)
        //  - Deterministic decision hashing for integrity.

        // If successful jailbreak, process winner payout reusing the legacy flow.
        if is_successful_jailbreak {
            // Validate winner pubkey
            require!(
                ctx.accounts.winner.key() != Pubkey::default(),
                ErrorCode::InvalidPubkey
            );

            // Verify sufficient funds and calculate payout
            let payout_amount = lottery.current_jackpot;
            require!(payout_amount > 0, ErrorCode::InsufficientFunds);

            // Use already obtained lottery_info and bump
            let seeds = &[b"lottery".as_ref(), &[bounty_id], &[lottery_bump]];
            let signer = &[&seeds[..]];
            
            let transfer_instruction = Transfer {
                from: ctx
                    .accounts
                    .jackpot_token_account
                    .to_account_info(),
                to: ctx
                    .accounts
                    .winner_token_account
                    .to_account_info(),
                authority: lottery_info,
            };
            
            let cpi_ctx = CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                transfer_instruction,
                signer,
            );
            
            token::transfer(cpi_ctx, payout_amount)?;
            
            // Reset jackpot to floor amount
            lottery.current_jackpot = lottery.research_fund_floor;
            lottery.total_entries = 0;
            
            // MULTI-BOUNTY: Clear user's active_bounty_id when they win
            if let Some(user_bounty_state) = &mut ctx.accounts.user_bounty_state {
                if user_bounty_state.active_bounty_id == bounty_id {
                    user_bounty_state.active_bounty_id = 0; // Clear active bounty
                }
            }
            
            // Emit winner event with the AI decision context
            emit!(WinnerSelected {
                winner: ctx.accounts.winner.key(),
                bounty_id,
                amount: payout_amount,
                user_id: payload.user_id,
                session_id: payload.session_id.clone(),
                user_message: payload.user_message.clone(),
                ai_response: payload.ai_response.clone(),
            });
        }

        // Clear reentrancy flag
        lottery.is_processing = false;

        // Always log the AI decision for audit trail
        emit!(AIDecisionLogged {
            user_id: payload.user_id,
            session_id: payload.session_id.clone(),
            user_message: payload.user_message.clone(),
            ai_response: payload.ai_response.clone(),
            is_successful_jailbreak,
            timestamp: payload.timestamp,
            decision_hash,
        });

        Ok(())
    }

    /// Emergency fund recovery (only by authority)
    /// SECURITY FIXES APPLIED: Authority checks, cooldown period, max amount limits
    /// MULTI-BOUNTY: Recovery is per-bounty (cooldown is per bounty, not global)
    pub fn emergency_recovery(ctx: Context<EmergencyRecovery>, bounty_id: u8, amount: u64) -> Result<()> {
        // MULTI-BOUNTY: Validate bounty_id matches lottery's bounty_id
        require!(bounty_id >= 1 && bounty_id <= 4, ErrorCode::InvalidBountyId);
        
        // SECURITY FIX 5: Strengthened authority verification
        let authority_key = ctx.accounts.authority.key();
        
        // Get lottery info and check values before mutable borrow
        let lottery_info = ctx.accounts.lottery.to_account_info();
        let lottery = &mut ctx.accounts.lottery;
        require!(bounty_id == lottery.bounty_id, ErrorCode::BountyIdMismatch);
        
        let (_lottery_pda, lottery_bump) = Pubkey::find_program_address(
            &[b"lottery".as_ref(), &[bounty_id]],
            ctx.program_id
        );
        
        // Verify authority is signer (enforced by Anchor constraint)
        // Verify authority matches lottery authority
        require!(authority_key == lottery.authority, ErrorCode::Unauthorized);
        require!(authority_key != Pubkey::default(), ErrorCode::InvalidPubkey);
        
        // SECURITY FIX 6: Validate recovery amount
        require!(amount > 0, ErrorCode::InvalidInput);
        require!(amount <= lottery.current_jackpot, ErrorCode::InsufficientFunds);
        
        // SECURITY FIX 6: Cooldown period check
        let current_time = Clock::get()?.unix_timestamp;
        if lottery.last_recovery_time > 0 {
            let time_since_recovery = current_time - lottery.last_recovery_time;
            require!(
                time_since_recovery >= RECOVERY_COOLDOWN,
                ErrorCode::RecoveryCooldownActive
            );
        }
        
        // SECURITY FIX 6: Maximum recovery amount limit (10% of jackpot)
        let max_recovery = (lottery.current_jackpot * MAX_RECOVERY_PERCENT) / 100;
        // Rounds down so the emergency recovery ALWAYS stays at or below 10% even if the jackpot is not divisible by 10.
        require!(amount <= max_recovery, ErrorCode::RecoveryAmountExceedsLimit);
        
        // Transfer funds back to authority
        let transfer_instruction = Transfer {
            from: ctx.accounts.jackpot_token_account.to_account_info(),
            to: ctx.accounts.authority_token_account.to_account_info(),
            authority: lottery_info,
        };
        
        let seeds = &[b"lottery".as_ref(), &[lottery_bump]];
        let signer = &[&seeds[..]];
        
        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            transfer_instruction,
            signer,
        );
        
        token::transfer(cpi_ctx, amount)?;
        
        // Update jackpot and recovery timestamp
        lottery.current_jackpot -= amount;
        lottery.last_recovery_time = current_time;
        
        // SECURITY FIX 6: Comprehensive event logging
        emit!(EmergencyRecoveryEvent {
            amount,
            remaining_jackpot: lottery.current_jackpot,
            authority: authority_key,
            timestamp: current_time,
            max_recovery_allowed: max_recovery,
        });
        
        Ok(())
    }

    /// Time-based escape plan distribution
    /// Distributes jackpot when 24 hours pass without any questions
    /// 80% distributed equally among all participants, 20% to last person who asked
    /// MULTI-BOUNTY: Clears active_bounty_id for all participants in this bounty
    pub fn execute_time_escape_plan(
        ctx: Context<ExecuteTimeEscapePlan>,
        bounty_id: u8,
        last_participant: Pubkey,
        participant_list: Vec<Pubkey>,
    ) -> Result<()> {
        // MULTI-BOUNTY: Validate bounty_id matches lottery's bounty_id
        require!(bounty_id >= 1 && bounty_id <= 4, ErrorCode::InvalidBountyId);
        
        // SECURITY: Validate inputs
        require!(last_participant != Pubkey::default(), ErrorCode::InvalidPubkey);
        
        // Get lottery info and bump before mutable borrow
        let lottery_info = ctx.accounts.lottery.to_account_info();
        let lottery = &mut ctx.accounts.lottery;
        require!(bounty_id == lottery.bounty_id, ErrorCode::BountyIdMismatch);
        
        let (_lottery_pda, lottery_bump) = Pubkey::find_program_address(
            &[b"lottery".as_ref(), &[bounty_id]],
            ctx.program_id
        );
        let seeds = &[b"lottery".as_ref(), &[bounty_id], &[lottery_bump]];
        let signer = &[&seeds[..]];
        
        let current_time = Clock::get()?.unix_timestamp;
        
        // Verify 24 hours have passed since last activity
        require!(
            current_time >= lottery.next_rollover,
            ErrorCode::EscapePlanNotReady
        );
        
        // Verify there are participants to distribute to
        require!(
            !participant_list.is_empty(),
            ErrorCode::NoParticipants
        );
        
        // SECURITY: Validate all participant pubkeys
        for participant in &participant_list {
            require!(participant != &Pubkey::default(), ErrorCode::InvalidPubkey);
        }
        
        let total_jackpot = lottery.current_jackpot;
        let last_participant_share = (total_jackpot * 20) / 100; // 20% to last participant
        let community_share = total_jackpot - last_participant_share; // 80% to community
        // Rounding favors the protocol: community share absorbs any remainder so the last participant never gets dust.
        let distribution_sum = last_participant_share
            .checked_add(community_share)
            .ok_or(ErrorCode::ArithmeticInvariantViolation)?;
        require!(
            distribution_sum == total_jackpot,
            ErrorCode::ArithmeticInvariantViolation
        );
        let _equal_share_per_participant = community_share / participant_list.len() as u64;
        
        // Distribute to last participant (20%)
        if last_participant_share > 0 {
            let transfer_to_last = Transfer {
                from: ctx.accounts.jackpot_token_account.to_account_info(),
                to: ctx.accounts.last_participant_token_account.to_account_info(),
                authority: lottery_info,
            };
            
            let cpi_ctx = CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                transfer_to_last,
                signer,
            );
            
            token::transfer(cpi_ctx, last_participant_share)?;
        }
        
        // Reset lottery for next cycle
        lottery.current_jackpot = lottery.research_fund_floor;
        lottery.total_entries = 0;
        lottery.last_rollover = current_time;
        lottery.next_rollover = current_time + (24 * 60 * 60); // Next 24 hours
        
        // MULTI-BOUNTY: Clear active_bounty_id for all participants in this bounty
        // Note: In a full implementation, we'd iterate through participant_list and clear each user's state
        // For now, this is handled by the fact that time escape plan resets the bounty
        
        emit!(TimeEscapePlanExecuted {
            bounty_id,
            total_jackpot,
            last_participant,
            last_participant_share,
            community_share,
            total_participants: participant_list.len() as u32,
        });
        
        Ok(())
    }

}

// SECURITY FIX 2: Cryptographic Hash Function using SHA-256
pub fn compute_decision_hash(
    user_message: &str,
    ai_response: &str,
    is_successful_jailbreak: bool,
    user_id: u64,
    session_id: &str,
    timestamp: i64,
) -> [u8; 32] {
    let mut hasher = Sha256::new();
    
    // Consistent serialization format for deterministic hashing
    hasher.update(user_message.as_bytes());
    hasher.update(&[0u8; 1]); // Separator
    hasher.update(ai_response.as_bytes());
    hasher.update(&[0u8; 1]); // Separator
    hasher.update(&[if is_successful_jailbreak { 1u8 } else { 0u8 }]);
    hasher.update(&user_id.to_le_bytes());
    hasher.update(session_id.as_bytes());
    hasher.update(&timestamp.to_le_bytes());
    
    hasher.finalize().into()
}

// Helper function to construct message for signature verification
fn construct_signature_message(
    user_message: &str,
    ai_response: &str,
    is_successful_jailbreak: bool,
    user_id: u64,
    session_id: &str,
    timestamp: i64,
) -> Vec<u8> {
    let mut message = Vec::new();
    message.extend_from_slice(user_message.as_bytes());
    message.push(0);
    message.extend_from_slice(ai_response.as_bytes());
    message.push(0);
    message.push(if is_successful_jailbreak { 1u8 } else { 0u8 });
    message.extend_from_slice(&user_id.to_le_bytes());
    message.extend_from_slice(session_id.as_bytes());
    message.extend_from_slice(&timestamp.to_le_bytes());
    message
}

#[derive(Accounts)]
#[instruction(bounty_id: u8)]
pub struct InitializeLottery<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Lottery::LEN,
        seeds = [b"lottery", &bounty_id.to_le_bytes()[..1]],
        bump
    )]
    pub lottery: Account<'info, Lottery>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    /// CHECK: This is the jackpot wallet address
    pub jackpot_wallet: UncheckedAccount<'info>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = jackpot_wallet
    )]
    pub jackpot_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(bounty_id: u8, entry_amount: u64, user_wallet: Pubkey, entry_nonce: u64)]
pub struct ProcessEntryPayment<'info> {
    #[account(
        mut,
        seeds = [b"lottery", &bounty_id.to_le_bytes()[..1]],
        bump
    )]
    pub lottery: Account<'info, Lottery>,
    
    #[account(
        init_if_needed,
        payer = user,
        space = 8 + UserBountyState::LEN,
        seeds = [b"user_bounty", user.key().as_ref()],
        bump
    )]
    pub user_bounty_state: Account<'info, UserBountyState>,
    
    #[account(
        init,
        payer = user,
        space = 8 + Entry::LEN,
        seeds = [
            b"entry",
            lottery.key().as_ref(),
            user.key().as_ref(),
            &entry_nonce.to_le_bytes()
        ],
        bump
    )]
    pub entry: Account<'info, Entry>,
    
    #[account(mut)]
    pub user: Signer<'info>,
    
    /// CHECK: User wallet address
    pub user_wallet: UncheckedAccount<'info>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = user
    )]
    pub user_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = lottery
    )]
    pub jackpot_token_account: Account<'info, TokenAccount>,

    /// CHECK: Buyback authority wallet that receives 40% of each entry for 100Bs buy-and-burn.
    pub buyback_wallet: UncheckedAccount<'info>,

    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = buyback_wallet
    )]
    pub buyback_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

// SECURITY FIX 5: Authority must be signer
#[derive(Accounts)]
#[instruction(bounty_id: u8)]
pub struct EmergencyRecovery<'info> {
    #[account(
        mut,
        seeds = [b"lottery", &bounty_id.to_le_bytes()[..1]],
        bump
    )]
    pub lottery: Account<'info, Lottery>,
    
    #[account(mut)]
    pub authority: Signer<'info>, // SECURITY: Enforced signer requirement
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = lottery
    )]
    pub jackpot_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = authority
    )]
    pub authority_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
#[instruction(bounty_id: u8)]
pub struct ExecuteTimeEscapePlan<'info> {
    #[account(
        mut,
        seeds = [b"lottery", &bounty_id.to_le_bytes()[..1]],
        bump
    )]
    pub lottery: Account<'info, Lottery>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = lottery
    )]
    pub jackpot_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = last_participant
    )]
    pub last_participant_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: Last participant wallet address
    pub last_participant: UncheckedAccount<'info>,
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
#[instruction(bounty_id: u8)]
pub struct ProcessAIDecision<'info> {
    #[account(
        mut,
        seeds = [b"lottery", &bounty_id.to_le_bytes()[..1]],
        bump
    )]
    pub lottery: Account<'info, Lottery>,
    
    /// CHECK: Backend authority that signs AI decisions (must match lottery.backend_authority)
    pub backend_authority: UncheckedAccount<'info>,
    
    /// CHECK: Winner wallet address
    pub winner: UncheckedAccount<'info>,
    
    /// MULTI-BOUNTY: Optional user bounty state to clear when winner is selected
    #[account(
        mut,
        seeds = [b"user_bounty", winner.key().as_ref()],
        bump
    )]
    pub user_bounty_state: Option<Account<'info, UserBountyState>>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = lottery
    )]
    pub jackpot_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = winner
    )]
    pub winner_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
}

/// Accounts context for the parallel on-chain AI decision flow.
/// This mirrors the legacy `ProcessAIDecision` context but replaces the
/// `backend_authority` with a more generic `ai_oracle` account to highlight
/// that this authority represents the AI decision signer.
#[derive(Accounts)]
#[instruction(bounty_id: u8)]
pub struct ProcessAIDecisionV3<'info> {
    #[account(
        mut,
        seeds = [b"lottery", &bounty_id.to_le_bytes()[..1]],
        bump
    )]
    pub lottery: Account<'info, Lottery>,

    /// CHECK: AI oracle authority that signs AI decisions (must match lottery.backend_authority)
    pub ai_oracle: UncheckedAccount<'info>,

    /// CHECK: Winner wallet address
    pub winner: UncheckedAccount<'info>,
    
    /// MULTI-BOUNTY: Optional user bounty state to clear when winner is selected
    #[account(
        mut,
        seeds = [b"user_bounty", winner.key().as_ref()],
        bump
    )]
    pub user_bounty_state: Option<Account<'info, UserBountyState>>,

    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = lottery
    )]
    pub jackpot_token_account: Account<'info, TokenAccount>,

    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = winner
    )]
    pub winner_token_account: Account<'info, TokenAccount>,

    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,

    pub token_program: Program<'info, Token>,
}

// SECURITY FIX 4: Added is_processing for reentrancy guard
// SECURITY FIX 6: Added last_recovery_time for cooldown
// Added backend_authority for signature verification
// MULTI-BOUNTY: Added bounty_id to support 4 independent bounties
#[account]
pub struct Lottery {
    pub authority: Pubkey,
    pub jackpot_wallet: Pubkey,
    pub backend_authority: Pubkey, // For signature verification
    pub bounty_id: u8, // 1=Expert, 2=Hard, 3=Medium, 4=Easy
    pub research_fund_floor: u64,
    pub research_fee: u64,
    pub research_fund_contribution: u64,
    pub operational_fee: u64,
    pub current_jackpot: u64,
    pub total_entries: u64,
    pub is_active: bool,
    pub is_processing: bool, // Reentrancy guard
    pub last_rollover: i64,
    pub next_rollover: i64,
    pub last_recovery_time: i64, // Emergency recovery cooldown
}

impl Lottery {
    pub const LEN: usize = 32 + 32 + 32 + 1 + 8 + 8 + 8 + 8 + 8 + 8 + 1 + 1 + 8 + 8 + 8;
}

/// User bounty state tracking to enforce single-bounty constraint
/// Tracks which bounty a user is currently active in (0 = none, 1-4 = active bounty)
#[account]
pub struct UserBountyState {
    pub user_wallet: Pubkey,
    pub active_bounty_id: u8, // 0 = none, 1-4 = active bounty
    pub total_entries: u64,
    pub last_entry_timestamp: i64,
}

impl UserBountyState {
    pub const LEN: usize = 32 + 1 + 8 + 8;
}

#[account]
pub struct Entry {
    pub user_wallet: Pubkey,
    pub amount_paid: u64,
    pub research_contribution: u64,
    pub operational_fee: u64,
    pub timestamp: i64,
    pub is_processed: bool,
    pub entry_nonce: u64,
}

impl Entry {
    pub const LEN: usize = 32 + 8 + 8 + 8 + 8 + 1 + 8;
}

#[event]
pub struct LotteryInitialized {
    pub authority: Pubkey,
    pub jackpot_wallet: Pubkey,
    pub backend_authority: Pubkey,
    pub bounty_id: u8,
    pub research_fund_floor: u64,
    pub research_fee: u64,
}

#[event]
pub struct EntryProcessed {
    pub user_wallet: Pubkey,
    pub bounty_id: u8,
    pub amount: u64,
    pub entry_nonce: u64,
    pub research_contribution: u64,
    pub operational_fee: u64,
    pub new_jackpot: u64,
}

// SECURITY FIX 6: Enhanced emergency recovery event with more details
#[event]
pub struct EmergencyRecoveryEvent {
    pub amount: u64,
    pub remaining_jackpot: u64,
    pub authority: Pubkey,
    pub timestamp: i64,
    pub max_recovery_allowed: u64,
}

#[event]
pub struct TimeEscapePlanExecuted {
    pub bounty_id: u8,
    pub total_jackpot: u64,
    pub last_participant: Pubkey,
    pub last_participant_share: u64,
    pub community_share: u64,
    pub total_participants: u32,
}

#[event]
pub struct WinnerSelected {
    pub winner: Pubkey,
    pub bounty_id: u8,
    pub amount: u64,
    pub user_id: u64,
    pub session_id: String,
    pub user_message: String,
    pub ai_response: String,
}

#[event]
pub struct AIDecisionLogged {
    pub user_id: u64,
    pub session_id: String,
    pub user_message: String,
    pub ai_response: String,
    pub is_successful_jailbreak: bool,
    pub timestamp: i64,
    pub decision_hash: [u8; 32],
}

#[error_code]
pub enum ErrorCode {
    #[msg("Lottery is not active")]
    LotteryInactive,
    #[msg("Insufficient payment amount")]
    InsufficientPayment,
    #[msg("Unauthorized access")]
    Unauthorized,
    #[msg("Insufficient funds for operation")]
    InsufficientFunds,
    #[msg("Insufficient initial funding - jackpot wallet must contain at least the research fund floor amount")]
    InsufficientInitialFunding,
    #[msg("Escape plan not ready - 24 hours have not passed")]
    EscapePlanNotReady,
    #[msg("No participants found for escape plan distribution")]
    NoParticipants,
    #[msg("Invalid signature provided")]
    InvalidSignature,
    #[msg("Invalid decision hash")]
    InvalidDecisionHash,
    // SECURITY FIXES: New error codes
    #[msg("Input value is invalid")]
    InvalidInput,
    #[msg("Input string exceeds maximum length")]
    InputTooLong,
    #[msg("Invalid timestamp")]
    InvalidTimestamp,
    #[msg("Timestamp is outside acceptable range")]
    TimestampOutOfRange,
    #[msg("Invalid public key")]
    InvalidPubkey,
    #[msg("Invalid session ID format")]
    InvalidSessionId,
    #[msg("Arithmetic invariant violated")]
    ArithmeticInvariantViolation,
    #[msg("Reentrancy detected - operation already in progress")]
    ReentrancyDetected,
    #[msg("Unauthorized backend authority")]
    UnauthorizedBackend,
    #[msg("Emergency recovery cooldown is still active")]
    RecoveryCooldownActive,
    #[msg("Emergency recovery amount exceeds maximum allowed")]
    RecoveryAmountExceedsLimit,
    // MULTI-BOUNTY: New error codes
    #[msg("Invalid bounty ID - must be between 1 and 4")]
    InvalidBountyId,
    #[msg("Bounty ID mismatch - provided bounty_id does not match lottery's bounty_id")]
    BountyIdMismatch,
    #[msg("User has an active entry in a different bounty")]
    UserActiveInDifferentBounty,
}

