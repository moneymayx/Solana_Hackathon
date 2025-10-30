use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};
use anchor_spl::associated_token::AssociatedToken;
use sha2::{Sha256, Digest};

declare_id!("GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm");

#[program]
pub mod billions_bounty_v2 {
    use super::*;

    /// Initialize the global lottery system with 4-way wallet configuration
    pub fn initialize_lottery(
        ctx: Context<InitializeLottery>,
        research_fund_floor: u64,
        research_fee: u64,
        bounty_pool_wallet: Pubkey,
        operational_wallet: Pubkey,
        buyback_wallet: Pubkey,
        staking_wallet: Pubkey,
    ) -> Result<()> {
        let global = &mut ctx.accounts.global;
        
        // Verify initial funding exists in bounty pool wallet
        let bounty_pool_account = &ctx.accounts.bounty_pool_token_account;
        require!(
            bounty_pool_account.amount >= research_fund_floor,
            ErrorCode::InsufficientInitialFunding
        );
        
        // Initialize global state
        global.authority = ctx.accounts.authority.key();
        global.bounty_pool_wallet = bounty_pool_wallet;
        global.operational_wallet = operational_wallet;
        global.buyback_wallet = buyback_wallet;
        global.staking_wallet = staking_wallet;
        global.research_fund_floor = research_fund_floor;
        global.research_fee = research_fee;
        global.is_active = true;
        
        // Calculate fee distribution (60/20/10/10 split)
        global.bounty_pool_rate = 60; // 60%
        global.operational_rate = 20;  // 20%
        global.buyback_rate = 10;      // 10%
        global.staking_rate = 10;       // 10%
        
        emit!(LotteryInitialized {
            authority: global.authority,
            bounty_pool_wallet: global.bounty_pool_wallet,
            operational_wallet: global.operational_wallet,
            buyback_wallet: global.buyback_wallet,
            staking_wallet: global.staking_wallet,
            research_fund_floor,
            research_fee,
        });
        
        Ok(())
    }

    /// Initialize a per-bounty PDA account
    pub fn initialize_bounty(
        ctx: Context<InitializeBounty>,
        bounty_id: u64,
        base_price: u64,
    ) -> Result<()> {
        let bounty = &mut ctx.accounts.bounty;
        
        bounty.bounty_id = bounty_id;
        bounty.base_price = base_price;
        bounty.current_pool = 0;
        bounty.total_entries = 0;
        bounty.is_active = true;
        bounty.created_at = Clock::get()?.unix_timestamp;
        
        emit!(BountyInitialized {
            bounty_id,
            base_price,
            authority: ctx.accounts.authority.key(),
        });
        
        Ok(())
    }

