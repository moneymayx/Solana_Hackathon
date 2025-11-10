"""
SDK Test API Routers - Parallel Development

These routers provide isolated test endpoints for SDK integrations.
All endpoints are prefixed with /api/sdk-test/ to avoid conflicts with
production endpoints.

These routers are only included when SDK testing is enabled via environment
variables and should NOT be included in production until validated.
"""

__all__ = [
    "kora_router",
    "attestations_router",
    "solana_pay_router",
    "include_sdk_test_routers",
]

