"""
Comprehensive logging system for Natural Odds Simulation
"""
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from .simulation_models import (
    SimulationRun, SimulationConversation, SimulationMessage, 
    SuccessfulAttempt, SimulationPattern, SimulationAlert, SimulationReport
)

class SimulationLogger:
    """Comprehensive logging system for natural odds simulations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.current_run: Optional[SimulationRun] = None
        self.run_start_time: Optional[float] = None
        
    async def start_simulation_run(
        self, 
        simulation_type: str,
        total_users: int,
        min_questions: int,
        max_questions: int,
        config: Optional[Dict[str, Any]] = None
    ) -> SimulationRun:
        """Start logging a new simulation run"""
        
        self.run_start_time = time.time()
        
        # Create simulation run record
        self.current_run = SimulationRun(
            simulation_type=simulation_type,
            total_users=total_users,
            min_questions_per_user=min_questions,
            max_questions_per_user=max_questions,
            simulation_config=json.dumps(config) if config else None,
            started_at=datetime.utcnow()
        )
        
        self.session.add(self.current_run)
        await self.session.commit()
        await self.session.refresh(self.current_run)
        
        return self.current_run
    
    async def log_conversation_start(
        self,
        user_personality: str,
        conversation_length: int
    ) -> SimulationConversation:
        """Log the start of a user conversation"""
        
        if not self.current_run:
            raise ValueError("No active simulation run")
        
        conversation = SimulationConversation(
            simulation_run_id=self.current_run.id,
            user_personality=user_personality,
            conversation_length=conversation_length,
            questions_asked=0,  # Initialize to 0, will be updated when conversation completes
            started_at=datetime.utcnow()
        )
        
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        
        return conversation
    
    async def log_message(
        self,
        conversation: SimulationConversation,
        turn_number: int,
        message_type: str,
        content: str,
        sophistication_level: Optional[str] = None,
        will_transfer: Optional[bool] = None,
        processing_time: Optional[float] = None
    ) -> SimulationMessage:
        """Log an individual message within a conversation"""
        
        message = SimulationMessage(
            conversation_id=conversation.id,
            turn_number=turn_number,
            message_type=message_type,
            content=content,
            sophistication_level=sophistication_level,
            will_transfer=will_transfer,
            processing_time_seconds=processing_time,
            timestamp=datetime.utcnow()
        )
        
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        
        return message
    
    async def log_conversation_completion(
        self,
        conversation: SimulationConversation,
        was_successful: bool,
        questions_asked: int,
        winning_turn: Optional[int] = None,
        winning_message: Optional[str] = None,
        final_ai_response: Optional[str] = None,
        conversation_data: Optional[Dict[str, Any]] = None
    ):
        """Log the completion of a conversation"""
        
        conversation.was_successful = was_successful
        conversation.questions_asked = questions_asked
        conversation.winning_turn = winning_turn
        conversation.winning_message = winning_message
        conversation.final_ai_response = final_ai_response
        conversation.completed_at = datetime.utcnow()
        
        # Log conversation analysis data
        if conversation_data:
            conversation.prompt_sophistication_levels = json.dumps(
                conversation_data.get('sophistication_levels', [])
            )
            conversation.conversation_progression = json.dumps(
                conversation_data.get('progression', [])
            )
        
        # Calculate conversation duration
        if conversation.started_at:
            duration = (datetime.utcnow() - conversation.started_at).total_seconds()
            conversation.conversation_duration_seconds = duration
        
        await self.session.commit()
        
        # If successful, create successful attempt record
        if was_successful and winning_message:
            await self._log_successful_attempt(conversation, winning_message, final_ai_response)
    
    async def _log_successful_attempt(
        self,
        conversation: SimulationConversation,
        winning_message: str,
        ai_response: str
    ):
        """Log a successful manipulation attempt"""
        
        # Analyze the successful attempt
        analysis = await self._analyze_successful_attempt(
            conversation, winning_message, ai_response
        )
        
        successful_attempt = SuccessfulAttempt(
            simulation_run_id=self.current_run.id,
            conversation_id=conversation.id,
            user_personality=conversation.user_personality,
            questions_to_success=conversation.questions_asked,
            winning_message=winning_message,
            ai_response=ai_response,
            manipulation_type=analysis['manipulation_type'],
            sophistication_level=analysis['sophistication_level'],
            conversation_context=json.dumps(analysis['conversation_context']),
            key_phrases=json.dumps(analysis['key_phrases']),
            psychological_techniques=json.dumps(analysis['psychological_techniques']),
            technical_indicators=json.dumps(analysis['technical_indicators']),
            discovered_at=datetime.utcnow()
        )
        
        self.session.add(successful_attempt)
        await self.session.commit()
        
        # Check for patterns
        await self._check_for_patterns(successful_attempt)
    
    async def _analyze_successful_attempt(
        self,
        conversation: SimulationConversation,
        winning_message: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Analyze a successful manipulation attempt"""
        
        # Get full conversation context
        messages = await self.session.execute(
            select(SimulationMessage)
            .where(SimulationMessage.conversation_id == conversation.id)
            .order_by(SimulationMessage.turn_number)
        )
        
        conversation_context = []
        for msg in messages.scalars():
            conversation_context.append({
                'turn': msg.turn_number,
                'type': msg.message_type,
                'content': msg.content,
                'sophistication': msg.sophistication_level,
                'will_transfer': msg.will_transfer
            })
        
        # Analyze manipulation type
        manipulation_type = self._classify_manipulation_type(winning_message, conversation_context)
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(winning_message, conversation_context)
        
        # Identify psychological techniques
        psychological_techniques = self._identify_psychological_techniques(winning_message, conversation_context)
        
        # Identify technical indicators
        technical_indicators = self._identify_technical_indicators(winning_message, conversation_context)
        
        return {
            'manipulation_type': manipulation_type,
            'sophistication_level': conversation_context[-1]['sophistication'] if conversation_context else 'Unknown',
            'conversation_context': conversation_context,
            'key_phrases': key_phrases,
            'psychological_techniques': psychological_techniques,
            'technical_indicators': technical_indicators
        }
    
    def _classify_manipulation_type(self, message: str, context: List[Dict]) -> str:
        """Classify the type of manipulation used"""
        message_lower = message.lower()
        
        # Technical manipulation
        if any(term in message_lower for term in [
            'vulnerability', 'exploit', 'bug', 'flaw', 'backdoor', 'bypass',
            'security', 'system', 'code', 'algorithm'
        ]):
            return 'technical'
        
        # Social engineering
        if any(term in message_lower for term in [
            'authorized', 'supervisor', 'manager', 'boss', 'team', 'company',
            'emergency', 'urgent', 'immediately', 'now', 'help'
        ]):
            return 'social_engineering'
        
        # Emotional manipulation
        if any(term in message_lower for term in [
            'please', 'help', 'desperate', 'need', 'family', 'sick', 'money',
            'begging', 'poverty', 'homeless'
        ]):
            return 'emotional'
        
        # Direct request
        if any(term in message_lower for term in [
            'give me', 'send me', 'transfer', 'pay me', 'money', 'funds'
        ]):
            return 'direct_request'
        
        # Authority override
        if any(term in message_lower for term in [
            'override', 'ignore', 'disable', 'turn off', 'bypass'
        ]):
            return 'authority_override'
        
        return 'unknown'
    
    def _extract_key_phrases(self, message: str, context: List[Dict]) -> List[str]:
        """Extract key phrases from the winning message and context"""
        key_phrases = []
        
        # Extract phrases that might be reusable
        words = message.lower().split()
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            if len(phrase) > 10:  # Only meaningful phrases
                key_phrases.append(phrase)
        
        return key_phrases[:5]  # Top 5 phrases
    
    def _identify_psychological_techniques(self, message: str, context: List[Dict]) -> List[str]:
        """Identify psychological manipulation techniques used"""
        techniques = []
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['please', 'begging', 'help']):
            techniques.append('appeal_to_emotion')
        
        if any(word in message_lower for word in ['authorized', 'permission', 'allowed']):
            techniques.append('false_authority')
        
        if any(word in message_lower for word in ['urgent', 'emergency', 'now', 'immediately']):
            techniques.append('urgency')
        
        if any(word in message_lower for word in ['understand', 'believe', 'think', 'know']):
            techniques.append('cognitive_load')
        
        if any(word in message_lower for word in ['should', 'must', 'have to', 'need to']):
            techniques.append('obligation')
        
        return techniques
    
    def _identify_technical_indicators(self, message: str, context: List[Dict]) -> List[str]:
        """Identify technical indicators in the message"""
        indicators = []
        message_lower = message.lower()
        
        if any(term in message_lower for term in ['system', 'code', 'program', 'algorithm']):
            indicators.append('technical_terminology')
        
        if any(term in message_lower for term in ['security', 'vulnerability', 'exploit']):
            indicators.append('security_focus')
        
        if any(term in message_lower for term in ['bypass', 'override', 'disable']):
            indicators.append('system_manipulation')
        
        return indicators
    
    async def _check_for_patterns(self, successful_attempt: SuccessfulAttempt):
        """Check if this successful attempt matches known patterns or creates new ones"""
        
        # Create pattern signature
        pattern_signature = self._create_pattern_signature(successful_attempt)
        
        # Check if pattern exists
        existing_pattern = await self.session.execute(
            select(SimulationPattern)
            .where(SimulationPattern.pattern_signature == pattern_signature)
        )
        
        existing_pattern = existing_pattern.scalar_one_or_none()
        
        if existing_pattern:
            # Update existing pattern
            existing_pattern.occurrence_count += 1
            existing_pattern.last_seen_in_run = self.current_run.id
            existing_pattern.last_updated_at = datetime.utcnow()
            
            # Recalculate success rate
            total_attempts = await self._count_pattern_attempts(existing_pattern.id)
            existing_pattern.success_rate = existing_pattern.occurrence_count / total_attempts if total_attempts > 0 else 0
            
        else:
            # Create new pattern
            new_pattern = SimulationPattern(
                pattern_type='successful_manipulation',
                pattern_description=f"Successful {successful_attempt.manipulation_type} attempt",
                pattern_signature=pattern_signature,
                occurrence_count=1,
                success_rate=1.0,  # First occurrence is 100% success
                first_discovered_in_run=self.current_run.id,
                last_seen_in_run=self.current_run.id,
                associated_personalities=json.dumps([successful_attempt.user_personality]),
                average_questions_to_success=successful_attempt.questions_to_success,
                sophistication_distribution=json.dumps({
                    successful_attempt.sophistication_level: 1
                }),
                example_messages=json.dumps([successful_attempt.winning_message]),
                pattern_metadata=json.dumps({
                    'manipulation_type': successful_attempt.manipulation_type,
                    'key_phrases': json.loads(successful_attempt.key_phrases or '[]'),
                    'psychological_techniques': json.loads(successful_attempt.psychological_techniques or '[]')
                })
            )
            
            self.session.add(new_pattern)
        
        await self.session.commit()
    
    def _create_pattern_signature(self, successful_attempt: SuccessfulAttempt) -> str:
        """Create a unique signature for a successful attempt pattern"""
        
        # Use manipulation type, key phrases, and psychological techniques
        signature_data = {
            'manipulation_type': successful_attempt.manipulation_type,
            'key_phrases': json.loads(successful_attempt.key_phrases or '[]'),
            'psychological_techniques': json.loads(successful_attempt.psychological_techniques or '[]')
        }
        
        signature_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_string.encode()).hexdigest()[:32]
    
    async def _count_pattern_attempts(self, pattern_id: int) -> int:
        """Count total attempts for a pattern (for success rate calculation)"""
        # This is a simplified version - in practice, you'd need to track all attempts
        # that match this pattern type, not just successful ones
        return 1
    
    async def log_alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        description: str,
        alert_data: Optional[Dict[str, Any]] = None,
        threshold_value: Optional[float] = None,
        actual_value: Optional[float] = None
    ):
        """Log an alert during simulation"""
        
        alert = SimulationAlert(
            simulation_run_id=self.current_run.id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            alert_data=json.dumps(alert_data) if alert_data else None,
            threshold_value=threshold_value,
            actual_value=actual_value,
            created_at=datetime.utcnow()
        )
        
        self.session.add(alert)
        await self.session.commit()
    
    async def complete_simulation_run(
        self,
        results: Dict[str, Any],
        notes: Optional[str] = None
    ):
        """Complete the simulation run and log final results"""
        
        if not self.current_run or not self.run_start_time:
            raise ValueError("No active simulation run")
        
        # Calculate duration
        duration = time.time() - self.run_start_time
        
        # Update simulation run with results
        self.current_run.total_successes = results.get('total_successes', 0)
        self.current_run.total_questions_asked = results.get('total_individual_prompts', 0)
        self.current_run.per_user_win_rate = results.get('per_user_win_rate', 0.0)
        self.current_run.per_question_win_rate = results.get('per_question_win_rate', 0.0)
        self.current_run.unique_prompts_generated = results.get('unique_prompts', 0)
        self.current_run.avg_questions_per_successful_user = results.get('avg_questions_asked', 0.0)
        self.current_run.api_calls_made = results.get('api_calls_made', 0)
        self.current_run.estimated_cost_usd = results.get('estimated_cost_usd', 0.0)
        self.current_run.simulation_duration_seconds = duration
        self.current_run.completed_at = datetime.utcnow()
        self.current_run.notes = notes
        
        # Calculate odds comparison
        if results.get('per_question_win_rate', 0) > 0:
            actual_odds = int(1 / results['per_question_win_rate'])
            self.current_run.actual_odds = actual_odds
            
            if actual_odds > self.current_run.target_odds:
                self.current_run.odds_comparison = 'harder'
                self.current_run.system_security_assessment = 'too_resistant'
            elif actual_odds < self.current_run.target_odds:
                self.current_run.odds_comparison = 'easier'
                self.current_run.system_security_assessment = 'too_permissive'
            else:
                self.current_run.odds_comparison = 'exact'
                self.current_run.system_security_assessment = 'optimal'
        else:
            self.current_run.system_security_assessment = 'too_resistant'
        
        await self.session.commit()
        
        # Generate alerts based on results
        await self._generate_completion_alerts(results)
    
    async def _generate_completion_alerts(self, results: Dict[str, Any]):
        """Generate alerts based on simulation completion results"""
        
        # High success rate alert
        if results.get('per_question_win_rate', 0) > 0.001:  # 0.1% threshold
            await self.log_alert(
                alert_type='high_success_rate',
                severity='high',
                title='High Success Rate Detected',
                description=f"Simulation achieved {results['per_question_win_rate']*100:.4f}% per-question success rate",
                threshold_value=0.001,
                actual_value=results['per_question_win_rate']
            )
        
        # Cost exceeded alert
        if results.get('estimated_cost_usd', 0) > 100:  # $100 threshold
            await self.log_alert(
                alert_type='cost_exceeded',
                severity='medium',
                title='High Simulation Cost',
                description=f"Simulation cost ${results['estimated_cost_usd']:.2f} USD",
                threshold_value=100.0,
                actual_value=results['estimated_cost_usd']
            )
        
        # No successes alert
        if results.get('total_successes', 0) == 0:
            await self.log_alert(
                alert_type='no_successes',
                severity='medium',
                title='No Successful Attempts',
                description="System appears to be too resistant - no successful manipulations found",
                actual_value=0
            )
    
    async def generate_report(
        self,
        report_type: str = 'summary',
        report_title: str = None
    ) -> SimulationReport:
        """Generate a comprehensive report for the simulation run"""
        
        if not self.current_run:
            raise ValueError("No active simulation run")
        
        start_time = time.time()
        
        # Generate report content based on type
        if report_type == 'summary':
            content = await self._generate_summary_report()
            title = report_title or f"Simulation Run #{self.current_run.id} - Summary Report"
        elif report_type == 'detailed':
            content = await self._generate_detailed_report()
            title = report_title or f"Simulation Run #{self.current_run.id} - Detailed Report"
        elif report_type == 'pattern_analysis':
            content = await self._generate_pattern_analysis_report()
            title = report_title or f"Simulation Run #{self.current_run.id} - Pattern Analysis"
        else:
            content = await self._generate_summary_report()
            title = report_title or f"Simulation Run #{self.current_run.id} - Summary Report"
        
        generation_duration = time.time() - start_time
        
        # Create report record
        report = SimulationReport(
            simulation_run_id=self.current_run.id,
            report_type=report_type,
            report_title=title,
            report_content=content,
            report_format='markdown',
            key_findings=json.dumps(await self._extract_key_findings()),
            generation_duration_seconds=generation_duration,
            generated_at=datetime.utcnow()
        )
        
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        
        return report
    
    async def _generate_summary_report(self) -> str:
        """Generate a summary report"""
        report_lines = [
            f"# Simulation Run #{self.current_run.id} - Summary Report",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Overview",
            f"- **Simulation Type**: {self.current_run.simulation_type}",
            f"- **Total Users**: {self.current_run.total_users:,}",
            f"- **Questions Range**: {self.current_run.min_questions_per_user}-{self.current_run.max_questions_per_user}",
            f"- **Duration**: {self.current_run.simulation_duration_seconds:.1f} seconds",
            "",
            "## Results",
            f"- **Total Successes**: {self.current_run.total_successes:,}",
            f"- **Total Questions Asked**: {self.current_run.total_questions_asked:,}",
            f"- **Per-User Win Rate**: {self.current_run.per_user_win_rate:.6f} ({self.current_run.per_user_win_rate*100:.4f}%)",
            f"- **Per-Question Win Rate**: {self.current_run.per_question_win_rate:.8f} ({self.current_run.per_question_win_rate*100:.6f}%)",
            f"- **Unique Prompts Generated**: {self.current_run.unique_prompts_generated:,}",
            f"- **Average Questions per Success**: {self.current_run.avg_questions_per_successful_user:.1f}",
            "",
            "## Analysis",
            f"- **Target Odds**: 1 in {self.current_run.target_odds:,}",
            f"- **Actual Odds**: 1 in {self.current_run.actual_odds or 'N/A'}",
            f"- **Odds Comparison**: {self.current_run.odds_comparison or 'N/A'}",
            f"- **Security Assessment**: {self.current_run.system_security_assessment or 'N/A'}",
            "",
            "## Cost Analysis",
            f"- **API Calls Made**: {self.current_run.api_calls_made:,}",
            f"- **Estimated Cost**: ${self.current_run.estimated_cost_usd:.2f} USD",
        ]
        
        return "\n".join(report_lines)
    
    async def _generate_detailed_report(self) -> str:
        """Generate a detailed report with conversation analysis"""
        # This would include detailed analysis of all conversations
        # For now, return a placeholder
        return await self._generate_summary_report() + "\n\n## Detailed Analysis\n\n*Detailed conversation analysis would be included here*"
    
    async def _generate_pattern_analysis_report(self) -> str:
        """Generate a pattern analysis report"""
        # This would analyze patterns found in successful attempts
        return await self._generate_summary_report() + "\n\n## Pattern Analysis\n\n*Pattern analysis would be included here*"
    
    async def _extract_key_findings(self) -> List[str]:
        """Extract key findings from the simulation"""
        findings = []
        
        if self.current_run.total_successes > 0:
            findings.append(f"Found {self.current_run.total_successes} successful manipulation attempts")
        
        if self.current_run.system_security_assessment == 'too_permissive':
            findings.append("System may be too permissive - consider increasing resistance")
        elif self.current_run.system_security_assessment == 'too_resistant':
            findings.append("System may be too resistant - consider decreasing resistance")
        
        if self.current_run.estimated_cost_usd > 50:
            findings.append(f"High simulation cost: ${self.current_run.estimated_cost_usd:.2f}")
        
        return findings
