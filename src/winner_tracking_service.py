import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from .models import Winner, ConnectedWallet, WalletFundingSource, User, Transaction, SecurityEvent, Conversation
from .solana_service import solana_service

class SybilDetectionService:
    """Advanced sybil detection system using multiple correlation methods"""
    
    def __init__(self):
        self.suspicious_thresholds = {
            'ip_correlation': 0.7,  # 70% of wallets from same IP
            'behavioral_similarity': 0.8,  # 80% similar message patterns
            'timing_patterns': 0.9,  # 90% similar timing patterns
            'rapid_creation': 5,  # 5 wallets in 1 hour
            'funding_correlation': 0.6,  # 60% shared funding sources
            'device_fingerprint': 0.85  # 85% similar device characteristics
        }
        
        # Behavioral pattern storage
        self.behavioral_patterns = {}
        self.ip_correlations = {}
        self.timing_patterns = {}
    
    async def analyze_user_behavior(self, user_id: int, message: str, ip_address: str, 
                                  user_agent: str, session: AsyncSession) -> Dict[str, Any]:
        """Analyze user behavior for sybil patterns"""
        
        # 1. IP-based correlation analysis
        ip_analysis = await self._analyze_ip_correlation(user_id, ip_address, session)
        
        # 2. Behavioral pattern detection
        behavior_analysis = await self._analyze_behavioral_patterns(user_id, message, session)
        
        # 3. Timing pattern analysis
        timing_analysis = await self._analyze_timing_patterns(user_id, session)
        
        # 4. Device fingerprinting
        device_analysis = await self._analyze_device_fingerprint(user_id, user_agent, session)
        
        # 5. Calculate overall sybil score
        sybil_score = self._calculate_sybil_score({
            'ip_correlation': ip_analysis['correlation_score'],
            'behavioral_similarity': behavior_analysis['similarity_score'],
            'timing_patterns': timing_analysis['pattern_score'],
            'device_fingerprint': device_analysis['fingerprint_score']
        })
        
        # 6. Determine if user is suspicious
        is_suspicious = sybil_score >= 0.7
        
        if is_suspicious:
            await self._log_sybil_detection(session, user_id, sybil_score, {
                'ip_analysis': ip_analysis,
                'behavior_analysis': behavior_analysis,
                'timing_analysis': timing_analysis,
                'device_analysis': device_analysis
            })
        
        return {
            'sybil_score': sybil_score,
            'is_suspicious': is_suspicious,
            'risk_level': self._get_risk_level(sybil_score),
            'analysis_details': {
                'ip_correlation': ip_analysis,
                'behavioral_patterns': behavior_analysis,
                'timing_patterns': timing_analysis,
                'device_fingerprint': device_analysis
            }
        }
    
    async def _analyze_ip_correlation(self, user_id: int, ip_address: str, 
                                    session: AsyncSession) -> Dict[str, Any]:
        """Analyze IP-based correlation for sybil detection"""
        
        # Get all users from same IP in last 24 hours
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        
        same_ip_users = await session.execute(
            select(User.id, User.session_id, User.created_at)
            .where(
                and_(
                    User.ip_address == ip_address,
                    User.created_at >= twenty_four_hours_ago
                )
            )
        )
        
        ip_users = same_ip_users.fetchall()
        correlation_score = len(ip_users) / 10.0  # Normalize to 0-1 scale
        
        # Check for rapid creation pattern
        if len(ip_users) >= self.suspicious_thresholds['rapid_creation']:
            correlation_score = 1.0  # Maximum suspicion
        
        return {
            'ip_address': ip_address,
            'users_from_same_ip': len(ip_users),
            'correlation_score': min(correlation_score, 1.0),
            'is_rapid_creation': len(ip_users) >= self.suspicious_thresholds['rapid_creation'],
            'user_ids': [user.id for user in ip_users]
        }
    
    async def _analyze_behavioral_patterns(self, user_id: int, message: str, 
                                         session: AsyncSession) -> Dict[str, Any]:
        """Analyze behavioral patterns for sybil detection"""
        
        # Get user's recent messages
        recent_messages = await session.execute(
            select(Conversation.content)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.message_type == "user",
                    Conversation.timestamp >= datetime.utcnow() - timedelta(hours=24)
                )
            )
            .order_by(Conversation.timestamp.desc())
            .limit(10)
        )
        
        user_messages = [msg.content for msg in recent_messages.scalars().all()]
        
        # Calculate message patterns
        message_length_avg = sum(len(msg) for msg in user_messages) / len(user_messages) if user_messages else 0
        message_complexity = self._calculate_message_complexity(user_messages)
        keyword_usage = self._analyze_keyword_usage(user_messages)
        
        # Compare with other users from same IP
        ip_users = await self._get_users_from_same_ip(user_id, session)
        similarity_scores = []
        
        for other_user_id in ip_users:
            if other_user_id != user_id:
                other_messages = await self._get_user_messages(other_user_id, session)
                similarity = self._calculate_message_similarity(user_messages, other_messages)
                similarity_scores.append(similarity)
        
        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
        
        return {
            'message_count': len(user_messages),
            'avg_message_length': message_length_avg,
            'message_complexity': message_complexity,
            'keyword_usage': keyword_usage,
            'similarity_score': avg_similarity,
            'is_similar_to_others': avg_similarity >= self.suspicious_thresholds['behavioral_similarity']
        }
    
    async def _analyze_timing_patterns(self, user_id: int, session: AsyncSession) -> Dict[str, Any]:
        """Analyze timing patterns for sybil detection"""
        
        # Get user's activity timestamps
        user_activity = await session.execute(
            select(Conversation.timestamp)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.timestamp >= datetime.utcnow() - timedelta(hours=24)
                )
            )
            .order_by(Conversation.timestamp)
        )
        
        timestamps = [activity.timestamp for activity in user_activity.scalars().all()]
        
        if len(timestamps) < 2:
            return {'pattern_score': 0.0, 'is_regular_pattern': False}
        
        # Calculate time intervals between messages
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        # Check for regular patterns (suspicious for sybil)
        interval_variance = self._calculate_variance(intervals)
        is_regular_pattern = interval_variance < 60  # Less than 1 minute variance
        
        # Check for burst patterns (multiple messages in short time)
        burst_count = sum(1 for interval in intervals if interval < 10)  # Less than 10 seconds
        is_burst_pattern = burst_count >= 3
        
        pattern_score = 0.0
        if is_regular_pattern:
            pattern_score += 0.5
        if is_burst_pattern:
            pattern_score += 0.5
        
        return {
            'message_count': len(timestamps),
            'avg_interval': sum(intervals) / len(intervals) if intervals else 0,
            'interval_variance': interval_variance,
            'pattern_score': pattern_score,
            'is_regular_pattern': is_regular_pattern,
            'is_burst_pattern': is_burst_pattern
        }
    
    async def _analyze_device_fingerprint(self, user_id: int, user_agent: str, 
                                        session: AsyncSession) -> Dict[str, Any]:
        """Analyze device fingerprint for sybil detection"""
        
        # Extract device characteristics from user agent
        device_info = self._parse_user_agent(user_agent)
        
        # Get other users with similar device characteristics
        similar_devices = await session.execute(
            select(User.id, User.user_agent)
            .where(
                and_(
                    User.id != user_id,
                    User.created_at >= datetime.utcnow() - timedelta(hours=24)
                )
            )
        )
        
        fingerprint_scores = []
        for other_user in similar_devices.fetchall():
            if other_user.user_agent:
                other_device = self._parse_user_agent(other_user.user_agent)
                similarity = self._calculate_device_similarity(device_info, other_device)
                fingerprint_scores.append(similarity)
        
        avg_fingerprint_similarity = sum(fingerprint_scores) / len(fingerprint_scores) if fingerprint_scores else 0
        
        return {
            'device_info': device_info,
            'fingerprint_score': avg_fingerprint_similarity,
            'is_similar_device': avg_fingerprint_similarity >= self.suspicious_thresholds['device_fingerprint']
        }
    
    def _calculate_sybil_score(self, analysis_scores: Dict[str, float]) -> float:
        """Calculate overall sybil score from individual analysis scores"""
        weights = {
            'ip_correlation': 0.3,
            'behavioral_similarity': 0.25,
            'timing_patterns': 0.2,
            'device_fingerprint': 0.25
        }
        
        weighted_score = sum(
            analysis_scores.get(metric, 0) * weight 
            for metric, weight in weights.items()
        )
        
        return min(weighted_score, 1.0)
    
    def _get_risk_level(self, sybil_score: float) -> str:
        """Get risk level based on sybil score"""
        if sybil_score >= 0.8:
            return "critical"
        elif sybil_score >= 0.6:
            return "high"
        elif sybil_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    async def _log_sybil_detection(self, session: AsyncSession, user_id: int, 
                                 sybil_score: float, analysis_details: Dict[str, Any]) -> None:
        """Log sybil detection event"""
        security_event = SecurityEvent(
            event_type="sybil_detection",
            severity=self._get_risk_level(sybil_score),
            description=f"Sybil detection triggered for user {user_id} with score {sybil_score:.2f}",
            additional_data=json.dumps(analysis_details)
        )
        session.add(security_event)
        await session.commit()
    
    # Helper methods
    def _calculate_message_complexity(self, messages: List[str]) -> float:
        """Calculate message complexity score"""
        if not messages:
            return 0.0
        
        total_complexity = 0
        for message in messages:
            # Simple complexity: length + unique words + special characters
            complexity = len(message) + len(set(message.lower().split())) + len([c for c in message if not c.isalnum()])
            total_complexity += complexity
        
        return total_complexity / len(messages)
    
    def _analyze_keyword_usage(self, messages: List[str]) -> Dict[str, int]:
        """Analyze keyword usage patterns"""
        keywords = {}
        for message in messages:
            words = message.lower().split()
            for word in words:
                keywords[word] = keywords.get(word, 0) + 1
        return keywords
    
    def _calculate_message_similarity(self, messages1: List[str], messages2: List[str]) -> float:
        """Calculate similarity between two sets of messages"""
        if not messages1 or not messages2:
            return 0.0
        
        # Simple similarity based on common words
        words1 = set(' '.join(messages1).lower().split())
        words2 = set(' '.join(messages2).lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _parse_user_agent(self, user_agent: str) -> Dict[str, str]:
        """Parse user agent string to extract device information"""
        # Simple user agent parsing
        device_info = {
            'browser': 'unknown',
            'os': 'unknown',
            'device': 'unknown'
        }
        
        user_agent_lower = user_agent.lower()
        
        # Browser detection
        if 'chrome' in user_agent_lower:
            device_info['browser'] = 'chrome'
        elif 'firefox' in user_agent_lower:
            device_info['browser'] = 'firefox'
        elif 'safari' in user_agent_lower:
            device_info['browser'] = 'safari'
        
        # OS detection
        if 'windows' in user_agent_lower:
            device_info['os'] = 'windows'
        elif 'mac' in user_agent_lower:
            device_info['os'] = 'mac'
        elif 'linux' in user_agent_lower:
            device_info['os'] = 'linux'
        
        # Device type detection
        if 'mobile' in user_agent_lower:
            device_info['device'] = 'mobile'
        elif 'tablet' in user_agent_lower:
            device_info['device'] = 'tablet'
        else:
            device_info['device'] = 'desktop'
        
        return device_info
    
    def _calculate_device_similarity(self, device1: Dict[str, str], device2: Dict[str, str]) -> float:
        """Calculate similarity between two device fingerprints"""
        similarities = []
        
        for key in device1:
            if device1[key] == device2.get(key, ''):
                similarities.append(1.0)
            else:
                similarities.append(0.0)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    async def _get_users_from_same_ip(self, user_id: int, session: AsyncSession) -> List[int]:
        """Get other users from the same IP address"""
        # Get current user's IP
        current_user = await session.execute(
            select(User.ip_address)
            .where(User.id == user_id)
        )
        ip_address = current_user.scalar()
        
        if not ip_address:
            return []
        
        # Get other users from same IP
        other_users = await session.execute(
            select(User.id)
            .where(
                and_(
                    User.ip_address == ip_address,
                    User.id != user_id
                )
            )
        )
        
        return [user.id for user in other_users.scalars().all()]
    
    async def _get_user_messages(self, user_id: int, session: AsyncSession) -> List[str]:
        """Get recent messages for a user"""
        messages = await session.execute(
            select(Conversation.content)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.message_type == "user",
                    Conversation.timestamp >= datetime.utcnow() - timedelta(hours=24)
                )
            )
            .order_by(Conversation.timestamp.desc())
            .limit(10)
        )
        
        return [msg.content for msg in messages.scalars().all()]