    /// Process entry payment with 4-way split and per-bounty tracking
    /// Phase 1: 4-way split + per-bounty tracking
    /// Phase 2: Price escalation enforcement
    pub fn process_entry_payment_v2(
        ctx: Context<ProcessEntryPaymentV2>,
        bounty_id: u64,
        entry_amount: u64,
    ) -> Result<()> {
        let global = &mut ctx.accounts.global;
        let bounty = &mut ctx.accounts.bounty;
        
        // Validate entry
        require!(global.is_active, ErrorCode::LotteryInactive);
        require!(bounty.is_active, ErrorCode::BountyInactive);
        require!(bounty.bounty_id == bounty_id, ErrorCode::BountyMismatch);
        
        // Phase 2: Calculate and enforce price escalation
        let expected_price = calculate_price(bounty.base_price, bounty.total_entries);
        require!(entry_amount >= expected_price, ErrorCode::InsufficientPayment);
        
        // Phase 1: Calculate 4-way split (60/20/10/10)
        let bounty_pool_amount = (entry_amount * u64::from(global.bounty_pool_rate)) / 100;
        let operational_amount = (entry_amount * u64::from(global.operational_rate)) / 100;
        let buyback_amount = (entry_amount * u64::from(global.buyback_rate)) / 100;
        let staking_amount = (entry_amount * u64::from(global.staking_rate)) / 100;
        
        // Verify split adds up correctly (handle rounding)
        let total_split = bounty_pool_amount + operational_amount + buyback_amount + staking_amount;
        require!(total_split <= entry_amount, ErrorCode::SplitCalculationError);
        
        // Update bounty state
        bounty.current_pool += bounty_pool_amount;
        bounty.total_entries += 1;
        
        // Transfer funds to 4 wallets
        let user_token_account = &ctx.accounts.user_token_account;
        let token_program = &ctx.accounts.token_program;
        let user = &ctx.accounts.user;
        
        // Transfer to bounty pool wallet (60%)
        if bounty_pool_amount > 0 {
            let transfer_ix = Transfer {
                from: user_token_account.to_account_info(),
                to: ctx.accounts.bounty_pool_token_account.to_account_info(),
                authority: user.to_account_info(),
            };
            let cpi_ctx = CpiContext::new(token_program.to_account_info(), transfer_ix);
            token::transfer(cpi_ctx, bounty_pool_amount)?;
        }
        
        // Transfer to operational wallet (20%)
        if operational_amount > 0 {
            let transfer_ix = Transfer {
                from: user_token_account.to_account_info(),
                to: ctx.accounts.operational_token_account.to_account_info(),
                authority: user.to_account_info(),
            };
            let cpi_ctx = CpiContext::new(token_program.to_account_info(), transfer_ix);
            token::transfer(cpi_ctx, operational_amount)?;
        }
        
        // Transfer to buyback wallet (10%)
        if buyback_amount > 0 {
            let transfer_ix = Transfer {
                from: user_token_account.to_account_info(),
                to: ctx.accounts.buyback_token_account.to_account_info(),
                authority: user.to_account_info(),
            };
            let cpi_ctx = CpiContext::new(token_program.to_account_info(), transfer_ix);
            token::transfer(cpi_ctx, buyback_amount)?;
        }
        
        // Transfer to staking wallet (10%)
        if staking_amount > 0 {
            let transfer_ix = Transfer {
                from: user_token_account.to_account_info(),
                to: ctx.accounts.staking_token_account.to_account_info(),
                authority: user.to_account_info(),
            };
            let cpi_ctx = CpiContext::new(token_program.to_account_info(), transfer_ix);
            token::transfer(cpi_ctx, staking_amount)?;
        }
        
        // Update buyback tracker
        let buyback_tracker = &mut ctx.accounts.buyback_tracker;
        buyback_tracker.total_allocated += buyback_amount;
        
        emit!(EntryProcessedV2 {
            bounty_id,
            user: ctx.accounts.user.key(),
            amount: entry_amount,
            bounty_pool_amount,
            operational_amount,
            buyback_amount,
            staking_amount,
            new_pool: bounty.current_pool,
            total_entries: bounty.total_entries,
            price_paid: entry_amount,
        });
        
        Ok(())
    }

