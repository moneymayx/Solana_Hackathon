# Billions Bounty Package
"""
Main package for Billions Bounty backend services.
This __init__.py provides exports for backward compatibility after organizing files into subdirectories.
"""

# Core infrastructure (always at root level)
from .base import Base
from .database import (
    engine,
    AsyncSessionLocal,
    get_db,
    create_tables
)
from .models import *  # All database models
from .repositories import (
    UserRepository,
    ConversationRepository,
    AttackAttemptRepository,
    PrizePoolRepository,
    SecurityEventRepository,
    BlacklistedPhraseRepository
)

# Services (now in services/ subdirectory)
from .services.ai_agent import BillionsAgent
from .services.ai_decision_service import ai_decision_service
from .services.ai_decision_integration import ai_decision_integration
from .services.semantic_decision_analyzer import SemanticDecisionAnalyzer
from .services.auth_service import AuthService
from .services.email_service import EmailService
from .services.encryption_service import EncryptionService
from .services.free_question_service import FreeQuestionService
from .services.gdpr_compliance import GDPRComplianceService, ConsentType
from .services.kyc_service import KYCService
from .services.moonpay_service import MoonpayService
from .services.payment_flow_service import payment_flow_service
from .services.payment_service_with_discounts import PaymentServiceWithDiscounts
from .services.referral_service import ReferralService
from .services.regulatory_compliance import regulatory_compliance_service
from .services.smart_contract_service import smart_contract_service, SmartContractService
from .services.solana_service import solana_service
from .services.wallet_service import WalletConnectSolanaService, PaymentOrchestrator
from .services.winner_tracking_service import winner_tracking_service

# Context management services
from .services.semantic_search_service import SemanticSearchService
from .services.pattern_detector_service import PatternDetectorService
from .services.context_builder_service import ContextBuilderService

# Token economics services
from .services.token_economics_service import TokenEconomicsService
from .services.revenue_distribution_service import RevenueDistributionService
from .services.team_service import TeamService, team_service

# Rate limiting
from .services.rate_limiter import RateLimiter, SecurityMonitor
from .services.advanced_rate_limiter import rate_limiter, rate_limit, RateLimitType

# Personality
from .services.personality import BillionsPersonality
from .services.personality_public import BillionsPersonalityPublic

# Background tasks
from .services.celery_app import celery_app
from .services.celery_tasks import *

# Configuration (now in config/ subdirectory)
from .config.token_config import (
    TOKEN_MINT_ADDRESS,
    TOKEN_SYMBOL,
    TOKEN_DECIMALS,
    TOKEN_TOTAL_SUPPLY,
    BASE_QUERY_COST,
    DISCOUNT_TIERS,
    STAKING_REVENUE_PERCENTAGE,
    BUYBACK_PERCENTAGE,
    StakingPeriod,
    get_discount_for_balance,
    get_tier_info,
    calculate_staking_share,
    TIER_ALLOCATIONS
)
from .config.simulation_logger import SimulationLogger
from .config.simulation_models import *

__all__ = [
    # Core
    'Base',
    'engine',
    'AsyncSessionLocal',
    'get_db',
    'create_tables',
    
    # Repositories
    'UserRepository',
    'ConversationRepository',
    'AttackAttemptRepository',
    'PrizePoolRepository',
    'SecurityEventRepository',
    'BlacklistedPhraseRepository',
    
    # Services
    'BillionsAgent',
    'ai_decision_service',
    'ai_decision_integration',
    'SemanticDecisionAnalyzer',
    'AuthService',
    'EmailService',
    'EncryptionService',
    'FreeQuestionService',
    'GDPRComplianceService',
    'ConsentType',
    'KYCService',
    'MoonpayService',
    'payment_flow_service',
    'PaymentServiceWithDiscounts',
    'ReferralService',
    'regulatory_compliance_service',
    'smart_contract_service',
    'SmartContractService',
    'solana_service',
    'WalletConnectSolanaService',
    'PaymentOrchestrator',
    'winner_tracking_service',
    'SemanticSearchService',
    'PatternDetectorService',
    'ContextBuilderService',
    'TokenEconomicsService',
    'RevenueDistributionService',
    'TeamService',
    'team_service',
    'RateLimiter',
    'SecurityMonitor',
    'rate_limiter',
    'rate_limit',
    'RateLimitType',
    'BillionsPersonality',
    'BillionsPersonalityPublic',
    'celery_app',
    
    # Config
    'TOKEN_MINT_ADDRESS',
    'TOKEN_SYMBOL',
    'TOKEN_DECIMALS',
    'TOKEN_TOTAL_SUPPLY',
    'BASE_QUERY_COST',
    'DISCOUNT_TIERS',
    'STAKING_REVENUE_PERCENTAGE',
    'BUYBACK_PERCENTAGE',
    'StakingPeriod',
    'get_discount_for_balance',
    'get_tier_info',
    'calculate_staking_share',
    'TIER_ALLOCATIONS',
    'SimulationLogger',
]
