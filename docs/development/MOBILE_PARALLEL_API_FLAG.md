# Mobile Parallel API Flag

This note captures the feature-flagged mobile router that runs alongside the legacy FastAPI endpoints.

## Feature Flag

- Environment variable: `ENABLE_MOBILE_PARALLEL_API`
- Accepted truthy values: `true`, `1`, `yes`, `on`
- When enabled, `apps/backend/main.py` dynamically registers `apps/backend/api/mobile_parallel_router.py` without modifying the existing v1 routes.

## Exposed Endpoints (Flagged)

- `GET /api/mobile/bounty/{bounty_id}/winning-prompts`
- `GET /api/bounty/{bounty_id}/winning-prompts` *(mobile-parallel tag)*
- `POST /api/mobile/wallet/connect`

These handlers:

1. Surface recent winning prompts using the same `Conversation` records as the core lottery flow so mobile clients can verify jackpot transparency.
2. Provide a signature-optional wallet connect path that still records the wallet against the user record while bypassing the primary `/api/wallet/connect` handler.

## Testing

- Unit tests live in `tests/test_mobile_parallel_api.py` and expect the flag to be enabled.
- Run `ENABLE_MOBILE_PARALLEL_API=true pytest tests/test_mobile_parallel_api.py` to validate the parallel endpoints without touching the primary suite.

## Rollout Notes

- The router respects the existing winner blacklist logic. If the blacklist service is unavailable, the endpoints continue to function while logging a warning.
- Public-key logging is retained so winner-tracking analytics can trace mobile connections during the trial phase.



