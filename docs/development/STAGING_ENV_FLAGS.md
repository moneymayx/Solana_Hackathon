# Staging Environment Flags (DO/Vercel)

## Backend (DigitalOcean)
- `USE_CONTRACT_V2=true`
- `USE_CONTRACT_V3=false` (Feature flag - start disabled)
- `LOTTERY_PROGRAM_ID=4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK` (V1)
- `LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm` (V2)
- `LOTTERY_PROGRAM_ID_V3=52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov` (V3 - updated 2024)
- `V2_GLOBAL_PDA=BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb`
- `V2_BOUNTY_1_PDA=2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb`
- `V2_USDC_MINT=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh`
- `SOLANA_RPC_ENDPOINT=https://api.devnet.solana.com`
- `BOUNTY_POOL_WALLET=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF`
- `OPERATIONAL_WALLET=46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D`
- `BUYBACK_WALLET=7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya`
- `STAKING_WALLET=Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX`

## Frontend (Vercel)
- `NEXT_PUBLIC_USE_CONTRACT_V2=false` initially
- `NEXT_PUBLIC_USE_CONTRACT_V3=false` (Feature flag - start disabled)
- `NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V3=52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov` (updated 2024)
- `NEXT_PUBLIC_V3_LOTTERY_PDA=HsZZAW2hPyeewapZEGrNJWgnHKc1mQU34oLuBXJUSV2x` (if needed for direct PDA reference)
- `NEXT_PUBLIC_API_URL=<staging-backend-url>`

## Notes
- Do not enable v2 on prod until staging sign-off
- Keep secrets out of repo; use platform env settings