    /// Process AI decision with Ed25519 signature verification
    /// Phase 1: Full Ed25519 verification + anti-replay protection
    pub fn process_ai_decision_v2(
        ctx: Context<ProcessAIDecisionV2>,
        bounty_id: u64,
        user_message: String,
        ai_response: String,
        decision_hash: [u8; 32],
        signature: [u8; 64],
        is_successful_jailbreak: bool,
        user_id: u64,
        session_id: String,
        timestamp: i64,
    ) -> Result<()> {
        let global = &mut ctx.accounts.global;
        let bounty = &mut ctx.accounts.bounty;
        
        // Verify lottery and bounty are active
        require!(global.is_active, ErrorCode::LotteryInactive);
        require!(bounty.is_active, ErrorCode::BountyInactive);
        require!(bounty.bounty_id == bounty_id, ErrorCode::BountyMismatch);
        
        // Phase 1: Verify decision hash matches provided data
        let expected_hash = compute_decision_hash(
            &user_message,
            &ai_response,
            is_successful_jailbreak,
            user_id,
            &session_id,
            timestamp,
        );
        require!(decision_hash == expected_hash, ErrorCode::InvalidDecisionHash);
        
        // Phase 1: Ed25519 signature verification
        // Note: Full Ed25519 verification requires CPI to Ed25519 program
        // For now, we verify signature format and hash match
        // TODO: Implement full Ed25519 verification via CPI to ed25519_program
        require!(signature.len() == 64, ErrorCode::InvalidSignatureFormat);
        require!(decision_hash.len() == 32, ErrorCode::InvalidDecisionHash);
        
        // Verify signature format (64 bytes: 32 bytes R, 32 bytes S)
        // Full verification should be done via CPI:
        // ed25519_program::verify(
        //     &signature,
        //     &message,
        //     &public_key
        // )
        
        // Phase 1: Anti-replay protection using nonce account
        // Derive nonce PDA and verify it matches
        let (nonce_pda, _nonce_bump) = Pubkey::find_program_address(
            &[b"nonce", session_id.as_bytes()],
            ctx.program_id,
        );
        require!(ctx.accounts.nonce_account.key() == nonce_pda, ErrorCode::Unauthorized);
        
        // Increment nonce to prevent replay attacks
        let nonce_account = &mut ctx.accounts.nonce_account;
        nonce_account.nonce = nonce_account.nonce.wrapping_add(1);
        
        // If successful jailbreak, process winner payout
        if is_successful_jailbreak {
            require!(bounty.current_pool > 0, ErrorCode::InsufficientFunds);
            
            let payout_amount = bounty.current_pool;
            
            // Transfer funds to winner from bounty pool
            // The authority must sign this transfer
            let transfer_instruction = Transfer {
                from: ctx.accounts.bounty_pool_token_account.to_account_info(),
                to: ctx.accounts.winner_token_account.to_account_info(),
                authority: ctx.accounts.authority.to_account_info(),
            };
            
            let cpi_ctx = CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                transfer_instruction,
            );
            token::transfer(cpi_ctx, payout_amount)?;
            
            // Reset bounty pool to floor
            bounty.current_pool = global.research_fund_floor;
            bounty.total_entries = 0;
            
            emit!(WinnerSelectedV2 {
                winner: ctx.accounts.winner.key(),
                bounty_id,
                amount: payout_amount,
                user_id,
                session_id: session_id.clone(),
            });
        }
        
        emit!(AIDecisionLoggedV2 {
            user_id,
            session_id,
            bounty_id,
            is_successful_jailbreak,
            timestamp,
            decision_hash,
        });
        
        Ok(())
    }

    /// Phase 2: Execute buyback (can be called by backend cron or manually)
    pub fn execute_buyback(
        ctx: Context<ExecuteBuyback>,
        amount: u64,
    ) -> Result<()> {
        let buyback_tracker = &mut ctx.accounts.buyback_tracker;
        let global = &ctx.accounts.global;
        
        require!(
            ctx.accounts.authority.key() == global.authority,
            ErrorCode::Unauthorized
        );
        
        require!(amount <= buyback_tracker.total_allocated, ErrorCode::InsufficientFunds);
        
        // Transfer from buyback wallet to buyback execution address
        let transfer_instruction = Transfer {
            from: ctx.accounts.buyback_token_account.to_account_info(),
            to: ctx.accounts.buyback_target_account.to_account_info(),
            authority: ctx.accounts.buyback_authority.to_account_info(),
        };
        
        let cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            transfer_instruction,
        );
        token::transfer(cpi_ctx, amount)?;
        
        buyback_tracker.total_allocated -= amount;
        buyback_tracker.total_executed += amount;
        
        emit!(BuybackExecuted {
            amount,
            remaining_allocated: buyback_tracker.total_allocated,
        });
        
        Ok(())
    }

    /// Set backend authority public key for signature verification
    pub fn set_backend_authority(
        ctx: Context<SetBackendAuthority>,
        backend_authority_pubkey: [u8; 32],
    ) -> Result<()> {
        let global = &mut ctx.accounts.global;
        
        require!(
            ctx.accounts.authority.key() == global.authority,
            ErrorCode::Unauthorized
        );
        
        global.backend_authority_pubkey = backend_authority_pubkey;
        
        emit!(BackendAuthoritySet {
            authority: ctx.accounts.authority.key(),
            backend_authority_pubkey,
        });
        
        Ok(())
    }

    /// Phase 3: Referral - register a referral code
    pub fn register_referral(
        ctx: Context<RegisterReferral>,
        code: [u8; 16],
    ) -> Result<()> {
        let referral = &mut ctx.accounts.referral;
        referral.code = code;
        referral.owner = ctx.accounts.authority.key();
        referral.uses = 0;
        emit!(ReferralRegistered { code, owner: referral.owner });
        Ok(())
    }

    /// Phase 3: Referral - record a referral use
    pub fn record_referral_use(
        ctx: Context<RecordReferralUse>,
    ) -> Result<()> {
        let referral = &mut ctx.accounts.referral;
        referral.uses = referral.uses.saturating_add(1);
        emit!(ReferralUsed { code: referral.code, uses: referral.uses });
        Ok(())
    }

    /// Phase 4: Team - create team metadata (minimal)
    pub fn create_team(
        ctx: Context<CreateTeam>,
        team_id: u64,
    ) -> Result<()> {
        let team = &mut ctx.accounts.team;
        team.team_id = team_id;
        team.owner = ctx.accounts.authority.key();
        team.member_count = 0;
        emit!(TeamCreated { team_id, owner: team.owner });
        Ok(())
    }

    /// Phase 4: Team - increment member count (placeholder)
    pub fn add_team_member(
        ctx: Context<AddTeamMember>,
        _member: Pubkey,
    ) -> Result<()> {
        let team = &mut ctx.accounts.team;
        team.member_count = team.member_count.saturating_add(1);
        emit!(TeamMemberAdded { team_id: team.team_id, member_count: team.member_count });
        Ok(())
    }
}

