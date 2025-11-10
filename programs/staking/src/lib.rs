// Legacy staking contract - deprecated
// Use staking-v2 for new implementations
// This file exists only to satisfy Anchor workspace requirements

use anchor_lang::prelude::*;

declare_id!("5Yx1QzgapjAAFTR4mN4oxy3Qk3imj4nAAaNXQCYTMgCc");

#[program]
pub mod staking {
    use super::*;
    
    pub fn initialize(_ctx: Context<Initialize>) -> Result<()> {
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize {}



