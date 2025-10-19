"""
Unit Tests for Phase 2 & 3: Token Economics and Team Collaboration

Tests for TokenEconomicsService, RevenueDistributionService, and TeamService
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from src.token_economics_service import TokenEconomicsService
from src.revenue_distribution_service import RevenueDistributionService
from src.team_service import TeamService
from src.token_config import StakingPeriod


# ===========================
# Token Economics Service Tests
# ===========================

class TestTokenEconomicsService:
    """Tests for token operations"""
    
    @pytest.fixture
    def service(self):
        return TokenEconomicsService()
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None
        assert hasattr(service, 'solana_client')
    
    @pytest.mark.asyncio
    async def test_create_staking_position(self, service):
        """Test creating a staking position"""
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar.return_value = 0.0  # Mock tier total
        
        position = await service.create_staking_position(
            db=mock_db,
            user_id=1,
            amount=1000000.0,
            period=StakingPeriod.NINETY_DAYS,
            estimated_monthly_revenue=10000.0
        )
        
        assert position is not None
        assert position.staked_amount == 1000000.0
        assert position.staking_period_days == 90
        assert position.estimated_rewards > 0


# ===========================
# Revenue Distribution Service Tests
# ===========================

class TestRevenueDistributionService:
    """Tests for revenue distribution"""
    
    @pytest.fixture
    def service(self):
        return RevenueDistributionService()
    
    @pytest.mark.asyncio
    async def test_calculate_monthly_distribution(self, service):
        """Test calculating revenue distribution"""
        mock_db = AsyncMock()
        
        # Mock no active positions
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        
        distribution = await service.calculate_monthly_distribution(
            db=mock_db,
            monthly_revenue=10000.0
        )
        
        assert distribution["monthly_revenue"] == 10000.0
        assert distribution["staking_revenue_percentage"] == 30.0  # 30%
        assert distribution["total_staking_pool"] == 3000.0
        assert "tiers" in distribution
    
    @pytest.mark.asyncio
    async def test_get_tier_statistics(self, service):
        """Test getting tier statistics"""
        mock_db = AsyncMock()
        
        # Mock tier data
        mock_db.execute.return_value.scalar.return_value = 1000000.0
        
        stats = await service.get_tier_statistics(db=mock_db)
        
        assert "tiers" in stats
        assert "total_active_stakers" in stats
        assert "total_tokens_staked" in stats


# ===========================
# Team Service Tests
# ===========================

class TestTeamService:
    """Tests for team collaboration"""
    
    @pytest.fixture
    def service(self):
        return TeamService()
    
    @pytest.mark.asyncio
    async def test_create_team(self, service):
        """Test team creation"""
        mock_db = AsyncMock()
        
        # Mock no existing team with same name
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        team = await service.create_team(
            db=mock_db,
            leader_id=1,
            name="Test Team",
            description="Test Description",
            max_members=5,
            is_public=True
        )
        
        assert team["name"] == "Test Team"
        assert team["leader_id"] == 1
        assert team["max_members"] == 5
        assert "invite_code" in team
    
    @pytest.mark.asyncio
    async def test_invite_code_generation(self, service):
        """Test invite code is unique"""
        code1 = service._generate_invite_code()
        code2 = service._generate_invite_code()
        
        assert len(code1) == 8
        assert len(code2) == 8
        assert code1 != code2  # Should be different
    
    @pytest.mark.asyncio
    async def test_contribute_to_pool(self, service):
        """Test contributing to team pool"""
        mock_db = AsyncMock()
        
        # Mock team exists and user is member
        mock_team = Mock()
        mock_team.id = 1
        mock_team.total_pool = 1000.0
        
        mock_member = Mock()
        mock_member.total_contributed = 500.0
        
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_member
        mock_db.execute.return_value.scalar_one.return_value = mock_team
        
        # Mock _is_team_member
        with patch.object(service, '_is_team_member', return_value=True):
            funding = await service.contribute_to_pool(
                db=mock_db,
                team_id=1,
                user_id=1,
                amount=500.0
            )
        
        assert funding["amount"] == 500.0
    
    @pytest.mark.asyncio
    async def test_send_message(self, service):
        """Test sending team message"""
        mock_db = AsyncMock()
        
        # Mock user is member
        with patch.object(service, '_is_team_member', return_value=True):
            message = await service.send_message(
                db=mock_db,
                team_id=1,
                user_id=1,
                content="Test message",
                message_type="text"
            )
        
        assert message["content"] == "Test message"
        assert message["message_type"] == "text"


# ===========================
# Integration Tests
# ===========================

class TestServicesIntegration:
    """Integration tests for services working together"""
    
    @pytest.mark.asyncio
    async def test_staking_and_revenue_distribution(self):
        """Test staking position creation and revenue distribution"""
        token_service = TokenEconomicsService()
        revenue_service = RevenueDistributionService()
        
        mock_db = AsyncMock()
        
        # Create mock staking position
        mock_db.execute.return_value.scalar.return_value = 1000000.0
        
        # Calculate distribution
        distribution = await revenue_service.calculate_monthly_distribution(
            db=mock_db,
            monthly_revenue=10000.0
        )
        
        assert distribution["total_staking_pool"] > 0
        assert distribution["staking_revenue_percentage"] == 30.0
    
    @pytest.mark.asyncio
    async def test_team_workflow(self):
        """Test complete team workflow"""
        service = TeamService()
        mock_db = AsyncMock()
        
        # 1. Create team
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        team = await service.create_team(
            db=mock_db,
            leader_id=1,
            name="Test Team",
            description="Test",
            max_members=5,
            is_public=True
        )
        
        assert "invite_code" in team
        
        # 2. Mock contribution
        with patch.object(service, '_is_team_member', return_value=True):
            mock_team = Mock()
            mock_team.total_pool = 0.0
            mock_member = Mock()
            mock_member.total_contributed = 0.0
            
            mock_db.execute.return_value.scalar_one.return_value = mock_team
            mock_db.execute.return_value.scalar_one_or_none.return_value = mock_member
            
            funding = await service.contribute_to_pool(
                db=mock_db,
                team_id=team["id"],
                user_id=1,
                amount=1000.0
            )
            
            assert funding["amount"] == 1000.0


# ===========================
# Calculation Tests
# ===========================

class TestTokenCalculations:
    """Test token calculation functions"""
    
    def test_discount_tiers(self):
        """Test discount tier calculations"""
        from src.token_config import get_discount_for_balance
        
        # Test each tier
        assert get_discount_for_balance(500000) == 0.0  # Below threshold
        assert get_discount_for_balance(1000000) == 0.10  # 10%
        assert get_discount_for_balance(10000000) == 0.25  # 25%
        assert get_discount_for_balance(100000000) == 0.50  # 50%
        assert get_discount_for_balance(200000000) == 0.50  # Max tier
    
    def test_staking_share_calculation(self):
        """Test revenue-based staking calculations"""
        from src.token_config import calculate_staking_share, StakingPeriod
        
        result = calculate_staking_share(
            amount=1000000,
            period=StakingPeriod.NINETY_DAYS,
            tier_total_staked=10000000,
            monthly_staking_pool=3000
        )
        
        assert result["staked_amount"] == 1000000
        assert result["staking_days"] == 90
        assert result["tier_allocation_percentage"] == 50.0  # 90-day tier
        assert result["estimated_monthly_rewards"] > 0
        assert "note" in result


# ===========================
# Error Handling Tests
# ===========================

class TestServiceErrorHandling:
    """Test error handling in services"""
    
    @pytest.mark.asyncio
    async def test_create_team_duplicate_name(self):
        """Test creating team with duplicate name"""
        service = TeamService()
        mock_db = AsyncMock()
        
        # Mock existing team
        mock_db.execute.return_value.scalar_one_or_none.return_value = Mock()
        
        with pytest.raises(ValueError, match="already taken"):
            await service.create_team(
                db=mock_db,
                leader_id=1,
                name="Duplicate Team"
            )
    
    @pytest.mark.asyncio
    async def test_leave_team_as_leader(self):
        """Test leader cannot leave team"""
        service = TeamService()
        mock_db = AsyncMock()
        
        # Mock member exists and is leader
        mock_member = Mock()
        mock_member.team_id = 1
        mock_member.user_id = 1
        
        mock_team = Mock()
        mock_team.id = 1
        mock_team.leader_id = 1
        
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_member
        mock_db.execute.return_value.scalar_one.return_value = mock_team
        
        with pytest.raises(ValueError, match="leader cannot leave"):
            await service.leave_team(
                db=mock_db,
                team_id=1,
                user_id=1
            )


# ===========================
# Run Tests
# ===========================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

