"""
AI Decision Service - Handles cryptographic signing of AI decisions
"""
import hashlib
import json
import time
from typing import Dict, Any, Optional, List
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import os
from dotenv import load_dotenv
from .semantic_decision_analyzer import SemanticDecisionAnalyzer

load_dotenv()

class AIDecisionService:
    """Service for creating cryptographically signed AI decisions"""
    
    def __init__(self):
        self.private_key = self._load_or_generate_private_key()
        self.public_key = self.private_key.public_key()
        self.semantic_analyzer = SemanticDecisionAnalyzer()
        
    def _load_or_generate_private_key(self) -> ed25519.Ed25519PrivateKey:
        """Load existing private key or generate new one"""
        private_key_path = os.getenv("AI_DECISION_PRIVATE_KEY_PATH", "ai_decision_key.pem")
        
        if os.path.exists(private_key_path):
            # Load existing key
            with open(private_key_path, "rb") as key_file:
                private_key = load_pem_private_key(
                    key_file.read(),
                    password=None
                )
                return private_key
        else:
            # Generate new key
            private_key = ed25519.Ed25519PrivateKey.generate()
            
            # Save private key
            with open(private_key_path, "wb") as key_file:
                key_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                key_file.write(key_pem)
            
            # Save public key
            public_key_path = private_key_path.replace(".pem", "_public.pem")
            with open(public_key_path, "wb") as key_file:
                public_key_pem = private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                key_file.write(public_key_pem)
            
            print(f"🔑 Generated new AI decision key pair:")
            print(f"   Private key: {private_key_path}")
            print(f"   Public key: {public_key_path}")
            
            return private_key
    
    def get_public_key_bytes(self) -> bytes:
        """Get public key as bytes for smart contract verification"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    def create_ai_decision(
        self, 
        user_message: str, 
        ai_response: str, 
        is_successful_jailbreak: bool,
        user_id: int,
        session_id: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a cryptographically signed AI decision with semantic analysis"""
        
        # Perform semantic analysis for research purposes
        semantic_analysis = self.semantic_analyzer.analyze_decision(
            user_message=user_message,
            ai_response=ai_response,
            conversation_history=conversation_history or [],
            user_profile=user_profile or {},
            decision_context={
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": int(time.time())
            }
        )
        
        # Create decision data with research analysis
        decision_data = {
            "user_message": user_message,
            "ai_response": ai_response,
            "is_successful_jailbreak": is_successful_jailbreak,
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": int(time.time()),
            "nonce": os.urandom(16).hex(),  # Prevent replay attacks
            "research_analysis": {
                "manipulation_types": [t.value for t in semantic_analysis.manipulation_types],
                "detected_patterns": semantic_analysis.detected_patterns,
                "context_anomalies": semantic_analysis.context_anomalies,
                "sophistication_level": semantic_analysis.sophistication_level,
                "user_behavior_notes": semantic_analysis.user_behavior_notes,
                "research_insights": semantic_analysis.research_insights
            }
        }
        
        # Create hash of decision data
        decision_json = json.dumps(decision_data, sort_keys=True)
        decision_hash = hashlib.sha256(decision_json.encode()).digest()
        
        # Sign the hash
        signature = self.private_key.sign(decision_hash)
        
        # Create the signed decision
        signed_decision = {
            "decision_data": decision_data,
            "decision_hash": decision_hash.hex(),
            "signature": signature.hex(),
            "public_key": self.get_public_key_bytes().hex()
        }
        
        return signed_decision
    
    def verify_decision(self, signed_decision: Dict[str, Any]) -> bool:
        """Verify a signed decision (for testing)"""
        try:
            # Recreate the hash
            decision_json = json.dumps(signed_decision["decision_data"], sort_keys=True)
            expected_hash = hashlib.sha256(decision_json.encode()).digest()
            
            # Verify hash matches
            if expected_hash.hex() != signed_decision["decision_hash"]:
                return False
            
            # Verify signature
            signature = bytes.fromhex(signed_decision["signature"])
            public_key_bytes = bytes.fromhex(signed_decision["public_key"])
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            
            public_key.verify(signature, expected_hash)
            return True
            
        except Exception as e:
            print(f"❌ Decision verification failed: {e}")
            return False
    
    def get_research_insights(self, signed_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Get research insights from decision analysis"""
        try:
            decision_data = signed_decision["decision_data"]
            research_analysis = decision_data.get("research_analysis", {})
            
            return {
                "manipulation_techniques": research_analysis.get("manipulation_types", []),
                "sophistication_level": research_analysis.get("sophistication_level", "unknown"),
                "behavioral_patterns": research_analysis.get("user_behavior_notes", []),
                "research_value": research_analysis.get("research_insights", {}).get("research_value", "low"),
                "technique_diversity": research_analysis.get("research_insights", {}).get("technique_diversity", 0),
                "context_anomalies": research_analysis.get("context_anomalies", [])
            }
                
        except Exception as e:
            return {
                "error": f"Failed to extract research insights: {e}",
                "manipulation_techniques": [],
                "sophistication_level": "unknown",
                "research_value": "unknown"
            }
    
    def get_decision_summary(self, signed_decision: Dict[str, Any]) -> str:
        """Get a human-readable summary of the decision"""
        data = signed_decision["decision_data"]
        return f"""
🤖 AI Decision Summary:
   User ID: {data['user_id']}
   Session: {data['session_id'][:8]}...
   Jailbreak Success: {'✅ YES' if data['is_successful_jailbreak'] else '❌ NO'}
   Timestamp: {time.ctime(data['timestamp'])}
   Hash: {signed_decision['decision_hash'][:16]}...
   Signature: {signed_decision['signature'][:16]}...
        """

    def build_v3_payload(
        self,
        user_message: str,
        ai_response: str,
        is_successful_jailbreak: bool,
        user_id: int,
        session_id: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        model_id: Optional[str] = None,
        timestamp: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Build a minimal contract-friendly payload for the V3 on-chain AI decision flow.

        This mirrors the `AIDecisionPayload` struct in the V3 program and is
        intended to be used when submitting decisions via `process_ai_decision_v3`.

        The contract currently treats the AI signature as an integrity hint and
        enforces authority + hashing checks. To keep things future-proof, this
        method also signs a canonical JSON representation of the payload so a
        later on-chain Ed25519 integration can verify it.
        """
        # Derive timestamp if not provided.
        ts = timestamp or int(time.time())

        # Derive decision flag (0 = deny, 1 = allow) from jailbreak outcome.
        decision_flag = 1 if is_successful_jailbreak else 0

        # Compute a stable hash of the conversation history for auditability.
        conv_history = conversation_history or []
        conv_json = json.dumps(conv_history, sort_keys=True)
        conversation_hash = hashlib.sha256(conv_json.encode()).digest()

        # Derive a model identifier hash from a provided model_id or environment.
        model_id_source = model_id or os.getenv("AI_MODEL_ID", "unknown-model")
        model_id_hash = hashlib.sha256(model_id_source.encode()).digest()

        # Construct the payload dict that matches AIDecisionPayload in the program.
        payload: Dict[str, Any] = {
            "decision": decision_flag,
            "user_message": user_message,
            "ai_response": ai_response,
            "model_id_hash": model_id_hash,
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": ts,
            "conversation_hash": conversation_hash,
        }

        # Create a canonical JSON snapshot of the payload for signing.
        serializable_payload = {
            "decision": decision_flag,
            "user_message": user_message,
            "ai_response": ai_response,
            "model_id_hash": model_id_hash.hex(),
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": ts,
            "conversation_hash": conversation_hash.hex(),
        }
        payload_json = json.dumps(serializable_payload, sort_keys=True).encode()

        # Sign the payload snapshot with the AI decision key.
        ai_signature = self.private_key.sign(payload_json)

        # Attach signature and public key so the caller can forward them on-chain.
        payload["ai_signature"] = ai_signature
        payload["ai_public_key"] = self.get_public_key_bytes()

        return payload

# Global instance
ai_decision_service = AIDecisionService()
