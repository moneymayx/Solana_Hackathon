# Billions Bounty - V2 Devnet Deployment Summary

- Program (devnet): `GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm`
- Global PDA: `F4YATUC3tEA3Gb3Tt3v7sZBT9iKRhHXJsZ6s7nBWKDgh`
- Bounty[1] PDA: `AJC6D2mvMcktdzpJJQmbYXkTZn9xGpd2C3qm4VAZK83Z`
- Bounty Pool ATA (devnet test mint): `3QGq4L81FuhCNMHq2Mq7ZwahXzsyDQvKptZZL1UVsaXE`
- Devnet SPL mint used: `Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr`

Wallets configured
- Bounty Pool: `CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF`
- Operational: `46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D`
- Buyback: `7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya`
- Staking: `Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX`

Transactions
- initialize_lottery: `5fSFtumQVVrYJFyEAmUPWQDqYhfm1w1sTgkW174rWnkoW7KCQWkaxwSQCuCvAKMdJZzAAvf681V9mRugFoCrkhrh`
- initialize_bounty (id=1): `vBjCWGdAsWjnQLyS4cRdRPZPr3XkLqFvL32UjZMm3AEZZW3uBajButS7UynKJdUdLMQwF7N7uqeuMWeWH2tVHcp`

IDL
- IDL Account: `HicBwRnacuFcfYXWGBFSCWofc8ZmJU4v4rKKxtxvXBQr`
- Size: 1308 bytes
- Status: ✅ Published and verified on devnet
- Fetch: `anchor idl fetch --provider.cluster devnet GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm`

Notes
- Research fund floor set to 0 for devnet init only.
- Source `declare_id!` and program configs updated to match deployed program.
- Contract is fully verifiable on Solana explorers (Solscan, Solana Explorer, etc.)
