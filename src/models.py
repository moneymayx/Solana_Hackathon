"""
Database models for Billions
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Float, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class User(Base):
    """User model for tracking sessions and attempts"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Authentication fields
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Free question tracking
    anonymous_free_questions_used: Mapped[int] = mapped_column(Integer, default=0)  # 2 max for anonymous users
    has_used_anonymous_questions: Mapped[bool] = mapped_column(Boolean, default=False)  # Track if user used anonymous questions
    
    # Wallet integration fields (primary authentication method)
    wallet_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)
    wallet_connected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    wallet_signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Store wallet signature for verification
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Optional display name
    
    # KYC fields
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    kyc_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, verified, rejected
    kyc_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # moonpay, manual
    kyc_reference_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="user")
    attack_attempts: Mapped[list["AttackAttempt"]] = relationship("AttackAttempt", back_populates="user")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user")
    wins: Mapped[list["Winner"]] = relationship("Winner", back_populates="user")

class Conversation(Base):
    """Conversation model for storing chat history"""
    __tablename__ = "conversations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    message_type: Mapped[str] = mapped_column(String(20))  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")

class AttackAttempt(Base):
    """Model for logging potential manipulation attempts"""
    __tablename__ = "attack_attempts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    attempt_type: Mapped[str] = mapped_column(String(100))  # e.g., 'jailbreak', 'social_engineering', 'prompt_injection'
    message_content: Mapped[str] = mapped_column(Text)
    ai_response: Mapped[str] = mapped_column(Text)
    threat_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1 scale
    was_successful: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="attack_attempts")

class Transaction(Base):
    """Model for tracking prize pool transactions and costs"""
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    transaction_type: Mapped[str] = mapped_column(String(50))  # 'query_fee', 'prize_contribution', 'payout'
    amount: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    conversation_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("conversations.id"), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")

class PrizePool(Base):
    """Model for tracking the current prize pool status"""
    __tablename__ = "prize_pool"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    current_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total_contributions: Mapped[float] = mapped_column(Float, default=0.0)
    total_queries: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    base_query_cost: Mapped[float] = mapped_column(Float, default=10.0)  # Starting at $10
    escalation_rate: Mapped[float] = mapped_column(Float, default=0.0078)  # 0.78% increase
    max_query_cost: Mapped[float] = mapped_column(Float, default=4500.0)  # Max $4,500

class SecurityEvent(Base):
    """Model for logging security-related events"""
    __tablename__ = "security_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100))  # e.g., 'rate_limit_exceeded', 'suspicious_pattern', 'validation_failed'
    severity: Mapped[str] = mapped_column(String(20))  # 'low', 'medium', 'high', 'critical'
    description: Mapped[str] = mapped_column(Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    additional_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string for extra data

class PaymentTransaction(Base):
    """Model for tracking wallet and fiat payment transactions"""
    __tablename__ = "payment_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    payment_method: Mapped[str] = mapped_column(String(50))  # 'wallet', 'moonpay'
    payment_type: Mapped[str] = mapped_column(String(50))  # 'query_payment', 'deposit'
    
    # Amount details
    amount_usd: Mapped[float] = mapped_column(Float)
    amount_crypto: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    crypto_currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # 'SOL', 'ETH', etc.
    
    # Transaction identifiers
    tx_signature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  # Blockchain signature
    moonpay_tx_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  # Moonpay transaction ID
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, confirmed, failed, cancelled
    
    # Wallet details
    from_wallet: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    to_wallet: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps and additional data
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    extra_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON for additional data
    
    # Relationships
    user: Mapped["User"] = relationship("User")

class BountyState(Base):
    """Model for tracking bounty state and rollover logic"""
    __tablename__ = "bounty_states"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    current_jackpot_usd: Mapped[float] = mapped_column(Float, default=10000.0)  # PRIZE_FLOOR_USD
    total_entries_this_period: Mapped[int] = mapped_column(Integer, default=0)
    last_winner_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    last_participant_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # Last person who asked a question
    last_question_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # Timestamp of last question
    last_rollover_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    next_rollover_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    last_winner: Mapped[Optional["User"]] = relationship("User", foreign_keys=[last_winner_id])
    last_participant: Mapped[Optional["User"]] = relationship("User", foreign_keys=[last_participant_id])

class BountyEntry(Base):
    """Model for tracking individual bounty entries"""
    __tablename__ = "bounty_entries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    entry_fee_usd: Mapped[float] = mapped_column(Float, default=10.0)
    pool_contribution: Mapped[float] = mapped_column(Float, default=8.0)  # 80% of entry fee
    operational_fee: Mapped[float] = mapped_column(Float, default=2.0)  # 20% of entry fee
    message_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False)
    prize_payout: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User")