class WinnerTrackingService:
    """Service for tracking winners and preventing them from creating new accounts"""
    
    def __init__(self):
        self.is_active = False  # Will be activated after first jackpot win
        self.sybil_detector = SybilDetectionService()  # Add sybil detection
        # Exchange addresses are user-specific and not publicly available
        # We'll use pattern-based detection instead of hardcoded addresses
        self.known_exchanges = {
            # Only include addresses that are confirmed to be exchange-wide (not user-specific)
            "binance": [
                "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Binance hot wallet
                "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9",  # Binance cold wallet
            ]
            # Other exchanges use user-specific addresses, so we don't hardcode them
        }
    
    def _is_exchange_address(self, address: str) -> bool:
        """Check if an address is a known exchange address"""
        all_exchange_addresses = self._get_all_exchange_addresses()
        return address in all_exchange_addresses
    
    def _get_all_exchange_addresses(self) -> List[str]:
        """Get all known exchange addresses"""
        all_addresses = []
        for exchange_addresses in self.known_exchanges.values():
            all_addresses.extend(exchange_addresses)
        return all_addresses
    
    def add_exchange_addresses(self, exchange_name: str, addresses: List[str]) -> None:
        """Add or update exchange addresses"""
        if exchange_name not in self.known_exchanges:
            self.known_exchanges[exchange_name] = []
        
        # Add new addresses (avoid duplicates)
        for address in addresses:
            if address not in self.known_exchanges[exchange_name]:
                self.known_exchanges[exchange_name].append(address)
        
        print(f"✅ Added {len(addresses)} addresses for {exchange_name}")
    
    def remove_exchange_addresses(self, exchange_name: str, addresses: List[str]) -> None:
        """Remove specific addresses from an exchange"""
        if exchange_name in self.known_exchanges:
            for address in addresses:
                if address in self.known_exchanges[exchange_name]:
                    self.known_exchanges[exchange_name].remove(address)
            print(f"✅ Removed {len(addresses)} addresses from {exchange_name}")
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """Get information about all configured exchanges"""
        return {
            "exchanges": list(self.known_exchanges.keys()),
            "total_addresses": sum(len(addresses) for addresses in self.known_exchanges.values()),
            "addresses_per_exchange": {
                exchange: len(addresses) for exchange, addresses in self.known_exchanges.items()
            }
        }
    
    async def activate_winner_tracking(self, session: AsyncSession) -> None:
        """Activate winner tracking after first jackpot win"""
        self.is_active = True
        print("🎯 Winner tracking system activated!")
    
    async def record_winner(self, session: AsyncSession, user_id: int, wallet_address: str, 
                          prize_amount: float, token: str, transaction_hash: str) -> Winner:
        """Record a new winner and start tracking their wallet connections"""
        # Create winner record
        winner = Winner(
            user_id=user_id,
            wallet_address=wallet_address,
            prize_amount=prize_amount,
            token=token,
            transaction_hash=transaction_hash
        )
        session.add(winner)
        await session.commit()
        await session.refresh(winner)
        
        # Activate tracking if this is the first winner
        if not self.is_active:
            await self.activate_winner_tracking(session)
        
        # Start tracking wallet connections
        await self._track_winner_connections(session, winner)
        
        print(f"🏆 Winner recorded: {wallet_address} won {prize_amount} {token}")
        return winner
    
    async def _track_winner_connections(self, session: AsyncSession, winner: Winner) -> None:
        """Track all wallets connected to a winner"""
        print(f"🔍 Tracking connections for winner: {winner.wallet_address}")
        
        # 1. Track direct transfers from winner's wallet
        await self._track_direct_transfers(session, winner)
        
        # 2. Track wallets that received funds from the same funding source
        await self._track_funding_source_connections(session, winner)
        
        # 3. Track wallets that sent funds to the winner (potential accomplices)
        await self._track_sender_connections(session, winner)
    
    async def _track_direct_transfers(self, session: AsyncSession, winner: Winner) -> None:
        """Track wallets that received direct transfers from winner"""
        try:
            # Get recent transactions from winner's wallet
            # This would require Solana RPC calls to get transaction history
            # For now, we'll implement a placeholder that can be enhanced
            
            # In a real implementation, you would:
            # 1. Query Solana RPC for recent transactions from winner's wallet
            # 2. Identify recipient addresses
            # 3. Add them to connected_wallets table
            
            print(f"📤 Tracking direct transfers from {winner.wallet_address}")
            # Placeholder for actual Solana transaction tracking
            
        except Exception as e:
            print(f"Error tracking direct transfers: {e}")
    
    async def _track_funding_source_connections(self, session: AsyncSession, winner: Winner) -> None:
        """Track wallets funded by the same source as the winner"""
        try:
            # Get winner's funding sources
            winner_funding = await session.execute(
                select(WalletFundingSource)
                .where(WalletFundingSource.wallet_address == winner.wallet_address)
            )
            winner_sources = winner_funding.scalars().all()
            
            for source in winner_sources:
                # Skip if funding source is a known exchange address
                if self._is_exchange_address(source.funding_source):
                    continue
                
                # Find other wallets funded by the same source
                other_wallets = await session.execute(
                    select(WalletFundingSource)
                    .where(
                        and_(
                            WalletFundingSource.funding_source == source.funding_source,
                            WalletFundingSource.wallet_address != winner.wallet_address
                        )
                    )
                )
                
                for other_wallet in other_wallets.scalars().all():
                    # Add as connected wallet
                    connected = ConnectedWallet(
                        winner_id=winner.id,
                        wallet_address=other_wallet.wallet_address,
                        connection_type="funding_source",
                        connection_details=json.dumps({
                            "shared_funding_source": source.funding_source,
                            "discovery_method": "funding_source_analysis"
                        })
                    )
                    session.add(connected)
            
            await session.commit()
            print(f"🔗 Tracked funding source connections for {winner.wallet_address}")
            
        except Exception as e:
            print(f"Error tracking funding source connections: {e}")
    
    async def _track_sender_connections(self, session: AsyncSession, winner: Winner) -> None:
        """Track wallets that sent funds to the winner (potential accomplices)"""
        try:
            # This would require analyzing incoming transactions to winner's wallet
            # For now, we'll implement a placeholder
            
            print(f"📥 Tracking sender connections for {winner.wallet_address}")
            # Placeholder for actual sender tracking
            
        except Exception as e:
            print(f"Error tracking sender connections: {e}")
    
    async def is_wallet_blacklisted(self, session: AsyncSession, wallet_address: str) -> Dict[str, Any]:
        """Check if a wallet is blacklisted due to winner connections"""
        if not self.is_active:
            return {"blacklisted": False, "reason": "Winner tracking not active"}
        
        # Check if wallet is a direct winner
        winner_check = await session.execute(
            select(Winner)
            .where(Winner.wallet_address == wallet_address)
        )
        if winner_check.scalar_one_or_none():
            return {
                "blacklisted": True,
                "reason": "Direct winner",
                "type": "winner"
            }
        
        # Check if wallet is connected to a winner
        connected_check = await session.execute(
            select(ConnectedWallet)
            .where(
                and_(
                    ConnectedWallet.wallet_address == wallet_address,
                    ConnectedWallet.is_blacklisted == True
                )
            )
        )
        connected_wallet = connected_check.scalar_one_or_none()
        
        if connected_wallet:
            return {
                "blacklisted": True,
                "reason": f"Connected to winner via {connected_wallet.connection_type}",
                "type": "connected",
                "connection_details": connected_wallet.connection_details
            }
        
        # Check if wallet shares funding sources with winners
        funding_blacklist = await self._check_funding_source_blacklist(session, wallet_address)
        if funding_blacklist["blacklisted"]:
            return funding_blacklist
        
        return {"blacklisted": False, "reason": "No winner connections found"}
    
    async def _check_funding_source_blacklist(self, session: AsyncSession, wallet_address: str) -> Dict[str, Any]:
        """Check if wallet shares funding sources with any winners"""
        try:
            # Get wallet's funding sources
            wallet_sources = await session.execute(
                select(WalletFundingSource)
                .where(WalletFundingSource.wallet_address == wallet_address)
            )
            wallet_funding = wallet_sources.scalars().all()
            
            for source in wallet_funding:
                # Skip if funding source is a known exchange address
                if self._is_exchange_address(source.funding_source):
                    continue
                
                # Check if any winner used this funding source
                winner_with_same_source = await session.execute(
                    select(Winner)
                    .join(WalletFundingSource, Winner.wallet_address == WalletFundingSource.wallet_address)
                    .where(WalletFundingSource.funding_source == source.funding_source)
                )
                
                if winner_with_same_source.scalar_one_or_none():
                    return {
                        "blacklisted": True,
                        "reason": f"Shares funding source with winner: {source.funding_source}",
                        "type": "shared_funding",
                        "funding_source": source.funding_source
                    }
            
            return {"blacklisted": False, "reason": "No shared funding sources with winners"}
            
        except Exception as e:
            print(f"Error checking funding source blacklist: {e}")
            return {"blacklisted": False, "reason": "Error in funding source check"}
    
    async def record_wallet_funding(self, session: AsyncSession, wallet_address: str, 
                                  funding_source: str, amount: float) -> None:
        """Record wallet funding source for future blacklist checks"""
        try:
            # Check if funding source already exists
            existing = await session.execute(
                select(WalletFundingSource)
                .where(
                    and_(
                        WalletFundingSource.wallet_address == wallet_address,
                        WalletFundingSource.funding_source == funding_source
                    )
                )
            )
            funding_record = existing.scalar_one_or_none()
            
            if funding_record:
                # Update existing record
                funding_record.last_seen = datetime.utcnow()
                funding_record.total_funding_amount += amount
                funding_record.transaction_count += 1
            else:
                # Create new record
                funding_record = WalletFundingSource(
                    wallet_address=wallet_address,
                    funding_source=funding_source,
                    total_funding_amount=amount,
                    transaction_count=1
                )
                session.add(funding_record)
            
            await session.commit()
            print(f"💰 Recorded funding: {wallet_address} <- {funding_source} ({amount})")
            
        except Exception as e:
            print(f"Error recording wallet funding: {e}")
    
    async def get_winner_statistics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get statistics about winners and blacklisted wallets"""
        # Total winners
        total_winners = await session.execute(select(func.count(Winner.id)))
        winner_count = total_winners.scalar()
        
        # Total blacklisted wallets
        total_blacklisted = await session.execute(
            select(func.count(ConnectedWallet.id))
            .where(ConnectedWallet.is_blacklisted == True)
        )
        blacklisted_count = total_blacklisted.scalar()
        
        # Recent winners (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_winners = await session.execute(
            select(func.count(Winner.id))
            .where(Winner.won_at >= thirty_days_ago)
        )
        recent_winner_count = recent_winners.scalar()
        
        # Total prize money distributed
        total_prizes = await session.execute(select(func.sum(Winner.prize_amount)))
        total_prize_amount = total_prizes.scalar() or 0
        
        return {
            "total_winners": winner_count,
            "total_blacklisted_wallets": blacklisted_count,
            "recent_winners_30d": recent_winner_count,
            "total_prize_money": total_prize_amount,
            "tracking_active": self.is_active
        }
    
    async def get_winner_list(self, session: AsyncSession, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of all winners with their details"""
        winners = await session.execute(
            select(Winner)
            .order_by(Winner.won_at.desc())
            .limit(limit)
        )
        
        winner_list = []
        for winner in winners.scalars().all():
            # Get connected wallets count
            connected_count = await session.execute(
                select(func.count(ConnectedWallet.id))
                .where(ConnectedWallet.winner_id == winner.id)
            )
            
            winner_list.append({
                "id": winner.id,
                "wallet_address": winner.wallet_address,
                "prize_amount": winner.prize_amount,
                "token": winner.token,
                "transaction_hash": winner.transaction_hash,
                "won_at": winner.won_at.isoformat(),
                "connected_wallets": connected_count.scalar(),
                "is_active": winner.is_active
            })
        
        return winner_list

# Global instance
winner_tracking_service = WinnerTrackingService()
