use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

declare_id!("STAK1NGv211111111111111111111111111111111111");

#[program]
pub mod staking_v2 {
    use super::*;

    /// Initialize staking pool
    pub fn initialize_staking(
        ctx: Context<InitializeStaking>,
        reward_rate: u64, // Reward rate per epoch
    ) -> Result<()> {
        let staking_pool = &mut ctx.accounts.staking_pool;
        
        staking_pool.authority = ctx.accounts.authority.key();
        staking_pool.reward_rate = reward_rate;
        staking_pool.total_staked = 0;
        staking_pool.total_rewards_distributed = 0;
        staking_pool.is_active = true;
        
        emit!(StakingInitialized {
            authority: staking_pool.authority,
            reward_rate,
        });
        
        Ok(())
    }

    /// Stake tokens (skeleton - full implementation to be added)
    pub fn stake(ctx: Context<Stake>, amount: u64) -> Result<()> {
        let staking_pool = &mut ctx.accounts.staking_pool;
        let position = &mut ctx.accounts.position;
        
        require!(staking_pool.is_active, ErrorCode::StakingInactive);
        require!(amount > 0, ErrorCode::InvalidAmount);
        
        // Transfer tokens to staking pool
        let transfer_ix = Transfer {
            from: ctx.accounts.user_token_account.to_account_info(),
            to: ctx.accounts.staking_token_account.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };
        
        let cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            transfer_ix,
        );
        token::transfer(cpi_ctx, amount)?;
        
        // Update position
        if position.amount == 0 {
            position.user = ctx.accounts.user.key();
            position.staked_at = Clock::get()?.unix_timestamp;
        }
        position.amount += amount;
        staking_pool.total_staked += amount;
        
        emit!(Staked {
            user: ctx.accounts.user.key(),
            amount,
            total_staked: staking_pool.total_staked,
        });
        
        Ok(())
    }

    /// Unstake tokens (skeleton - full implementation to be added)
    pub fn unstake(ctx: Context<Unstake>, amount: u64) -> Result<()> {
        let staking_pool = &mut ctx.accounts.staking_pool;
        let position = &mut ctx.accounts.position;
        
        require!(staking_pool.is_active, ErrorCode::StakingInactive);
        require!(position.amount >= amount, ErrorCode::InsufficientStake);
        require!(position.user == ctx.accounts.user.key(), ErrorCode::Unauthorized);
        
        // Transfer tokens back to user
        let transfer_ix = Transfer {
            from: ctx.accounts.staking_token_account.to_account_info(),
            to: ctx.accounts.user_token_account.to_account_info(),
            authority: ctx.accounts.authority.to_account_info(),
        };
        
        let cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            transfer_ix,
        );
        token::transfer(cpi_ctx, amount)?;
        
        position.amount -= amount;
        staking_pool.total_staked -= amount;
        
        emit!(Unstaked {
            user: ctx.accounts.user.key(),
            amount,
            total_staked: staking_pool.total_staked,
        });
        
        Ok(())
    }

    /// Distribute rewards (skeleton - to be called by backend cron)
    pub fn distribute_rewards(ctx: Context<DistributeRewards>, amount: u64) -> Result<()> {
        let staking_pool = &mut ctx.accounts.staking_pool;
        
        require!(
            ctx.accounts.authority.key() == staking_pool.authority,
            ErrorCode::Unauthorized
        );
        
        // Transfer rewards from staking wallet to pool
        let transfer_ix = Transfer {
            from: ctx.accounts.staking_wallet_account.to_account_info(),
            to: ctx.accounts.staking_token_account.to_account_info(),
            authority: ctx.accounts.staking_wallet_authority.to_account_info(),
        };
        
        let cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            transfer_ix,
        );
        token::transfer(cpi_ctx, amount)?;
        
        staking_pool.total_rewards_distributed += amount;
        
        emit!(RewardsDistributed {
            amount,
            total_distributed: staking_pool.total_rewards_distributed,
        });
        
        Ok(())
    }
}

#[derive(Accounts)]
pub struct InitializeStaking<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + StakingPool::LEN,
        seeds = [b"staking_pool"],
        bump
    )]
    pub staking_pool: Account<'info, StakingPool>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Stake<'info> {
    #[account(
        mut,
        seeds = [b"staking_pool"],
        bump
    )]
    pub staking_pool: Account<'info, StakingPool>,
    
    #[account(
        init_if_needed,
        payer = user,
        space = 8 + StakingPosition::LEN,
        seeds = [b"position", user.key().as_ref()],
        bump
    )]
    pub position: Account<'info, StakingPosition>,
    
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
        associated_token::authority = staking_pool
    )]
    pub staking_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: USDC mint
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Unstake<'info> {
    #[account(
        mut,
        seeds = [b"staking_pool"],
        bump
    )]
    pub staking_pool: Account<'info, StakingPool>,
    
    #[account(
        mut,
        seeds = [b"position", user.key().as_ref()],
        bump
    )]
    pub position: Account<'info, StakingPosition>,
    
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
        associated_token::authority = staking_pool
    )]
    pub staking_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: USDC mint
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct DistributeRewards<'info> {
    #[account(
        mut,
        seeds = [b"staking_pool"],
        bump
    )]
    pub staking_pool: Account<'info, StakingPool>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = staking_wallet_authority
    )]
    pub staking_wallet_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = usdc_mint,
        associated_token::authority = staking_pool
    )]
    pub staking_token_account: Account<'info, TokenAccount>,
    
    /// CHECK: Staking wallet authority
    pub staking_wallet_authority: UncheckedAccount<'info>,
    
    /// CHECK: USDC mint
    pub usdc_mint: UncheckedAccount<'info>,
    
    pub token_program: Program<'info, Token>,
}

#[account]
pub struct StakingPool {
    pub authority: Pubkey,
    pub reward_rate: u64,
    pub total_staked: u64,
    pub total_rewards_distributed: u64,
    pub is_active: bool,
}

impl StakingPool {
    pub const LEN: usize = 32 + 8 + 8 + 8 + 1;
}

#[account]
pub struct StakingPosition {
    pub user: Pubkey,
    pub amount: u64,
    pub staked_at: i64,
}

impl StakingPosition {
    pub const LEN: usize = 32 + 8 + 8;
}

#[event]
pub struct StakingInitialized {
    pub authority: Pubkey,
    pub reward_rate: u64,
}

#[event]
pub struct Staked {
    pub user: Pubkey,
    pub amount: u64,
    pub total_staked: u64,
}

#[event]
pub struct Unstaked {
    pub user: Pubkey,
    pub amount: u64,
    pub total_staked: u64,
}

#[event]
pub struct RewardsDistributed {
    pub amount: u64,
    pub total_distributed: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Staking is not active")]
    StakingInactive,
    #[msg("Invalid amount")]
    InvalidAmount,
    #[msg("Insufficient stake")]
    InsufficientStake,
    #[msg("Unauthorized")]
    Unauthorized,
}



