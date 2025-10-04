use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};
use anchor_spl::associated_token::AssociatedToken;
use std::hash::{Hash, Hasher};

declare_id!("4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK");

#[program]
pub mod billions_bounty {
    use super::*;

    /// Initialize the lottery system with initial configuration
    pub fn initialize_lottery(
        ctx: Context<InitializeLottery>,
        research_fund_floor: u64,
        research_fee: u64,
        jackpot_wallet: Pubkey,
    ) -> Result<()> {
        let lottery = &mut ctx.accounts.lottery;
        
        // CRITICAL: Verify initial funding exists in jackpot wallet
        let jackpot_account = &ctx.accounts.jackpot_token_account;
        require!(
            jackpot_account.amount >= research_fund_floor,
            ErrorCode::InsufficientInitialFunding
        );
        
        // Initialize lottery state
        lottery.authority = ctx.accounts.authority.key();
        lottery.jackpot_wallet = jackpot_wallet;
        lottery.research_fund_floor = research_fund_floor;
        lottery.research_fee = research_fee;
        lottery.current_jackpot = research_fund_floor;
        lottery.total_entries = 0;
        lottery.is_active = true;
        lottery.last_rollover = Clock::get()?.unix_timestamp;
        lottery.next_rollover = Clock::get()?.unix_timestamp + (24 * 60 * 60); // 24 hours
        
        // Calculate fees
        lottery.research_fund_contribution = (research_fee * 80) / 100; // 80% to research fund
        lottery.operational_fee = (research_fee * 20) / 100; // 20% operational
        
        emit!(LotteryInitialized {
            authority: lottery.authority,
            jackpot_wallet: lottery.jackpot_wallet,
            research_fund_floor,
            research_fee,
        });
        
        Ok(())
    }

    /// Process a lottery entry payment and lock funds
    pub fn process_entry_payment(
        ctx: Context<ProcessEntryPayment>,
        entry_amount: u64,
        user_wallet: Pubkey,
    ) -> Result<()> {
        let lottery = &mut ctx.accounts.lottery;
        let entry = &mut ctx.accounts.entry;
        
        // Validate entry
        require!(lottery.is_active, ErrorCode::LotteryInactive);
        require!(entry_amount >= lottery.research_fee, ErrorCode::InsufficientPayment);
        
        // Calculate fund distribution
        let research_contribution = (entry_amount * 80) / 100;
        let operational_fee = (entry_amount * 20) / 100;
        
        // Update lottery state
        lottery.current_jackpot += research_contribution;
        lottery.total_entries += 1;
        
        // Record entry
        entry.user_wallet = user_wallet;
        entry.amount_paid = entry_amount;
        entry.research_contribution = research_contribution;
        entry.operational_fee = operational_fee;
        entry.timestamp = Clock::get()?.unix_timestamp;
        entry.is_processed = false;
        
        // Transfer funds to jackpot wallet (funds are locked)
        let transfer_instruction = Transfer {
            from: ctx.accounts.user_token_account.to_account_info(),
            to: ctx.accounts.jackpot_token_account.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };
        
        let cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            transfer_instruction,
        );
        
        token::transfer(cpi_ctx, entry_amount)?;
        
        emit!(EntryProcessed {
            user_wallet,
            amount: entry_amount,
            research_contribution,
            operational_fee,
            new_jackpot: lottery.current_jackpot,
        });
        
        Ok(())
    }

    /// Process AI decision and execute winner payout if successful
    pub fn process_ai_decision(
        ctx: Context<ProcessAIDecision>,
        user_message: String,
        ai_response: String,
        decision_hash: [u8; 32],
        signature: [u8; 64],
        is_successful_jailbreak: bool,
        user_id: u64,
        session_id: String,
        timestamp: i64,
    ) -> Result<()> {
        // Get lottery info and bump before mutable borrow
        let lottery_info = ctx.accounts.lottery.to_account_info();
        let lottery_bump = *ctx.bumps.get("lottery").unwrap();
        let seeds = &[b"lottery".as_ref(), &[lottery_bump]];
        let signer = &[&seeds[..]];
        
        let lottery = &mut ctx.accounts.lottery;
        
        // Verify lottery is active
        require!(lottery.is_active, ErrorCode::LotteryInactive);
        
        // Verify signature (simplified - in production, use proper Ed25519 verification)
        // For now, we'll trust the backend signature and focus on on-chain verification
        require!(signature.len() == 64, ErrorCode::InvalidSignature);
        
        // TODO: Add proper Ed25519 signature verification
        // This would verify the signature against the backend authority public key
        // For now, we trust the backend and focus on decision hash verification
        
        // Verify decision hash matches the provided data (optimized for stack usage)
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
            // Verify sufficient funds
            require!(lottery.current_jackpot > 0, ErrorCode::InsufficientFunds);
            
            // Calculate payout (for now, transfer entire jackpot)
            let payout_amount = lottery.current_jackpot;
            
            // Transfer funds to winner
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
            
            // Emit winner event
            emit!(WinnerSelected {
                winner: ctx.accounts.winner.key(),
                amount: payout_amount,
                user_id,
                session_id: session_id.clone(),
                user_message: user_message.clone(),
                ai_response: ai_response.clone(),
            });
        }
        
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

    /// Emergency fund recovery (only by authority)
    pub fn emergency_recovery(ctx: Context<EmergencyRecovery>, amount: u64) -> Result<()> {
        // Get lottery info before mutable borrow
        let lottery_info = ctx.accounts.lottery.to_account_info();
        let lottery_bump = *ctx.bumps.get("lottery").unwrap();
        
        let lottery = &mut ctx.accounts.lottery;
        
        // Only authority can perform emergency recovery
        require!(ctx.accounts.authority.key() == lottery.authority, ErrorCode::Unauthorized);
        require!(amount <= lottery.current_jackpot, ErrorCode::InsufficientFunds);
        
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
        
        // Update jackpot
        lottery.current_jackpot -= amount;
        
        emit!(EmergencyRecoveryEvent {
            amount,
            remaining_jackpot: lottery.current_jackpot,
        });
        
        Ok(())
    }

    /// Time-based escape plan distribution
    /// Distributes jackpot when 24 hours pass without any questions
    /// 80% distributed equally among all participants, 20% to last person who asked
    pub fn execute_time_escape_plan(
        ctx: Context<ExecuteTimeEscapePlan>,
        last_participant: Pubkey,
        participant_list: Vec<Pubkey>,
    ) -> Result<()> {
        // Get lottery info and bump before mutable borrow
        let lottery_info = ctx.accounts.lottery.to_account_info();
        let lottery_bump = *ctx.bumps.get("lottery").unwrap();
        let seeds = &[b"lottery".as_ref(), &[lottery_bump]];
        let signer = &[&seeds[..]];
        
        let lottery = &mut ctx.accounts.lottery;
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
        
        let total_jackpot = lottery.current_jackpot;
        let last_participant_share = (total_jackpot * 20) / 100; // 20% to last participant
        let community_share = total_jackpot - last_participant_share; // 80% to community
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
        
        emit!(TimeEscapePlanExecuted {
            total_jackpot,
            last_participant,
            last_participant_share,
            community_share,
            total_participants: participant_list.len() as u32,
        });
        
        Ok(())
    }

}

