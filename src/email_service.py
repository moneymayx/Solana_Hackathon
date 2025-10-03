"""
Email Service - Handles email verification and notifications
"""
import os
import secrets
import smtplib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from .models import EmailVerification, User

class EmailService:
    """Service for sending emails and managing verification tokens"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@billionsbounty.com")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
    def _generate_verification_token(self) -> str:
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)
    
    def _create_verification_email(self, email: str, token: str, verification_type: str = "email_verification") -> MIMEMultipart:
        """Create verification email content"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Verify Your Billions Bounty Account"
        msg['From'] = self.from_email
        msg['To'] = email
        
        if verification_type == "email_verification":
            subject = "Verify Your Billions Bounty Account"
            verification_url = f"{self.frontend_url}/verify-email?token={token}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">🔬 Billions Bounty</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">AI Security Research Platform</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333; margin-top: 0;">Welcome to Billions Bounty!</h2>
                    <p style="color: #666; line-height: 1.6;">
                        Thank you for joining our AI security research platform. To complete your account setup, 
                        please verify your email address by clicking the button below.
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" 
                           style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                  color: white; 
                                  padding: 15px 30px; 
                                  text-decoration: none; 
                                  border-radius: 25px; 
                                  font-weight: bold; 
                                  display: inline-block;">
                            Verify Email Address
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        If the button doesn't work, you can also copy and paste this link into your browser:<br>
                        <a href="{verification_url}" style="color: #667eea; word-break: break-all;">{verification_url}</a>
                    </p>
                    
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin-top: 20px;">
                        <p style="margin: 0; color: #1976d2; font-size: 14px;">
                            <strong>What's next?</strong><br>
                            • Verify your email to access your account<br>
                            • Connect your wallet for enhanced features<br>
                            • Start your AI security research journey
                        </p>
                    </div>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 30px; text-align: center;">
                        This verification link will expire in 24 hours.<br>
                        If you didn't create an account, please ignore this email.
                    </p>
                </div>
            </body>
            </html>
            """
            
        elif verification_type == "password_reset":
            subject = "Reset Your Billions Bounty Password"
            verification_url = f"{self.frontend_url}/reset-password?token={token}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">🔒 Password Reset</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Billions Bounty Security</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333; margin-top: 0;">Password Reset Request</h2>
                    <p style="color: #666; line-height: 1.6;">
                        We received a request to reset your password. Click the button below to create a new password.
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" 
                           style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); 
                                  color: white; 
                                  padding: 15px 30px; 
                                  text-decoration: none; 
                                  border-radius: 25px; 
                                  font-weight: bold; 
                                  display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        If the button doesn't work, you can also copy and paste this link into your browser:<br>
                        <a href="{verification_url}" style="color: #ff6b6b; word-break: break-all;">{verification_url}</a>
                    </p>
                    
                    <div style="background: #ffebee; padding: 15px; border-radius: 5px; margin-top: 20px;">
                        <p style="margin: 0; color: #c62828; font-size: 14px;">
                            <strong>Security Notice:</strong><br>
                            • This link will expire in 1 hour<br>
                            • If you didn't request this reset, please ignore this email<br>
                            • Your account remains secure
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        # Create plain text version
        text_content = f"""
        Billions Bounty - {subject}
        
        Please click the following link to verify your account:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        """
        
        # Attach both versions
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        return msg
    
    async def send_verification_email(self, session: AsyncSession, user_id: int, email: str, 
                                    verification_type: str = "email_verification") -> Dict[str, Any]:
        """Send verification email to user"""
        try:
            # Generate verification token
            token = self._generate_verification_token()
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # Create verification record
            verification = EmailVerification(
                user_id=user_id,
                email=email,
                verification_token=token,
                verification_type=verification_type,
                expires_at=expires_at
            )
            session.add(verification)
            await session.commit()
            
            # Create email
            email_msg = self._create_verification_email(email, token, verification_type)
            
            # Send email
            if self.smtp_username and self.smtp_password:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(email_msg)
                
                return {
                    "success": True,
                    "message": "Verification email sent successfully",
                    "token": token  # For testing purposes
                }
            else:
                return {
                    "success": False,
                    "error": "SMTP credentials not configured",
                    "token": token  # For testing purposes
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send verification email: {str(e)}"
            }
    
    async def verify_email_token(self, session: AsyncSession, token: str) -> Dict[str, Any]:
        """Verify email token and update user status"""
        try:
            # Find verification record
            result = await session.execute(
                select(EmailVerification)
                .where(
                    and_(
                        EmailVerification.verification_token == token,
                        EmailVerification.is_used == False,
                        EmailVerification.expires_at > datetime.utcnow()
                    )
                )
            )
            verification = result.scalar_one_or_none()
            
            if not verification:
                return {
                    "success": False,
                    "error": "Invalid or expired verification token"
                }
            
            # Mark token as used
            await session.execute(
                update(EmailVerification)
                .where(EmailVerification.id == verification.id)
                .values(
                    is_used=True,
                    used_at=datetime.utcnow()
                )
            )
            
            # Update user verification status
            await session.execute(
                update(User)
                .where(User.id == verification.user_id)
                .values(is_verified=True)
            )
            
            await session.commit()
            
            return {
                "success": True,
                "message": "Email verified successfully",
                "user_id": verification.user_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to verify email: {str(e)}"
            }
    
    async def send_password_reset_email(self, session: AsyncSession, email: str) -> Dict[str, Any]:
        """Send password reset email"""
        try:
            # Find user by email
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {
                    "success": False,
                    "error": "Email not found"
                }
            
            # Send password reset email
            return await self.send_verification_email(
                session, user.id, email, "password_reset"
            )
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send password reset email: {str(e)}"
            }

# Global instance
email_service = EmailService()
