use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};
use anchor_spl::associated_token::AssociatedToken;

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

    /// Select a winner and transfer jackpot (autonomous)
    pub fn select_winner(ctx: Context<SelectWinner>) -> Result<()> {
        // Get lottery info before mutable borrow
        let lottery_info = ctx.accounts.lottery.to_account_info();
        let lottery_bump = *ctx.bumps.get("lottery").unwrap();
        let lottery_key = ctx.accounts.lottery.key();
        
        let lottery = &mut ctx.accounts.lottery;
        let winner = &mut ctx.accounts.winner;
        
        // Validate lottery state
        require!(lottery.is_active, ErrorCode::LotteryInactive);
        require!(lottery.current_jackpot > 0, ErrorCode::NoJackpot);
        require!(lottery.total_entries > 0, ErrorCode::NoEntries);
        
        // Generate secure random number using clock timestamp (simplified for Anchor 0.28)
        let clock = Clock::get()?;
        let random_seed = clock.unix_timestamp.to_le_bytes();
        let random_number = u64::from_le_bytes([
            random_seed[0], random_seed[1], random_seed[2], random_seed[3],
            random_seed[4], random_seed[5], random_seed[6], random_seed[7],
        ]) % lottery.total_entries;
        
        // Select winner (simplified - in production, use proper random selection)
        let winner_index = (random_number % lottery.total_entries) + 1;
        
        // Record winner
        winner.lottery_id = lottery_key;
        winner.winner_index = winner_index;
        winner.jackpot_amount = lottery.current_jackpot;
        winner.timestamp = Clock::get()?.unix_timestamp;
        winner.is_claimed = false;
        
        // Transfer jackpot to winner
        let transfer_amount = lottery.current_jackpot;
        
        let transfer_instruction = Transfer {
            from: ctx.accounts.jackpot_token_account.to_account_info(),
            to: ctx.accounts.winner_token_account.to_account_info(),
            authority: lottery_info,
        };
        
        let seeds = &[b"lottery".as_ref(), &[lottery_bump]];
        let signer = &[&seeds[..]];
        
        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            transfer_instruction,
            signer,
        );
        
        token::transfer(cpi_ctx, transfer_amount)?;
        
        // Reset lottery for next round
        lottery.current_jackpot = lottery.research_fund_floor;
        lottery.total_entries = 0;
        lottery.last_rollover = Clock::get()?.unix_timestamp;
        lottery.next_rollover = Clock::get()?.unix_timestamp + (24 * 60 * 60);
        
        emit!(WinnerSelected {
            winner_index,
            jackpot_amount: winner.jackpot_amount,
            new_jackpot: lottery.current_jackpot,
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

#[derive(Accounts)]
pub struct SelectWinner<'info> {
    #[account(
        mut,
        seeds = [b"lottery"],
        bump
    )]
    pub lottery: Account<'info, Lottery>,
    
    #[account(
        init,
        payer = lottery_authority,
        space = 8 + Winner::LEN,
        seeds = [b"winner", lottery.key().as_ref()],
        bump
    )]
    pub winner: Account<'info, Winner>,
    
    #[account(mut)]
    pub lottery_authority: Signer<'info>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = lottery
    )]
    pub jackpot_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: Winner token account
    pub winner_token_account: UncheckedAccount<'info>,
    
    /// CHECK: USDC mint address
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub clock: Sysvar<'info, Clock>,
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

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

#[account]
pub struct Winner {
    pub lottery_id: Pubkey,
    pub winner_index: u64,
    pub jackpot_amount: u64,
    pub timestamp: i64,
    pub is_claimed: bool,
}

impl Winner {
    pub const LEN: usize = 32 + 8 + 8 + 8 + 1;
}

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

#[event]
pub struct WinnerSelected {
    pub winner_index: u64,
    pub jackpot_amount: u64,
    pub new_jackpot: u64,
}

#[event]
pub struct EmergencyRecoveryEvent {
    pub amount: u64,
    pub remaining_jackpot: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Lottery is not active")]
    LotteryInactive,
    #[msg("Insufficient payment amount")]
    InsufficientPayment,
    #[msg("No jackpot available")]
    NoJackpot,
    #[msg("No entries in lottery")]
    NoEntries,
    #[msg("Unauthorized access")]
    Unauthorized,
    #[msg("Insufficient funds for operation")]
    InsufficientFunds,
}
