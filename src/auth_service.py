"""
Authentication Service - Handles secure password management and user authentication
"""
import bcrypt
import secrets
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from .models import User, EmailVerification
from .email_service import email_service

class AuthService:
    """Service for secure authentication and password management"""
    
    def __init__(self):
        self.bcrypt_rounds = 12  # Secure bcrypt rounds
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength_score": self._calculate_strength_score(password)
        }
    
    def _calculate_strength_score(self, password: str) -> int:
        """Calculate password strength score (0-100)"""
        score = 0
        
        # Length bonus
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        
        # Character variety bonus
        if any(c.isupper() for c in password):
            score += 10
        if any(c.islower() for c in password):
            score += 10
        if any(c.isdigit() for c in password):
            score += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 10
        
        # Pattern penalties
        if password.lower() in ["password", "123456", "qwerty", "abc123"]:
            score -= 50
        
        return min(max(score, 0), 100)
    
    async def create_user(self, session: AsyncSession, email: str, password: str, 
                         display_name: Optional[str] = None, 
                         session_id: Optional[str] = None,
                         ip_address: Optional[str] = None,
                         user_agent: Optional[str] = None) -> Tuple[User, Dict[str, Any]]:
        """Create a new user with secure password hashing"""
        
        # Validate password strength
        password_validation = self.validate_password_strength(password)
        if not password_validation["is_valid"]:
            return None, {
                "success": False,
                "error": "Password does not meet requirements",
                "validation_errors": password_validation["errors"]
            }
        
        # Check if email already exists
        existing_user = await session.execute(
            select(User).where(User.email == email)
        )
        if existing_user.scalar_one_or_none():
            return None, {
                "success": False,
                "error": "Email already registered"
            }
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user
        user = User(
            session_id=session_id or secrets.token_urlsafe(32),
            email=email,
            password_hash=password_hash,
            display_name=display_name,
            ip_address=ip_address,
            user_agent=user_agent,
            is_verified=False  # Will be verified via email
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return user, {
            "success": True,
            "message": "User created successfully",
            "user_id": user.id,
            "email": user.email,
            "requires_verification": True
        }
    
    async def authenticate_user(self, session: AsyncSession, email: str, password: str) -> Tuple[Optional[User], Dict[str, Any]]:
        """Authenticate user with email and password"""
        
        # Find user by email
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None, {
                "success": False,
                "error": "Invalid credentials"
            }
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            return None, {
                "success": False,
                "error": "Invalid credentials"
            }
        
        # Check if user is verified
        if not user.is_verified:
            return user, {
                "success": False,
                "error": "Email not verified",
                "requires_verification": True,
                "user_id": user.id
            }
        
        return user, {
            "success": True,
            "message": "Authentication successful",
            "user_id": user.id,
            "email": user.email
        }
    
    async def reset_password(self, session: AsyncSession, token: str, new_password: str) -> Dict[str, Any]:
        """Reset user password using verification token"""
        
        # Validate new password
        password_validation = self.validate_password_strength(new_password)
        if not password_validation["is_valid"]:
            return {
                "success": False,
                "error": "Password does not meet requirements",
                "validation_errors": password_validation["errors"]
            }
        
        # Find verification record
        result = await session.execute(
            select(EmailVerification)
            .where(
                EmailVerification.verification_token == token,
                EmailVerification.verification_type == "password_reset",
                EmailVerification.is_used == False,
                EmailVerification.expires_at > datetime.utcnow()
            )
        )
        verification = result.scalar_one_or_none()
        
        if not verification:
            return {
                "success": False,
                "error": "Invalid or expired reset token"
            }
        
        # Hash new password
        new_password_hash = self.hash_password(new_password)
        
        # Update user password
        await session.execute(
            update(User)
            .where(User.id == verification.user_id)
            .values(password_hash=new_password_hash)
        )
        
        # Mark token as used
        await session.execute(
            update(EmailVerification)
            .where(EmailVerification.id == verification.id)
            .values(
                is_used=True,
                used_at=datetime.utcnow()
            )
        )
        
        await session.commit()
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
    
    async def change_password(self, session: AsyncSession, user_id: int, 
                            current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password (requires current password)"""
        
        # Get user
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {
                "success": False,
                "error": "User not found"
            }
        
        # Verify current password
        if not self.verify_password(current_password, user.password_hash):
            return {
                "success": False,
                "error": "Current password is incorrect"
            }
        
        # Validate new password
        password_validation = self.validate_password_strength(new_password)
        if not password_validation["is_valid"]:
            return {
                "success": False,
                "error": "Password does not meet requirements",
                "validation_errors": password_validation["errors"]
            }
        
        # Hash new password
        new_password_hash = self.hash_password(new_password)
        
        # Update password
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_hash=new_password_hash)
        )
        
        await session.commit()
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }

# Global instance
auth_service = AuthService()
