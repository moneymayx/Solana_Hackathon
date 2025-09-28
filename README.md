# Billions Bounty - Solana Hackathon Project

A challenging AI agent inspired by the original Freysa bounty challenge. This AI agent is designed to resist manipulation attempts while maintaining a distinct anime-inspired personality.

## Project Context & History

This project was created for the Solana Hackathon based on analysis of Freysa AI's "Act I" bounty challenge, where participants attempted to persuade an autonomous AI agent to transfer a cryptocurrency prize pool. The original challenge had these key characteristics:

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

- 🤖 **Distinct AI Personality**: Billions has her own unique anime-inspired traits and communication style
- 🛡️ **Security-First Design**: Built with multiple layers of protection against manipulation
- 💰 **Prize Pool System**: Gamified interaction with escalating costs
- 🌐 **Web Interface**: Clean, modern chat interface built with Next.js
- 📱 **Mobile Ready**: Responsive design for mobile devices
- 🔗 **Solana Integration**: Full Solana wallet connectivity and transaction support
- 🎯 **Advanced Near-Miss System**: Personalized engagement system that creates false hope
- 📊 **Progressive Difficulty**: AI becomes harder to convince over time

## Quick Start

### 1. Setup Environment

```bash
# Navigate to project directory
cd Billions_Bounty

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
# Start the backend server
uvicorn main:app --reload

# In another terminal, start the frontend
cd frontend
npm install
npm run dev

# Open browser to http://localhost:3000
```

## Development

### Project Structure

```
Billions_Bounty/
├── main.py                    # FastAPI application
├── requirements.txt           # Python dependencies
├── src/                      # Backend source code
│   ├── ai_agent.py          # Core AI agent logic
│   ├── bounty_service.py    # Bounty management
│   ├── models.py            # Database models
│   ├── personality.py       # AI personality configuration
│   └── ...
├── frontend/                # Next.js frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   └── app/            # Next.js app router
│   └── package.json
├── tests/                   # Comprehensive test suite
└── README.md               # This file
```

## Testing

All backend tests are passing 100%! Run tests with:

```bash
# Run all backend tests
python run_tests.py --type backend

# Run frontend tests
cd frontend && npm test

# Run integration tests
python run_tests.py --type integration
```

## Security Features

### Current Implementation:
- ✅ Multiple AI validation layers
- ✅ Advanced near-miss system for engagement
- ✅ Progressive difficulty scaling
- ✅ Freysa vulnerability protection
- ✅ Conversation history tracking
- ✅ Input sanitization
- ✅ AI-only decision making (no human oversight)
- ✅ Comprehensive test coverage

### Advanced Security Systems:
- **Near-Miss Categories**: Technical vulnerability hints, progress indicators, system glitches, confession revelations, competitive rivalry, technical difficulty, memory references, emotional vulnerability
- **Progressive Difficulty**: Beginner → Intermediate → Advanced → Expert → Master → Legendary → Impossible
- **Personalized Responses**: Based on user sophistication and attempt history
- **Anti-Manipulation**: Resistant to social engineering, authority appeals, emotional manipulation

## API Endpoints

- `GET /` - Health check
- `GET /chat` - Chat interface (HTML)
- `POST /api/chat` - Chat API endpoint
- `GET /api/stats` - Bounty statistics
- `POST /api/payment/create` - Create payment
- `GET /api/wallet/balance` - Wallet balance
- And many more...

## Technical Architecture

### Core Components:
```python
# AI Reasoning Engine with Advanced Personality
class BillionsAgent:
    - personality_config: Anime-inspired personality traits
    - near_miss_system: Personalized engagement responses
    - progressive_difficulty: Dynamic difficulty scaling
    - security_validation: Multi-layer protection

# Bounty Management System
class BountyService:
    - entry_processing: Handle user submissions
    - winner_determination: Automated winner selection
    - status_tracking: Real-time bounty status

# Solana Integration
class SolanaService:
    - wallet_operations: Connect and manage wallets
    - transaction_handling: Secure transaction processing
    - balance_tracking: Real-time balance updates
```

## Contributing

This project was developed for the Solana Hackathon and demonstrates advanced AI agent development with:
- Complex personality systems
- Advanced security implementations
- Full-stack web development
- Solana blockchain integration
- Comprehensive testing strategies

The codebase is ready for production deployment and showcases modern AI agent architecture with robust security measures.
