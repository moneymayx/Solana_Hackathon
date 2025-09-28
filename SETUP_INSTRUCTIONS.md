# Billions - Complete Setup Instructions

## Quick Start Guide

### 1. Environment Setup
```bash
# Navigate to project directory
cd /Users/jaybrantley/myenv/Hackathon/billions-bounty-agent

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify Python version (should be 3.13.3)
python --version
```

### 2. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python test_setup.py
```

### 3. Configure API Keys
```bash
# Copy environment template
cp env.example .env

# Edit .env file and add your Claude API key
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```env
ANTHROPIC_API_KEY=your_claude_api_key_here
DATABASE_URL=your_database_url  # Optional for now
SECRET_KEY=your_secret_key      # Optional for now
```

### 4. Get Claude API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and paste it in your `.env` file

### 5. Test the Setup
```bash
# Run the test suite
python test_setup.py

# Expected output: 3/3 tests passed
```

### 6. Start the Application
```bash
# Start the development server
python main.py

# Alternative: Use uvicorn directly
uvicorn main:app --reload
```

### 7. Access the Application
- **API Documentation**: http://localhost:8000/docs
- **Chat Interface**: http://localhost:8000/chat
- **Health Check**: http://localhost:8000/

## Development Workflow

### Using Cursor AI for Development
1. **Open Cursor**: Launch Cursor in the project directory
2. **Use Chat**: Press `Ctrl+L` (or `Cmd+L` on Mac) to open chat
3. **Ask Questions**: 
   - "Help me add security validation to the AI agent"
   - "How do I implement rate limiting?"
   - "Help me add a database for conversation history"
   - "How do I deploy this to a cloud service?"

### Code Structure
```
billions-bounty-agent/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create from env.example)
├── test_setup.py          # Setup verification script
├── README.md              # Complete project documentation
├── DEVELOPMENT_NOTES.md   # Full context and decision history
├── SETUP_INSTRUCTIONS.md  # This file
├── src/
│   ├── __init__.py        # Package initialization
│   └── ai_agent.py        # Core BillionsAgent class
└── tests/                 # Test files (to be created)
```

## API Endpoints

### Available Endpoints:
- `GET /` - Health check endpoint
- `GET /chat` - HTML chat interface
- `POST /api/chat` - Chat API endpoint

### Chat API Usage:
```bash
# Test the chat API
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello Billions!"}'
```

## Troubleshooting

### Common Issues:

#### 1. Xcode License Agreement Error
```bash
# If you see Xcode license errors during pip install
sudo xcodebuild -license
# Follow the prompts to accept the license
```

#### 2. Virtual Environment Not Activating
```bash
# Make sure you're in the right directory
cd /Users/jaybrantley/myenv/Hackathon/billions-bounty-agent

# Try activating with full path
source ./venv/bin/activate
```

#### 3. API Key Not Working
```bash
# Verify your .env file exists and has the correct key
cat .env

# Make sure there are no extra spaces or quotes around the key
ANTHROPIC_API_KEY=sk-ant-api03-...  # Correct format
ANTHROPIC_API_KEY="sk-ant-api03-..."  # Incorrect format
```

#### 4. Port Already in Use
```bash
# If port 8000 is busy, use a different port
uvicorn main:app --reload --port 8001
```

### Verification Commands:
```bash
# Check if all dependencies are installed
pip list | grep -E "(anthropic|fastapi|uvicorn|pydantic)"

# Test Python imports
python -c "import anthropic, fastapi, uvicorn; print('All imports successful')"

# Test the AI agent initialization
python -c "from src.ai_agent import BillionsAgent; agent = BillionsAgent(); print('BillionsAgent initialized successfully')"
```

## Next Steps After Setup

### 1. Test Basic Functionality
```bash
# Start the server
python main.py

# Open browser to http://localhost:8000/chat
# Try sending a message to Billions
```

### 2. Development Tasks
- [ ] Add database integration for conversation persistence
- [ ] Implement rate limiting and cost tracking
- [ ] Add security validation layers
- [ ] Create mobile app version
- [ ] Add prize pool management system

### 3. Deployment Options
- **Local Development**: Already set up
- **Cloud Deployment**: Railway, Render, or Vercel
- **Docker**: Create Dockerfile for containerized deployment

## Cost Monitoring

### Track API Usage:
- Monitor your Claude API usage in the Anthropic console
- Expected cost: ~$0.012 per message
- For 100 messages: ~$1.20
- For 1,000 messages: ~$12.00

### Budget Planning:
- **Development/Testing**: $0-10/month
- **Small Scale (100 messages/month)**: ~$36/month
- **Medium Scale (1,000 messages/month)**: ~$62/month
- **Large Scale (10,000 messages/month)**: ~$220/month

## Support

### Documentation Files:
- `README.md` - Complete project overview and architecture
- `DEVELOPMENT_NOTES.md` - Full context and decision history
- `SETUP_INSTRUCTIONS.md` - This file

### Getting Help:
1. Check the troubleshooting section above
2. Review the DEVELOPMENT_NOTES.md for context
3. Use Cursor AI chat for development assistance
4. Check the FastAPI docs at http://localhost:8000/docs

Your Billions is now ready for development and testing!
