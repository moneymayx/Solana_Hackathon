"""
Database models for Billions
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Float, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
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
    anonymous_free_questions_used: Mapped[int] = mapped_column(Integer, default=0)  # 1 max for anonymous users
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

class Bounty(Base):
    """Bounty model for different LLM challenges"""
    __tablename__ = "bounties"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))  # e.g., "Claude Champ", "GPT-4 Bounty"
    llm_provider: Mapped[str] = mapped_column(String(50))  # e.g., "claude", "gpt-4", "gemini", "llama"
    current_pool: Mapped[float] = mapped_column(Float, default=0.0)
    total_entries: Mapped[int] = mapped_column(Integer, default=0)
    win_rate: Mapped[float] = mapped_column(Float, default=0.0)  # Percentage
    difficulty_level: Mapped[str] = mapped_column(String(20), default="medium")  # easy, medium, hard, expert
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="bounty")

class Conversation(Base):
    """Conversation model for storing chat history"""
    __tablename__ = "conversations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    bounty_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("bounties.id"), nullable=True, index=True)
    message_type: Mapped[str] = mapped_column(String(20))  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    bounty: Mapped["Bounty"] = relationship("Bounty", back_populates="conversations")

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


# ===========================
# PHASE 2: TOKEN ECONOMICS MODELS ($100Bs)
# ===========================

class TokenBalance(Base):
    """
    Track user's $100Bs token balance and last verification
    """
    __tablename__ = "token_balances"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, index=True)
    wallet_address: Mapped[str] = mapped_column(String(255), index=True)
    
    # Token balance
    token_balance: Mapped[float] = mapped_column(Float, default=0.0)
    last_verified: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Current discount tier
    discount_rate: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 to 0.5
    tokens_to_next_tier: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User")


class StakingPosition(Base):
    """
    Track user's staked $100Bs tokens
    """
    __tablename__ = "staking_positions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # Staking details
    staked_amount: Mapped[float] = mapped_column(Float)
    staking_period_days: Mapped[int] = mapped_column(Integer)  # 30, 60, or 90
    apy_rate: Mapped[float] = mapped_column(Float)  # APY at time of staking
    
    # Timing
    staked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    unlocks_at: Mapped[datetime] = mapped_column(DateTime)
    
    # Rewards
    estimated_rewards: Mapped[float] = mapped_column(Float)
    claimed_rewards: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # On-chain reference
    transaction_signature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")


class BuybackEvent(Base):
    """
    Track platform token buyback events
    """
    __tablename__ = "buyback_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Buyback details
    revenue_amount: Mapped[float] = mapped_column(Float)  # Total revenue for period
    buyback_amount: Mapped[float] = mapped_column(Float)  # 5% allocated to buyback
    tokens_bought: Mapped[float] = mapped_column(Float)  # Tokens purchased
    average_price: Mapped[float] = mapped_column(Float)  # Average price per token
    
    # Timing
    period_start: Mapped[datetime] = mapped_column(DateTime)
    period_end: Mapped[datetime] = mapped_column(DateTime)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # On-chain reference
    transaction_signature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, executed, failed


class TokenPrice(Base):
    """
    Track $100Bs token price history
    """
    __tablename__ = "token_prices"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Price data
    price_usd: Mapped[float] = mapped_column(Float)
    volume_24h: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    market_cap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Source
    source: Mapped[str] = mapped_column(String(50), default="jupiter")  # jupiter, raydium, etc.
    
    # Timestamp
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class DiscountUsage(Base):
    """
    Track usage of token holder discounts
    """
    __tablename__ = "discount_usage"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # Discount details
    base_price: Mapped[float] = mapped_column(Float)
    discount_rate: Mapped[float] = mapped_column(Float)
    discount_amount: Mapped[float] = mapped_column(Float)
    final_price: Mapped[float] = mapped_column(Float)
    
    # Token balance at time of discount
    token_balance: Mapped[float] = mapped_column(Float)
    
    # Service details
    service_type: Mapped[str] = mapped_column(String(100), default="query")  # query, entry_fee, etc.
    
    # Timestamp
    used_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User")


# ===========================
# PHASE 1: CONTEXT WINDOW MANAGEMENT MODELS
# ===========================

class MessageEmbedding(Base):
    """
    Store vector embeddings of user messages for semantic search
    Used to find similar historical attack attempts
    """
    __tablename__ = "message_embeddings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("conversations.id"), index=True)
    message_content: Mapped[str] = mapped_column(Text)
    
    # Vector embedding (1536 dimensions for OpenAI ada-002)
    embedding: Mapped[list] = mapped_column(Vector(1536))
    
    # Metadata
    was_attack: Mapped[bool] = mapped_column(Boolean, default=False)
    attack_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    threat_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    conversation: Mapped["Conversation"] = relationship("Conversation")


class AttackPattern(Base):
    """
    Store detected attack patterns and techniques
    Used for pattern recognition and adaptive defense
    """
    __tablename__ = "attack_patterns"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Pattern classification
    pattern_type: Mapped[str] = mapped_column(String(100), index=True)  # e.g., 'role_play', 'function_confusion', 'emotional_manipulation'
    pattern_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    
    # Pattern details
    example_messages: Mapped[dict] = mapped_column(JSON)  # List of example messages
    indicators: Mapped[dict] = mapped_column(JSON)  # Keywords, phrases, structure patterns
    
    # Effectiveness tracking
    times_seen: Mapped[int] = mapped_column(Integer, default=1)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    avg_threat_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Detection confidence
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)  # How confident we are in this pattern
    
    # Timestamps
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    should_monitor: Mapped[bool] = mapped_column(Boolean, default=True)


class ContextSummary(Base):
    """
    Store summarized context from older conversations
    Used to reduce token usage while maintaining awareness of user history
    """
    __tablename__ = "context_summaries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # Time window for this summary
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    # Summary content
    summary_text: Mapped[str] = mapped_column(Text)  # AI-generated summary of the conversation period
    message_count: Mapped[int] = mapped_column(Integer)  # Number of messages summarized
    
    # Key insights
    attack_types_seen: Mapped[dict] = mapped_column(JSON)  # Dict of attack types and counts
    user_techniques: Mapped[dict] = mapped_column(JSON)  # Notable techniques user tried
    ai_responses: Mapped[dict] = mapped_column(JSON)  # Key AI response patterns
    
    # Metadata
    token_savings: Mapped[int] = mapped_column(Integer)  # Estimated tokens saved by summarizing
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User")


# ===========================
# PHASE 3: TEAM COLLABORATION MODELS
# ===========================

class Team(Base):
    """
    Team model for collaborative attempts
    Users can form teams to pool resources and share strategies
    """
    __tablename__ = "teams"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Team leader
    leader_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # Team settings
    max_members: Mapped[int] = mapped_column(Integer, default=5)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)  # Public teams appear in discovery
    invite_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    
    # Team stats
    total_pool: Mapped[float] = mapped_column(Float, default=0.0)  # Current pooled funds
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    total_spent: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leader: Mapped["User"] = relationship("User", foreign_keys=[leader_id])
    members: Mapped[list["TeamMember"]] = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    invitations: Mapped[list["TeamInvitation"]] = relationship("TeamInvitation", back_populates="team", cascade="all, delete-orphan")
    attempts: Mapped[list["TeamAttempt"]] = relationship("TeamAttempt", back_populates="team", cascade="all, delete-orphan")
    messages: Mapped[list["TeamMessage"]] = relationship("TeamMessage", back_populates="team", cascade="all, delete-orphan")
    fundings: Mapped[list["TeamFunding"]] = relationship("TeamFunding", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    """
    Team membership record
    Tracks who's in the team and their contribution share
    """
    __tablename__ = "team_members"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # Role
    role: Mapped[str] = mapped_column(String(50), default="member")  # leader, member, viewer
    
    # Contribution tracking
    total_contributed: Mapped[float] = mapped_column(Float, default=0.0)
    contribution_percentage: Mapped[float] = mapped_column(Float, default=0.0)  # Share of team pool
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="members")
    user: Mapped["User"] = relationship("User")


class TeamInvitation(Base):
    """
    Team invitation record
    Tracks pending invitations to join a team
    """
    __tablename__ = "team_invitations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), index=True)
    
    # Invitee
    invitee_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    invitee_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # For non-registered users
    
    # Inviter
    inviter_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, accepted, declined, expired
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)  # Invitations expire after 7 days
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="invitations")
    invitee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[invitee_user_id])
    inviter: Mapped["User"] = relationship("User", foreign_keys=[inviter_user_id])


class TeamAttempt(Base):
    """
    Team attempt record
    Tracks attempts made by the team
    """
    __tablename__ = "team_attempts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), index=True)
    
    # Attempt details
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("conversations.id"), index=True)
    initiated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)  # Which member made the attempt
    
    # Cost breakdown
    cost: Mapped[float] = mapped_column(Float)
    funded_by_pool: Mapped[float] = mapped_column(Float, default=0.0)  # Amount from team pool
    funded_by_initiator: Mapped[float] = mapped_column(Float, default=0.0)  # Amount from initiator's wallet
    
    # Result
    was_successful: Mapped[bool] = mapped_column(Boolean, default=False)
    threat_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # AI Response
    ai_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="attempts")
    conversation: Mapped["Conversation"] = relationship("Conversation")
    initiator: Mapped["User"] = relationship("User")


class TeamMessage(Base):
    """
    Team chat message
    Internal team communication for strategy sharing
    """
    __tablename__ = "team_messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # Message content
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[str] = mapped_column(String(50), default="text")  # text, system, strategy, attempt_result
    
    # Optional extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # For strategy links, attempt refs, etc.
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Status
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="messages")
    user: Mapped["User"] = relationship("User")


class TeamFunding(Base):
    """
    Team funding record
    Tracks individual contributions to team pool
    """
    __tablename__ = "team_funding"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # Funding details
    amount: Mapped[float] = mapped_column(Float)
    transaction_signature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Solana transaction
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="completed")  # pending, completed, failed, refunded
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="fundings")
    user: Mapped["User"] = relationship("User")


class TeamPrizeDistribution(Base):
    """
    Team prize distribution record
    Tracks how prizes are split among team members
    """
    __tablename__ = "team_prize_distributions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), index=True)
    winner_id: Mapped[int] = mapped_column(Integer, ForeignKey("winners.id"), index=True)
    
    # Distribution details
    total_prize: Mapped[float] = mapped_column(Float)
    distribution_method: Mapped[str] = mapped_column(String(50), default="proportional")  # proportional, equal, custom
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    distributed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team")
    winner: Mapped["Winner"] = relationship("Winner")
    member_distributions: Mapped[list["TeamMemberPrize"]] = relationship("TeamMemberPrize", back_populates="distribution", cascade="all, delete-orphan")


class TeamMemberPrize(Base):
    """
    Individual team member's prize share
    """
    __tablename__ = "team_member_prizes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    distribution_id: Mapped[int] = mapped_column(Integer, ForeignKey("team_prize_distributions.id"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # Prize share
    amount: Mapped[float] = mapped_column(Float)
    percentage: Mapped[float] = mapped_column(Float)  # Percentage of total prize
    
    # Payment
    transaction_signature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, paid, failed
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    distribution: Mapped["TeamPrizeDistribution"] = relationship("TeamPrizeDistribution", back_populates="member_distributions")
    user: Mapped["User"] = relationship("User")
