import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from .models import Winner, ConnectedWallet, WalletFundingSource, User, Transaction
from .solana_service import solana_service

class WinnerTrackingService:
    """Service for tracking winners and preventing them from creating new accounts"""
    
    def __init__(self):
        self.is_active = False  # Will be activated after first jackpot win
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
