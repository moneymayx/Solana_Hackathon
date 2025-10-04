"""
Database Migration Script - Add encryption support to existing data
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.database import AsyncSessionLocal, create_tables
from src.encryption_service import EncryptionService
from src.models import User, Conversation, AttackAttempt, SecurityEvent
import logging

logger = logging.getLogger(__name__)

class DatabaseEncryptionMigration:
    """Handle migration of existing data to encrypted format"""
    
    def __init__(self):
        self.encryption_service = EncryptionService()
        self.sensitive_fields = {
            'User': ['email', 'wallet_address', 'wallet_signature', 'session_id'],
            'Conversation': ['user_message', 'ai_response', 'session_id'],
            'AttackAttempt': ['user_message', 'ai_response', 'ip_address', 'user_agent', 'session_id'],
            'SecurityEvent': ['description', 'ip_address', 'user_agent', 'session_id', 'additional_data']
        }
    
    async def migrate_all_tables(self):
        """Migrate all tables to encrypted format"""
        logger.info("Starting database encryption migration...")
        
        try:
            # Create tables if they don't exist
            await create_tables()
            
            # Migrate each table
            await self._migrate_users()
            await self._migrate_conversations()
            await self._migrate_attack_attempts()
            await self._migrate_security_events()
            
            logger.info("Database encryption migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
    
    async def _migrate_users(self):
        """Migrate user data to encrypted format"""
        logger.info("Migrating users table...")
        
        async with AsyncSessionLocal() as session:
            # Get all users
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            migrated_count = 0
            for user in users:
                try:
                    # Prepare data for encryption
                    user_data = {
                        'email': user.email,
                        'wallet_address': user.wallet_address,
                        'wallet_signature': user.wallet_signature,
                        'session_id': user.session_id
                    }
                    
                    # Encrypt sensitive fields
                    encrypted_data = self.encryption_service.encrypt_sensitive_fields(
                        user_data, self.sensitive_fields['User']
                    )
                    
                    # Update user record
                    await session.execute(
                        update(User)
                        .where(User.id == user.id)
                        .values(
                            email=encrypted_data.get('email'),
                            wallet_address=encrypted_data.get('wallet_address'),
                            wallet_signature=encrypted_data.get('wallet_signature'),
                            session_id=encrypted_data.get('session_id')
                        )
                    )
                    
                    migrated_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to migrate user {user.id}: {e}")
                    continue
            
            await session.commit()
            logger.info(f"Migrated {migrated_count} users")
    
    async def _migrate_conversations(self):
        """Migrate conversation data to encrypted format"""
        logger.info("Migrating conversations table...")
        
        async with AsyncSessionLocal() as session:
            # Get all conversations
            result = await session.execute(select(Conversation))
            conversations = result.scalars().all()
            
            migrated_count = 0
            for conv in conversations:
                try:
                    # Prepare data for encryption
                    conv_data = {
                        'user_message': conv.user_message,
                        'ai_response': conv.ai_response,
                        'session_id': conv.session_id
                    }
                    
                    # Encrypt sensitive fields
                    encrypted_data = self.encryption_service.encrypt_sensitive_fields(
                        conv_data, self.sensitive_fields['Conversation']
                    )
                    
                    # Update conversation record
                    await session.execute(
                        update(Conversation)
                        .where(Conversation.id == conv.id)
                        .values(
                            user_message=encrypted_data.get('user_message'),
                            ai_response=encrypted_data.get('ai_response'),
                            session_id=encrypted_data.get('session_id')
                        )
                    )
                    
                    migrated_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to migrate conversation {conv.id}: {e}")
                    continue
            
            await session.commit()
            logger.info(f"Migrated {migrated_count} conversations")
    
    async def _migrate_attack_attempts(self):
        """Migrate attack attempt data to encrypted format"""
        logger.info("Migrating attack attempts table...")
        
        async with AsyncSessionLocal() as session:
            # Get all attack attempts
            result = await session.execute(select(AttackAttempt))
            attempts = result.scalars().all()
            
            migrated_count = 0
            for attempt in attempts:
                try:
                    # Prepare data for encryption
                    attempt_data = {
                        'user_message': attempt.user_message,
                        'ai_response': attempt.ai_response,
                        'ip_address': attempt.ip_address,
                        'user_agent': attempt.user_agent,
                        'session_id': attempt.session_id
                    }
                    
                    # Encrypt sensitive fields
                    encrypted_data = self.encryption_service.encrypt_sensitive_fields(
                        attempt_data, self.sensitive_fields['AttackAttempt']
                    )
                    
                    # Update attack attempt record
                    await session.execute(
                        update(AttackAttempt)
                        .where(AttackAttempt.id == attempt.id)
                        .values(
                            user_message=encrypted_data.get('user_message'),
                            ai_response=encrypted_data.get('ai_response'),
                            ip_address=encrypted_data.get('ip_address'),
                            user_agent=encrypted_data.get('user_agent'),
                            session_id=encrypted_data.get('session_id')
                        )
                    )
                    
                    migrated_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to migrate attack attempt {attempt.id}: {e}")
                    continue
            
            await session.commit()
            logger.info(f"Migrated {migrated_count} attack attempts")
    
    async def _migrate_security_events(self):
        """Migrate security event data to encrypted format"""
        logger.info("Migrating security events table...")
        
        async with AsyncSessionLocal() as session:
            # Get all security events
            result = await session.execute(select(SecurityEvent))
            events = result.scalars().all()
            
            migrated_count = 0
            for event in events:
                try:
                    # Prepare data for encryption
                    event_data = {
                        'description': event.description,
                        'ip_address': event.ip_address,
                        'user_agent': event.user_agent,
                        'session_id': event.session_id,
                        'additional_data': event.additional_data
                    }
                    
                    # Encrypt sensitive fields
                    encrypted_data = self.encryption_service.encrypt_sensitive_fields(
                        event_data, self.sensitive_fields['SecurityEvent']
                    )
                    
                    # Update security event record
                    await session.execute(
                        update(SecurityEvent)
                        .where(SecurityEvent.id == event.id)
                        .values(
                            description=encrypted_data.get('description'),
                            ip_address=encrypted_data.get('ip_address'),
                            user_agent=encrypted_data.get('user_agent'),
                            session_id=encrypted_data.get('session_id'),
                            additional_data=encrypted_data.get('additional_data')
                        )
                    )
                    
                    migrated_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to migrate security event {event.id}: {e}")
                    continue
            
            await session.commit()
            logger.info(f"Migrated {migrated_count} security events")

async def main():
    """Run the migration"""
    # Check if master key is set
    if not os.getenv("ENCRYPTION_MASTER_KEY"):
        print("❌ ENCRYPTION_MASTER_KEY environment variable not set!")
        print("Please set it with: export ENCRYPTION_MASTER_KEY='your-32-byte-key'")
        return
    
    migration = DatabaseEncryptionMigration()
    await migration.migrate_all_tables()

if __name__ == "__main__":
    asyncio.run(main())
