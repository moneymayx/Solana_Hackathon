"""
Encryption Service - AES-256 encryption for sensitive data at rest
"""
import os
import base64
import hashlib
from typing import Dict, Any, Optional, Union
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import json
import logging

logger = logging.getLogger(__name__)

class EncryptionService:
    """Service for encrypting and decrypting sensitive data at rest"""
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize encryption service with master key
        
        Args:
            master_key: Master encryption key (if None, will be generated or loaded from env)
        """
        self.master_key = master_key or os.getenv("ENCRYPTION_MASTER_KEY")
        if not self.master_key:
            raise ValueError("Master encryption key must be provided or set in ENCRYPTION_MASTER_KEY env var")
        
        # Derive encryption key from master key
        self.encryption_key = self._derive_key(self.master_key)
    
    def _derive_key(self, master_key: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from master key using PBKDF2"""
        if salt is None:
            salt = b'billions_bounty_salt_2024'  # Fixed salt for consistency
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # High iteration count for security
            backend=default_backend()
        )
        
        return kdf.derive(master_key.encode('utf-8'))
    
    def _generate_iv(self) -> bytes:
        """Generate random initialization vector"""
        return os.urandom(16)  # 128 bits for AES
    
    def encrypt_data(self, data: Union[str, Dict[str, Any]], field_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Encrypt sensitive data
        
        Args:
            data: Data to encrypt (string or dictionary)
            field_name: Optional field name for metadata
            
        Returns:
            Dictionary containing encrypted data and metadata
        """
        try:
            # Convert data to JSON string if it's a dictionary
            if isinstance(data, dict):
                data_str = json.dumps(data, sort_keys=True)
            else:
                data_str = str(data)
            
            # Generate IV
            iv = self._generate_iv()
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            # Pad data to block size (16 bytes for AES)
            padded_data = self._pad_data(data_str.encode('utf-8'))
            
            # Encrypt data
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Encode for storage
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            iv_b64 = base64.b64encode(iv).decode('utf-8')
            
            return {
                "encrypted_data": encrypted_b64,
                "iv": iv_b64,
                "field_name": field_name,
                "encryption_method": "AES-256-CBC",
                "key_derivation": "PBKDF2-SHA256",
                "iterations": 100000
            }
            
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise ValueError(f"Failed to encrypt data: {e}")
    
    def decrypt_data(self, encrypted_package: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_package: Dictionary containing encrypted data and metadata
            
        Returns:
            Decrypted data (string or dictionary)
        """
        try:
            # Extract components
            encrypted_b64 = encrypted_package["encrypted_data"]
            iv_b64 = encrypted_package["iv"]
            
            # Decode from base64
            encrypted_data = base64.b64decode(encrypted_b64)
            iv = base64.b64decode(iv_b64)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            # Decrypt data
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove padding
            decrypted_data = self._unpad_data(padded_data)
            
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(decrypted_data.decode('utf-8'))
            except json.JSONDecodeError:
                return decrypted_data.decode('utf-8')
                
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise ValueError(f"Failed to decrypt data: {e}")
    
    def encrypt_field(self, value: str, field_name: str) -> str:
        """
        Encrypt a single field value for database storage
        
        Args:
            value: Field value to encrypt
            field_name: Name of the field
            
        Returns:
            JSON string containing encrypted data
        """
        encrypted_package = self.encrypt_data(value, field_name)
        return json.dumps(encrypted_package)
    
    def decrypt_field(self, encrypted_json: str) -> str:
        """
        Decrypt a single field value from database storage
        
        Args:
            encrypted_json: JSON string containing encrypted data
            
        Returns:
            Decrypted field value
        """
        encrypted_package = json.loads(encrypted_json)
        return self.decrypt_data(encrypted_package)
    
    def encrypt_sensitive_fields(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """
        Encrypt multiple sensitive fields in a data dictionary
        
        Args:
            data: Dictionary containing data
            sensitive_fields: List of field names to encrypt
            
        Returns:
            Dictionary with sensitive fields encrypted
        """
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field] is not None:
                encrypted_data[field] = self.encrypt_field(str(encrypted_data[field]), field)
        
        return encrypted_data
    
    def decrypt_sensitive_fields(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """
        Decrypt multiple sensitive fields in a data dictionary
        
        Args:
            data: Dictionary containing encrypted data
            sensitive_fields: List of field names to decrypt
            
        Returns:
            Dictionary with sensitive fields decrypted
        """
        decrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field] is not None:
                try:
                    decrypted_data[field] = self.decrypt_field(decrypted_data[field])
                except Exception as e:
                    logger.warning(f"Failed to decrypt field {field}: {e}")
                    # Keep original value if decryption fails
                    pass
        
        return decrypted_data
    
    def _pad_data(self, data: bytes) -> bytes:
        """Pad data to AES block size (16 bytes)"""
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad_data(self, padded_data: bytes) -> bytes:
        """Remove padding from decrypted data"""
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]
    
    def generate_master_key(self) -> str:
        """Generate a new master encryption key"""
        return base64.b64encode(os.urandom(32)).decode('utf-8')
    
    def hash_sensitive_data(self, data: str) -> str:
        """Create a one-way hash of sensitive data for indexing/searching"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def verify_encryption_integrity(self, encrypted_package: Dict[str, Any]) -> bool:
        """Verify that encrypted data can be decrypted successfully"""
        try:
            self.decrypt_data(encrypted_package)
            return True
        except Exception:
            return False

class DatabaseEncryptionMixin:
    """Mixin class to add encryption capabilities to database models"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encryption_service = EncryptionService()
    
    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive data before database storage"""
        sensitive_fields = [
            'email', 'password_hash', 'wallet_address', 'wallet_signature',
            'user_message', 'ai_response', 'ip_address', 'user_agent',
            'additional_data', 'session_id'
        ]
        return self.encryption_service.encrypt_sensitive_fields(data, sensitive_fields)
    
    def decrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive data after database retrieval"""
        sensitive_fields = [
            'email', 'password_hash', 'wallet_address', 'wallet_signature',
            'user_message', 'ai_response', 'ip_address', 'user_agent',
            'additional_data', 'session_id'
        ]
        return self.encryption_service.decrypt_sensitive_fields(data, sensitive_fields)

# Utility functions for easy integration
def encrypt_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypt user data for storage"""
    encryption_service = EncryptionService()
    sensitive_fields = ['email', 'wallet_address', 'wallet_signature', 'session_id']
    return encryption_service.encrypt_sensitive_fields(user_data, sensitive_fields)

def decrypt_user_data(encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
    """Decrypt user data for retrieval"""
    encryption_service = EncryptionService()
    sensitive_fields = ['email', 'wallet_address', 'wallet_signature', 'session_id']
    return encryption_service.decrypt_sensitive_fields(encrypted_data, sensitive_fields)

def encrypt_conversation_data(conversation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypt conversation data for storage"""
    encryption_service = EncryptionService()
    sensitive_fields = ['user_message', 'ai_response', 'ip_address', 'user_agent', 'session_id']
    return encryption_service.encrypt_sensitive_fields(conversation_data, sensitive_fields)

def decrypt_conversation_data(encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
    """Decrypt conversation data for retrieval"""
    encryption_service = EncryptionService()
    sensitive_fields = ['user_message', 'ai_response', 'ip_address', 'user_agent', 'session_id']
    return encryption_service.decrypt_sensitive_fields(encrypted_data, sensitive_fields)