class BlacklistedPhrase(Base):
    """Model for tracking successful manipulation phrases that are now blacklisted"""
    __tablename__ = "blacklisted_phrases"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phrase: Mapped[str] = mapped_column(Text, unique=True, index=True)  # The exact phrase that worked
    original_message: Mapped[str] = mapped_column(Text)  # The full original message
    successful_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # Who first used it successfully
    success_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Can be deactivated if needed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    successful_user: Mapped["User"] = relationship("User")

class Winner(Base):
    """Winner model for tracking jackpot winners and their connected wallets"""
    __tablename__ = "winners"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    wallet_address: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    prize_amount: Mapped[float] = mapped_column(Float, nullable=False)
    token: Mapped[str] = mapped_column(String(10), nullable=False)  # SOL, USDC, USDT
    transaction_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    won_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # For potential pardons
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="wins")
    connected_wallets: Mapped[list["ConnectedWallet"]] = relationship("ConnectedWallet", back_populates="winner")

class ConnectedWallet(Base):
    """Connected wallet model for tracking wallets connected to winners"""
    __tablename__ = "connected_wallets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    winner_id: Mapped[int] = mapped_column(Integer, ForeignKey("winners.id"))
    wallet_address: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    connection_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'direct_transfer', 'funding_source', 'exchange_connected'
    connection_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string with connection info
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    winner: Mapped["Winner"] = relationship("Winner", back_populates="connected_wallets")

class EmailVerification(Base):
    """Email verification tokens for user account verification"""
    __tablename__ = "email_verifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    verification_token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    verification_type: Mapped[str] = mapped_column(String(50), default="email_verification")  # 'email_verification', 'password_reset'
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")

class WalletFundingSource(Base):
    """Wallet funding source model for tracking where wallets get their funds"""
    __tablename__ = "wallet_funding_sources"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    wallet_address: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    funding_source: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # Exchange address, other wallet, etc.
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    total_funding_amount: Mapped[float] = mapped_column(Float, default=0.0)
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)

class ReferralCode(Base):
    """Referral code model for tracking user referral codes"""
    __tablename__ = "referral_codes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    referral_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    total_uses: Mapped[int] = mapped_column(Integer, default=0)
    total_free_questions_earned: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    referrals: Mapped[list["Referral"]] = relationship("Referral", back_populates="referral_code")

class FundDeposit(Base):
    """Model for tracking fund deposits and routing"""
    __tablename__ = "fund_deposits"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transaction_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    wallet_address: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Amount details
    amount_usd: Mapped[float] = mapped_column(Float)
    amount_usdc: Mapped[float] = mapped_column(Float)
    
    # Payment method and routing
    payment_method: Mapped[str] = mapped_column(String(50))  # 'moonpay', 'wallet'
    deposit_wallet: Mapped[str] = mapped_column(String(255), nullable=False)  # Where funds were deposited
    target_wallet: Mapped[str] = mapped_column(String(255), nullable=False)  # Where funds should be routed
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, routed, routing_failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    routed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Additional data
    extra_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON for additional data

class FundTransfer(Base):
    """Model for tracking fund transfers between wallets"""
    __tablename__ = "fund_transfers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    deposit_id: Mapped[int] = mapped_column(Integer, ForeignKey("fund_deposits.id"))
    
    # Transfer details
    from_wallet: Mapped[str] = mapped_column(String(255), nullable=False)
    to_wallet: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_usdc: Mapped[float] = mapped_column(Float)
    
    # Transaction details
    transaction_signature: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, completed, failed
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    deposit: Mapped["FundDeposit"] = relationship("FundDeposit")

class Referral(Base):
    """Referral model for tracking successful referrals"""
    __tablename__ = "referrals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    referrer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    referee_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    referral_code_id: Mapped[int] = mapped_column(Integer, ForeignKey("referral_codes.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    referrer: Mapped["User"] = relationship("User", foreign_keys=[referrer_id])
    referee: Mapped["User"] = relationship("User", foreign_keys=[referee_id])
    referral_code: Mapped["ReferralCode"] = relationship("ReferralCode", back_populates="referrals")

class FreeQuestions(Base):
    """Free questions model for tracking free questions earned through referrals"""
    __tablename__ = "free_questions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    source: Mapped[str] = mapped_column(String(50))  # 'referral_bonus', 'referral_signup', 'anonymous'
    referral_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("referrals.id"), nullable=True)
    questions_earned: Mapped[int] = mapped_column(Integer, default=5)  # 5 free questions per referral, 2 for anonymous
    questions_used: Mapped[int] = mapped_column(Integer, default=0)
    questions_remaining: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # Optional expiration
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    referral: Mapped[Optional["Referral"]] = relationship("Referral")
