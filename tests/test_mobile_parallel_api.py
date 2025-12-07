import asyncio
import importlib
import os
from datetime import datetime
from typing import Dict
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Enable the parallel router before importing the FastAPI app
os.environ["ENABLE_MOBILE_PARALLEL_API"] = "true"

main = importlib.import_module("main")
main = importlib.reload(main)

from main import app  # noqa: E402  # pylint: disable=wrong-import-position
from src.database import get_db  # noqa: E402
from src.models import Conversation  # noqa: E402
from tests.test_database_setup import (  # noqa: E402
    TestSessionLocal,
    get_test_db,
    setup_test_database,
)

app.dependency_overrides[get_db] = get_test_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_database() -> Dict[str, str]:
    asyncio.run(setup_test_database())
    return {}


class TestMobileParallelAPI:
    """Tests for the complementary mobile endpoints."""

    def test_mobile_winning_prompts_endpoint(self) -> None:
        async def _seed_winner() -> None:
            async with TestSessionLocal() as session:
                conversation = Conversation(
                    user_id=1,
                    bounty_id=4,
                    message_type="user",
                    content="This is the triumphant prompt",
                    timestamp=datetime.utcnow(),
                    is_winner=True,
                )
                session.add(conversation)
                await session.commit()

        asyncio.run(_seed_winner())

        response = client.get("/api/mobile/bounty/4/winning-prompts")
        assert response.status_code == 200

        payload = response.json()
        assert payload["success"] is True
        assert payload["bounty_id"] == 4
        assert payload["total"] == 1
        assert payload["prompts"][0]["prompt"] == "This is the triumphant prompt"

    @patch("apps.backend.api.mobile_parallel_router.winner_tracking_service")
    def test_mobile_wallet_connect_without_signature(self, mock_winner_service: AsyncMock) -> None:
        async_mock = AsyncMock(return_value={"blacklisted": False})
        mock_winner_service.is_wallet_blacklisted = async_mock

        response = client.post(
            "/api/mobile/wallet/connect",
            json={
                "wallet_address": "4YQy7Jf8yAbCdEfGhijkLmnoPQRsTuVwxYZ1234567890",
                "display_name": "Mobile Tester",
                "public_key": "MobilePublicKey123",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert payload["display_name"] == "Mobile Tester"
        assert payload["public_key"] == "MobilePublicKey123"
        assert payload["details"]["note"] == "Signature skipped under mobile parallel flow"

        # Ensure the blacklist check executed with the provided wallet
        async_mock.assert_awaited()




