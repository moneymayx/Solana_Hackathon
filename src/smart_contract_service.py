"""
Shim module for backward compatibility.

Older tests and documentation import `smart_contract_service` from the top-level
`src.smart_contract_service` module. The actual implementation now lives in
`src/services/smart_contract_service.py`, so this file simply re-exports the
service and class from there.
"""

from .services.smart_contract_service import smart_contract_service, SmartContractService

__all__ = ["smart_contract_service", "SmartContractService"]


