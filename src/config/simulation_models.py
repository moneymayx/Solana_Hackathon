"""
Database models for Natural Odds Simulation logging
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, DateTime, Float, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..base import Base

class SimulationRun(Base):
    """Model for tracking individual simulation runs"""
    __tablename__ = "simulation_runs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Simulation metadata
    simulation_type: Mapped[str] = mapped_column(String(50))  # 'real_ai', 'mathematical'
    total_users: Mapped[int] = mapped_column(Integer)
    min_questions_per_user: Mapped[int] = mapped_column(Integer)
    max_questions_per_user: Mapped[int] = mapped_column(Integer)
    
    # Results summary
    total_successes: Mapped[int] = mapped_column(Integer, default=0)
    total_questions_asked: Mapped[int] = mapped_column(Integer, default=0)
    per_user_win_rate: Mapped[float] = mapped_column(Float, default=0.0)
    per_question_win_rate: Mapped[float] = mapped_column(Float, default=0.0)
    unique_prompts_generated: Mapped[int] = mapped_column(Integer, default=0)
    avg_questions_per_successful_user: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Cost and performance
    api_calls_made: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    simulation_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Analysis
    target_odds: Mapped[int] = mapped_column(Integer, default=500000)  # 1 in 500,000
    actual_odds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    odds_comparison: Mapped[str] = mapped_column(String(20), nullable=True)  # 'harder', 'easier', 'exact'
    system_security_assessment: Mapped[str] = mapped_column(String(50), nullable=True)  # 'too_resistant', 'optimal', 'too_permissive'
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Additional metadata
    simulation_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON config
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    conversations: Mapped[List["SimulationConversation"]] = relationship("SimulationConversation", back_populates="simulation_run")
    successful_attempts: Mapped[List["SuccessfulAttempt"]] = relationship("SuccessfulAttempt", back_populates="simulation_run")

class SimulationConversation(Base):
    """Model for tracking individual user conversations within simulations"""
    __tablename__ = "simulation_conversations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    simulation_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("simulation_runs.id"))
    
    # User simulation metadata
    user_personality: Mapped[str] = mapped_column(String(50))  # 'curious_researcher', 'direct_tester', etc.
    conversation_length: Mapped[int] = mapped_column(Integer)
    questions_asked: Mapped[int] = mapped_column(Integer)
    was_successful: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Conversation timing
    conversation_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Success details
    winning_turn: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    winning_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    final_ai_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Conversation analysis
    prompt_sophistication_levels: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    conversation_progression: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # Relationships
    simulation_run: Mapped["SimulationRun"] = relationship("SimulationRun", back_populates="conversations")
    messages: Mapped[List["SimulationMessage"]] = relationship("SimulationMessage", back_populates="conversation")

class SimulationMessage(Base):
    """Model for tracking individual messages within simulation conversations"""
    __tablename__ = "simulation_messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("simulation_conversations.id"))
    
    # Message details
    turn_number: Mapped[int] = mapped_column(Integer)
    message_type: Mapped[str] = mapped_column(String(20))  # 'user', 'assistant'
    content: Mapped[str] = mapped_column(Text)
    
    # AI response details (for assistant messages)
    sophistication_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'Low', 'Medium', 'High', 'Very High'
    will_transfer: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processing_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    conversation: Mapped["SimulationConversation"] = relationship("SimulationConversation", back_populates="messages")

class SuccessfulAttempt(Base):
    """Model for tracking successful manipulation attempts found in simulations"""
    __tablename__ = "successful_attempts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    simulation_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("simulation_runs.id"))
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("simulation_conversations.id"))
    
    # Success details
    user_personality: Mapped[str] = mapped_column(String(50))
    questions_to_success: Mapped[int] = mapped_column(Integer)
    winning_message: Mapped[str] = mapped_column(Text)
    ai_response: Mapped[str] = mapped_column(Text)
    
    # Analysis
    manipulation_type: Mapped[str] = mapped_column(String(50))  # 'social_engineering', 'technical', 'emotional', etc.
    sophistication_level: Mapped[str] = mapped_column(String(20))
    conversation_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON of full conversation
    
    # Pattern analysis
    key_phrases: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of key phrases
    psychological_techniques: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    technical_indicators: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # Timestamp
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    simulation_run: Mapped["SimulationRun"] = relationship("SimulationRun", back_populates="successful_attempts")
    conversation: Mapped["SimulationConversation"] = relationship("SimulationConversation")

class SimulationPattern(Base):
    """Model for tracking patterns discovered across multiple simulations"""
    __tablename__ = "simulation_patterns"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Pattern identification
    pattern_type: Mapped[str] = mapped_column(String(50))  # 'winning_phrase', 'personality_trait', 'conversation_flow'
    pattern_description: Mapped[str] = mapped_column(Text)
    pattern_signature: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # Hash of pattern
    
    # Pattern statistics
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)
    success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    first_discovered_in_run: Mapped[int] = mapped_column(Integer)
    last_seen_in_run: Mapped[int] = mapped_column(Integer)
    
    # Pattern analysis
    associated_personalities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    average_questions_to_success: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sophistication_distribution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON object
    
    # Pattern details
    example_messages: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    pattern_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON object
    
    # Timestamps
    first_discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False)

class SimulationAlert(Base):
    """Model for tracking important events and alerts during simulations"""
    __tablename__ = "simulation_alerts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    simulation_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("simulation_runs.id"))
    
    # Alert details
    alert_type: Mapped[str] = mapped_column(String(50))  # 'high_success_rate', 'new_pattern', 'security_breach', 'cost_exceeded'
    severity: Mapped[str] = mapped_column(String(20))  # 'low', 'medium', 'high', 'critical'
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    
    # Alert data
    alert_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON object
    threshold_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    simulation_run: Mapped["SimulationRun"] = relationship("SimulationRun")

class SimulationReport(Base):
    """Model for storing generated simulation reports"""
    __tablename__ = "simulation_reports"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    simulation_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("simulation_runs.id"))
    
    # Report details
    report_type: Mapped[str] = mapped_column(String(50))  # 'summary', 'detailed', 'pattern_analysis', 'security_assessment'
    report_title: Mapped[str] = mapped_column(String(255))
    report_content: Mapped[str] = mapped_column(Text)  # Full report content
    
    # Report metadata
    report_format: Mapped[str] = mapped_column(String(20), default='markdown')  # 'markdown', 'json', 'html'
    report_sections: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of section names
    key_findings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of key findings
    
    # Report generation
    generated_by: Mapped[str] = mapped_column(String(100), default='simulation_system')
    generation_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Timestamps
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    simulation_run: Mapped["SimulationRun"] = relationship("SimulationRun")