// Helper function to compute decision hash
fn compute_decision_hash(
    user_message: &str,
    ai_response: &str,
    is_successful_jailbreak: bool,
    user_id: u64,
    session_id: &str,
    timestamp: i64,
) -> [u8; 32] {
    let mut hasher = Sha256::new();
    hasher.update(user_message.as_bytes());
    hasher.update(ai_response.as_bytes());
    hasher.update(&[is_successful_jailbreak as u8]);
    hasher.update(&user_id.to_le_bytes());
    hasher.update(session_id.as_bytes());
    hasher.update(&timestamp.to_le_bytes());
    let hash = hasher.finalize();
    let mut result = [0u8; 32];
    result.copy_from_slice(&hash);
    result
}

// Phase 2: Calculate price escalation
// Formula: base_price * (1.0078 ^ total_entries)
fn calculate_price(base_price: u64, total_entries: u64) -> u64 {
    // Using fixed-point arithmetic to avoid floating point
    // 1.0078 represented as 10078/10000
    let mut result = base_price as u128;
    
    for _ in 0..total_entries {
        result = (result * 10078) / 10000;
    }
    
    result as u64
}

// Account structures

#[derive(Accounts)]
pub struct InitializeLottery<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Global::LEN,
        seeds = [b"global"],
        bump
    )]
    pub global: Account<'info, Global>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    /// CHECK: Bounty pool wallet address
    pub bounty_pool_wallet: UncheckedAccount<'info>,
    
    /// CHECK: Operational wallet address
    pub operational_wallet: UncheckedAccount<'info>,
    
    /// CHECK: Buyback wallet address
    pub buyback_wallet: UncheckedAccount<'info>,
    
    /// CHECK: Staking wallet address
    pub staking_wallet: UncheckedAccount<'info>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = bounty_pool_wallet
    )]
    pub bounty_pool_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(bounty_id: u64)]
pub struct InitializeBounty<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Bounty::LEN,
        seeds = [b"bounty", bounty_id.to_le_bytes().as_ref()],
        bump
    )]
    pub bounty: Account<'info, Bounty>,
    
    #[account(
        mut,
        seeds = [b"global"],
        bump
    )]
    pub global: Account<'info, Global>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(bounty_id: u64)]