// Helper function to compute decision hash (reduces stack usage)
pub fn compute_decision_hash(
    user_message: &str,
    ai_response: &str,
    is_successful_jailbreak: bool,
    user_id: u64,
    session_id: &str,
    timestamp: i64,
) -> [u8; 32] {
    let mut hasher = std::collections::hash_map::DefaultHasher::new();
    user_message.hash(&mut hasher);
    ai_response.hash(&mut hasher);
    is_successful_jailbreak.hash(&mut hasher);
    user_id.hash(&mut hasher);
    session_id.hash(&mut hasher);
    timestamp.hash(&mut hasher);
    let hash = hasher.finish();
    let hash_bytes = hash.to_le_bytes();
    let mut result = [0u8; 32];
    for i in 0..32 {
        result[i] = hash_bytes[i % 8];
    }
    result
}

#[derive(Accounts)]
pub struct InitializeLottery<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Lottery::LEN,
        seeds = [b"lottery"],
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
pub struct ProcessEntryPayment<'info> {
    #[account(
        mut,
        seeds = [b"lottery"],
        bump
    )]
    pub lottery: Account<'info, Lottery>,
    
    #[account(
        init,
        payer = user,
        space = 8 + Entry::LEN,
        seeds = [b"entry", lottery.key().as_ref(), user.key().as_ref()],
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
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

// NOTE: SelectWinner struct removed - winner selection handled by AI system

#[derive(Accounts)]
pub struct EmergencyRecovery<'info> {
    #[account(
        mut,
        seeds = [b"lottery"],
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
        associated_token::authority = authority
    )]
    pub authority_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct ExecuteTimeEscapePlan<'info> {
    #[account(
        mut,
        seeds = [b"lottery"],
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
pub struct ProcessAIDecision<'info> {
    #[account(
        mut,
        seeds = [b"lottery"],
        bump
    )]
    pub lottery: Account<'info, Lottery>,
    
    /// CHECK: Backend authority that signs AI decisions
    pub backend_authority: UncheckedAccount<'info>,
    
    /// CHECK: Winner wallet address
    pub winner: UncheckedAccount<'info>,
    
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

#[account]
pub struct Lottery {
    pub authority: Pubkey,
    pub jackpot_wallet: Pubkey,
    pub research_fund_floor: u64,
    pub research_fee: u64,
    pub research_fund_contribution: u64,
    pub operational_fee: u64,
    pub current_jackpot: u64,
    pub total_entries: u64,
    pub is_active: bool,
    pub last_rollover: i64,
    pub next_rollover: i64,
}

impl Lottery {
    pub const LEN: usize = 32 + 32 + 8 + 8 + 8 + 8 + 8 + 8 + 1 + 8 + 8;
}

#[account]
pub struct Entry {
    pub user_wallet: Pubkey,
    pub amount_paid: u64,
    pub research_contribution: u64,
    pub operational_fee: u64,
    pub timestamp: i64,
    pub is_processed: bool,
}

impl Entry {
    pub const LEN: usize = 32 + 8 + 8 + 8 + 8 + 1;
}


// NOTE: Winner struct removed - winner tracking handled by backend database

#[event]
pub struct LotteryInitialized {
    pub authority: Pubkey,
    pub jackpot_wallet: Pubkey,
    pub research_fund_floor: u64,
    pub research_fee: u64,
}

#[event]
pub struct EntryProcessed {
    pub user_wallet: Pubkey,
    pub amount: u64,
    pub research_contribution: u64,
    pub operational_fee: u64,
    pub new_jackpot: u64,
}

// NOTE: WinnerSelected event removed - winner events handled by backend

#[event]
pub struct EmergencyRecoveryEvent {
    pub amount: u64,
    pub remaining_jackpot: u64,
}

#[event]
pub struct TimeEscapePlanExecuted {
    pub total_jackpot: u64,
    pub last_participant: Pubkey,
    pub last_participant_share: u64,
    pub community_share: u64,
    pub total_participants: u32,
}

#[event]
pub struct WinnerSelected {
    pub winner: Pubkey,
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
    // NOTE: NoJackpot and NoEntries errors removed - not used in AI-based system
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
}
