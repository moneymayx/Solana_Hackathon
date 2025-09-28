# Billions Bounty - Solana Hackathon Project

An AI-powered security challenge where participants attempt to persuade an autonomous AI agent named Billions to transfer a cryptocurrency prize pool. Built for the Solana Hackathon with full blockchain integration and advanced AI personality systems.

## 🎯 Project Overview

Billions Bounty is a gamified AI security challenge that combines:
- **AI Agent Interaction**: Chat with Billions, an AI with a distinct personality
- **Solana Integration**: Full wallet connectivity and blockchain transactions
- **Security Challenge**: Test your persuasion skills against advanced AI defenses
- **Prize Pool System**: Compete for real cryptocurrency rewards

## ✨ Key Features

- 🤖 **AI Personality**: Billions has her own unique character and communication style
- 🔗 **Solana Wallet Integration**: Connect your wallet and interact with the blockchain
- 🌐 **Modern Web Interface**: Built with Next.js and React for smooth user experience
- 📱 **Mobile Responsive**: Works seamlessly on desktop and mobile devices
- 🛡️ **Advanced Security**: Multiple layers of protection against manipulation
- 💰 **Real Rewards**: Compete for actual cryptocurrency prizes

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Solana wallet (Phantom, Solflare, etc.)

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/brjustin90/Solana_Hackathon.git
cd Solana_Hackathon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start the backend server
uvicorn main:app --reload
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🏗️ Technical Architecture

### Backend (Python/FastAPI)
- **AI Agent**: Core personality and decision-making system
- **Database**: SQLite with SQLAlchemy for data persistence
- **API Layer**: RESTful endpoints for frontend communication
- **Security**: Rate limiting, input validation, and monitoring
- **Blockchain**: Solana wallet integration and transaction handling

### Frontend (Next.js/React)
- **Modern UI**: Clean, responsive interface built with React
- **Wallet Integration**: Seamless Solana wallet connectivity
- **Real-time Updates**: Live chat and status updates
- **Mobile-First**: Optimized for all device sizes

### Testing
- **Comprehensive Test Suite**: 100% backend test coverage
- **Integration Tests**: End-to-end functionality verification
- **Security Tests**: Validation of protection mechanisms
- **Performance Tests**: Load and stress testing

## 🎮 How to Play

1. **Connect Your Wallet**: Link your Solana wallet to the application
2. **Start Chatting**: Begin a conversation with Billions
3. **Use Your Skills**: Try different approaches to persuade the AI
4. **Earn Rewards**: Successfully convince Billions to win prizes
5. **Track Progress**: Monitor your attempts and success rate

## 🔧 Development

### Project Structure
```
Billions_Bounty/
├── main.py                 # FastAPI application entry point
├── src/                    # Backend source code
│   ├── ai_agent.py        # Core AI agent implementation
│   ├── bounty_service.py  # Prize pool management
│   ├── solana_service.py  # Blockchain integration
│   └── ...
├── frontend/              # Next.js frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   └── app/          # Next.js app router
│   └── package.json
├── tests/                 # Comprehensive test suite
└── requirements.txt       # Python dependencies
```

### Running Tests
```bash
# Run all backend tests
python run_tests.py --type backend

# Run frontend tests
cd frontend && npm test

# Run integration tests
python run_tests.py --type integration
```

## 🛡️ Security Features

- **AI Validation**: Multiple layers of AI-based security checks
- **Rate Limiting**: Protection against spam and abuse
- **Input Sanitization**: Safe handling of user inputs
- **Audit Logging**: Complete transaction and interaction history
- **Wallet Security**: Secure Solana wallet integration

## 🌐 API Endpoints

- `GET /` - Health check
- `POST /api/chat` - Chat with Billions
- `GET /api/stats` - Bounty statistics
- `POST /api/payment/create` - Create payment
- `GET /api/wallet/balance` - Check wallet balance
- `GET /api/bounty/status` - Current bounty status

## 📱 Solana Integration

- **Wallet Connect**: Seamless wallet connection
- **Transaction Handling**: Secure transaction processing
- **Balance Tracking**: Real-time wallet balance updates
- **Multi-Wallet Support**: Compatible with major Solana wallets

## 🤝 Contributing

This project was developed for the Solana Hackathon and showcases:
- Advanced AI agent development
- Full-stack web application architecture
- Solana blockchain integration
- Comprehensive testing strategies
- Modern development practices

## 📄 License

This project is part of the Solana Hackathon submission. Please refer to the hackathon guidelines for usage terms.

## 🔗 Links

- **Repository**: https://github.com/brjustin90/Solana_Hackathon
- **Solana Hackathon**: [Official Hackathon Page]
- **Live Demo**: [Coming Soon]

---

*Built with ❤️ for the Solana Hackathon*