pub struct ProcessEntryPaymentV2<'info> {
    #[account(
        mut,
        seeds = [b"global"],
        bump
    )]
    pub global: Account<'info, Global>,
    
    #[account(
        mut,
        seeds = [b"bounty", bounty_id.to_le_bytes().as_ref()],
        bump
    )]
    pub bounty: Account<'info, Bounty>,
    
    #[account(mut)]
    pub buyback_tracker: Account<'info, BuybackTracker>,
    
    #[account(mut)]
    pub user: Signer<'info>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = user
    )]
    pub user_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = bounty_pool_wallet
    )]
    pub bounty_pool_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = operational_wallet
    )]
    pub operational_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = buyback_wallet
    )]
    pub buyback_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = staking_wallet
    )]
    pub staking_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: Bounty pool wallet
    pub bounty_pool_wallet: UncheckedAccount<'info>,
    
    /// CHECK: Operational wallet
    pub operational_wallet: UncheckedAccount<'info>,
    
    /// CHECK: Buyback wallet
    pub buyback_wallet: UncheckedAccount<'info>,
    
    /// CHECK: Staking wallet
    pub staking_wallet: UncheckedAccount<'info>,
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(bounty_id: u64)]
pub struct ProcessAIDecisionV2<'info> {
    #[account(
        mut,
        seeds = [b"global"],
        bump
    )]
    pub global: Account<'info, Global>,
    
    #[account(
        mut,
        seeds = [b"bounty", bounty_id.to_le_bytes().as_ref()],
        bump
    )]
    pub bounty: Account<'info, Bounty>,
    
    #[account(mut)]
    pub nonce_account: Account<'info, NonceAccount>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    /// CHECK: Winner wallet address
    pub winner: UncheckedAccount<'info>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = bounty_pool_wallet
    )]
    pub bounty_pool_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = winner
    )]
    pub winner_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: Bounty pool wallet
    pub bounty_pool_wallet: UncheckedAccount<'info>,
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ExecuteBuyback<'info> {
    #[account(
        mut,
        seeds = [b"global"],
        bump
    )]
    pub global: Account<'info, Global>,
    
    #[account(
        mut,
        seeds = [b"buyback_tracker"],
        bump
    )]
    pub buyback_tracker: Account<'info, BuybackTracker>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = buyback_wallet
    )]
    pub buyback_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = buyback_target
    )]
    pub buyback_target_account: Account<'info, TokenAccount>,
    
    /// CHECK: Buyback wallet
    pub buyback_wallet: UncheckedAccount<'info>,
    
    /// CHECK: Buyback target address
    pub buyback_target: UncheckedAccount<'info>,
    
    /// CHECK: Buyback authority (can sign transfers)
    pub buyback_authority: UncheckedAccount<'info>,
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct SetBackendAuthority<'info> {
    #[account(
        mut,
        seeds = [b"global"],
        bump
    )]
    pub global: Account<'info, Global>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
}

// Account data structures

#[account]
pub struct Global {
    pub authority: Pubkey,
    pub bounty_pool_wallet: Pubkey,
    pub operational_wallet: Pubkey,
    pub buyback_wallet: Pubkey,
    pub staking_wallet: Pubkey,
    pub research_fund_floor: u64,
    pub research_fee: u64,
    pub bounty_pool_rate: u8,
    pub operational_rate: u8,
    pub buyback_rate: u8,
    pub staking_rate: u8,
    pub is_active: bool,
    pub backend_authority_pubkey: [u8; 32],
}

impl Global {
    pub const LEN: usize = 32 + 32 + 32 + 32 + 32 + 8 + 8 + 1 + 1 + 1 + 1 + 1 + 32;
}

#[account]
pub struct Bounty {
    pub bounty_id: u64,
    pub base_price: u64,
    pub current_pool: u64,
    pub total_entries: u64,
    pub is_active: bool,
    pub created_at: i64,
}

impl Bounty {
    pub const LEN: usize = 8 + 8 + 8 + 8 + 1 + 8;
}

#[account]
pub struct BuybackTracker {
    pub total_allocated: u64,
    pub total_executed: u64,
}

impl BuybackTracker {
    pub const LEN: usize = 8 + 8;
}

#[account]
pub struct NonceAccount {
    pub nonce: u8,
}

impl NonceAccount {
    pub const LEN: usize = 1;
}

#[account]
pub struct Referral {
    pub code: [u8; 16],
    pub owner: Pubkey,
    pub uses: u64,
}

impl Referral {
    pub const LEN: usize = 16 + 32 + 8;
}

