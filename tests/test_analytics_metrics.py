"""Analytics dashboard contract health tests."""

from typing import Dict, Any

import pytest

from apps.backend.main import determine_smart_contract_health


def test_determine_smart_contract_health_defaults_to_active(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the dashboard falls back to reporting active contracts when polling fails."""
    monkeypatch.delenv("SMART_CONTRACT_STATUS_OVERRIDE", raising=False)
    stub_status: Dict[str, Any] = {"success": False}
    stub_balance: Dict[str, Any] = {"success": False}
    assert determine_smart_contract_health(stub_status, stub_balance) is True


def test_determine_smart_contract_health_respects_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure operators can force the dashboard to show contracts offline when required."""
    monkeypatch.setenv("SMART_CONTRACT_STATUS_OVERRIDE", "false")
    stub_status: Dict[str, Any] = {"success": False}
    stub_balance: Dict[str, Any] = {"success": False}
    assert determine_smart_contract_health(stub_status, stub_balance) is False


def test_determine_smart_contract_health_true_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """If both smart contract queries succeed, the dashboard must report an active connection."""
    monkeypatch.setenv("SMART_CONTRACT_STATUS_OVERRIDE", "false")
    stub_status: Dict[str, Any] = {"success": True}
    stub_balance: Dict[str, Any] = {"success": True}
    assert determine_smart_contract_health(stub_status, stub_balance) is True

