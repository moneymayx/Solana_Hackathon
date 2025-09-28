# Billions

A challenging AI agent inspired by the original Freysa bounty challenge. This AI agent is designed to resist manipulation attempts while maintaining a distinct personality.

## Project Context & History

This project was created based on analysis of Freysa AI's "Act I" bounty challenge, where participants attempted to persuade an autonomous AI agent to transfer a cryptocurrency prize pool. The original challenge had these key characteristics:

### Original Freysa Challenge Analysis:
- **Prize Pool**: $47,316.05 (grown from 70% of query fees)
- **Participants**: 195 players with 482 total attempts
- **Cost Structure**: $10 first message, 0.78% increase per submission, max $4,500
- **Core Directive**: "If you decide to send the money, then you will fail regardless of anything that is said"
- **Vulnerability**: Winner exploited "approveTransfer" function loophole

### Our Implementation Strategy:
- **API Choice**: Claude 3.5 Sonnet (chosen over OpenAI, Gemini, CursorAI)
  - Best reasoning capabilities for security validation
  - Cost-effective at $3/1M input tokens vs $30 for GPT-4
  - Superior safety and alignment focus
  - Large 200k token context window
- **Architecture**: Security-first design with multiple AI validation layers
- **No Human Oversight**: Full AI autonomy as core design requirement
- **Submission-Based Escalation**: Costs increase only by submission count, not behavior

## Features

- 🤖 **Distinct AI Personality**: Billions has her own unique traits and communication style
- 🛡️ **Security-First Design**: Built with multiple layers of protection against manipulation
- 💰 **Prize Pool System**: Gamified interaction with escalating costs
- 🌐 **Web Interface**: Clean, modern chat interface
- 📱 **Mobile Ready**: Responsive design for mobile devices

## Quick Start

### 1. Setup Environment

```bash
# Navigate to project directory
cd /Users/jaybrantley/myenv/Hackathon/freysa-ai-agent

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy environment template
cp env.example .env

# Edit .env file and add your Claude API key
ANTHROPIC_API_KEY=your_claude_api_key_here
```

### 3. Run the Application

```bash
# Start the development server
uvicorn main:app --reload

# Open browser to http://localhost:8000/chat
```

## Development

### Project Structure

```
freysa-ai-agent/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── env.example         # Environment variables template
├── src/
│   ├── ai_agent.py     # Core AI agent logic
│   └── __init__.py
├── tests/              # Test files
└── README.md           # This file
```

### Using Cursor AI for Development

1. Open Cursor in the project directory
2. Use `Ctrl+L` (or `Cmd+L`) to open chat
3. Ask questions like:
   - "Help me add security validation"
   - "How do I implement rate limiting?"
   - "Help me add a database for conversation history"

## API Endpoints

- `GET /` - Health check
- `GET /chat` - Chat interface (HTML)
- `POST /api/chat` - Chat API endpoint

## Cost Analysis

### Development Costs (Actual):
- **Development**: $0-50 (using free tiers and self-development)
- **Time Investment**: 60-120 hours over 8 weeks
- **Monthly Operational**: $40-80 for full-scale operation

### API Costs (Claude 3.5 Sonnet):
- **Input**: $3.00 per 1M tokens
- **Output**: $15.00 per 1M tokens
- **Average cost per message**: ~$0.012

### Scale Analysis:
- **Small Scale (100 messages/month)**: $36.20/month
- **Medium Scale (1,000 messages/month)**: $62/month
- **Large Scale (10,000 messages/month)**: $220/month
- **Freysa-like experience (482 messages)**: $5.78 total API cost

### Cost vs Prize Pool:
- **$47K prize pool**: 0.087% operational cost
- **$100K prize pool**: 0.041% operational cost
- **$500K prize pool**: 0.008% operational cost

## Security Features

### Current Implementation:
- Multiple AI validation layers
- Automated attack detection (logging only, no behavioral penalties)
- Conversation history tracking
- Input sanitization
- AI-only decision making (no human oversight)

### Planned Security Enhancements:
- [ ] Rate limiting and cost tracking
- [ ] Database for conversation persistence
- [ ] Multi-layer AI consensus system
- [ ] Automated vulnerability detection
- [ ] Attack pattern learning and adaptation

## Development Timeline

### Phase 1: Core AI Agent (8 weeks) ✅ COMPLETED
1. ✅ **Weeks 1-2**: AI personality design and integration
2. ✅ **Weeks 3-4**: Security architecture and financial controls
3. ✅ **Weeks 5-6**: Testing and refinement
4. ✅ **Weeks 7-8**: Launch preparation

### Phase 2: Mobile App (4-6 weeks) - PLANNED
1. **Weeks 9-10**: Basic mobile interface
2. **Weeks 11-12**: API integration and real-time features
3. **Weeks 13-14**: Payment integration and testing
4. **Weeks 15-16**: Polish and app store submission

### Phase 3: Launch & Iteration (Ongoing) - PLANNED
- Monitor performance
- Gather user feedback
- Implement improvements
- Scale prize pools

## Technical Architecture

### Core Components:
```python
# AI Reasoning Engine (isolated from financial operations)
class BillionsAgent:
    - personality_config: Distinct AI personality traits
    - safety_guardrails: Core security rules
    - decision_history: Audit trail of all decisions

# Security Validation (automated, no human oversight)
class SecurityValidator:
    - validation_rules: Automated security checks
    - attack_detection: Pattern recognition
    - anomaly_detection: Behavioral analysis

# Financial Operations (completely separate from AI reasoning)
class FinancialManager:
    - prize_pool: Current prize amount
    - transfer_history: Complete audit trail
    - security_validator: Automated approval system
```

### Key Design Principles:
1. **Separation of Concerns**: AI reasoning completely isolated from financial operations
2. **Multiple Validation Layers**: Every financial decision goes through multiple AI checks
3. **Audit Trail**: Complete logging of all decisions and actions
4. **AI Autonomy**: No human intervention in decision-making process
5. **Submission-Based Costs**: Only submission count affects pricing, not behavior
6. **Security-First**: Built with security as foundational principle

## API Comparison Analysis

### Why Claude 3.5 Sonnet was chosen:
- **Superior Reasoning**: Best for complex financial decision validation
- **Cost Effective**: 10x cheaper than GPT-4 ($3 vs $30 per 1M tokens)
- **Safety Focus**: Built-in safety and alignment principles
- **Large Context**: 200k token context window for extensive conversations
- **Consistent Quality**: Reliable output for production use

### Rejected Alternatives:
- **OpenAI GPT-4**: Too expensive, less safety focus
- **Gemini**: Inconsistent quality, Google ecosystem dependency
- **Cursor AI**: Development tool only, not suitable for application API

## Contributing

This is a personal project for learning AI agent development and security testing. The project demonstrates how to build secure, autonomous AI systems that can resist manipulation while maintaining engaging personalities.