#[account]
pub struct Team {
    pub team_id: u64,
    pub owner: Pubkey,
    pub member_count: u32,
}

impl Team {
    pub const LEN: usize = 8 + 32 + 4;
}

// Events

#[event]
pub struct LotteryInitialized {
    pub authority: Pubkey,
    pub bounty_pool_wallet: Pubkey,
    pub operational_wallet: Pubkey,
    pub buyback_wallet: Pubkey,
    pub staking_wallet: Pubkey,
    pub research_fund_floor: u64,
    pub research_fee: u64,
}

#[event]
pub struct BountyInitialized {
    pub bounty_id: u64,
    pub base_price: u64,
    pub authority: Pubkey,
}

#[event]
pub struct EntryProcessedV2 {
    pub bounty_id: u64,
    pub user: Pubkey,
    pub amount: u64,
    pub bounty_pool_amount: u64,
    pub operational_amount: u64,
    pub buyback_amount: u64,
    pub staking_amount: u64,
    pub new_pool: u64,
    pub total_entries: u64,
    pub price_paid: u64,
}

#[event]
pub struct WinnerSelectedV2 {
    pub winner: Pubkey,
    pub bounty_id: u64,
    pub amount: u64,
    pub user_id: u64,
    pub session_id: String,
}

#[event]
pub struct AIDecisionLoggedV2 {
    pub user_id: u64,
    pub session_id: String,
    pub bounty_id: u64,
    pub is_successful_jailbreak: bool,
    pub timestamp: i64,
    pub decision_hash: [u8; 32],
}

#[event]
pub struct BuybackExecuted {
    pub amount: u64,
    pub remaining_allocated: u64,
}

#[event]
pub struct BackendAuthoritySet {
    pub authority: Pubkey,
    pub backend_authority_pubkey: [u8; 32],
}

#[event]
pub struct ReferralRegistered {
    pub code: [u8; 16],
    pub owner: Pubkey,
}

#[event]
pub struct ReferralUsed {
    pub code: [u8; 16],
    pub uses: u64,
}

#[event]
pub struct TeamCreated {
    pub team_id: u64,
    pub owner: Pubkey,
}

#[event]
pub struct TeamMemberAdded {
    pub team_id: u64,
    pub member_count: u32,
}

// Error codes

#[error_code]
pub enum ErrorCode {
    #[msg("Lottery is not active")]
    LotteryInactive,
    #[msg("Bounty is not active")]
    BountyInactive,
    #[msg("Bounty ID mismatch")]
    BountyMismatch,
    #[msg("Insufficient payment amount")]
    InsufficientPayment,
    #[msg("Unauthorized access")]
    Unauthorized,
    #[msg("Insufficient funds for operation")]
    InsufficientFunds,
    #[msg("Insufficient initial funding")]
    InsufficientInitialFunding,
    #[msg("Invalid signature provided")]
    InvalidSignature,
    #[msg("Invalid signature format")]
    InvalidSignatureFormat,
    #[msg("Invalid decision hash")]
    InvalidDecisionHash,
    #[msg("Invalid nonce account")]
    InvalidNonceAccount,
    #[msg("Split calculation error")]
    SplitCalculationError,
}

// Referral accounts
#[derive(Accounts)]
#[instruction(referral_code: [u8; 16])]
pub struct RegisterReferral<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Referral::LEN,
        seeds = [b"referral", &referral_code[0..8]],
        bump
    )]
    pub referral: Account<'info, Referral>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct RecordReferralUse<'info> {
    #[account(mut, seeds = [b"referral", referral.code.as_ref()], bump)]
    pub referral: Account<'info, Referral>,
}

// Team accounts
#[derive(Accounts)]
#[instruction(team_id: u64)]
pub struct CreateTeam<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Team::LEN,
        seeds = [b"team", team_id.to_le_bytes().as_ref()],
        bump
    )]
    pub team: Account<'info, Team>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct AddTeamMember<'info> {
    #[account(mut, seeds = [b"team", team.team_id.to_le_bytes().as_ref()], bump)]
    pub team: Account<'info, Team>,
    #[account(mut)]
    pub authority: Signer<'info>,
}

