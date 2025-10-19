#!/bin/bash

# Billions Bounty - Server Startup Script

echo "======================================"
echo "Starting Billions Bounty API Server"
echo "======================================"
echo ""

# Navigate to project root
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Kill any existing servers
echo "✓ Checking for existing servers..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "  Killed existing server" || echo "  No existing server found"

# Start the server
echo "✓ Starting server on http://localhost:8000"
echo ""
echo "🚀 Server will start in 3 seconds..."
echo ""
sleep 1
echo "   3..."
sleep 1
echo "   2..."
sleep 1
echo "   1..."
echo ""
echo "======================================"
echo "✅ Server Starting!"
echo "======================================"
echo ""
echo "📍 Access the API at:"
echo "   Swagger UI: http://localhost:8000/docs"
echo "   ReDoc:      http://localhost:8000/redoc"
echo ""
echo "🔍 Test endpoints:"
echo "   curl http://localhost:8000/api/context/health"
echo "   curl http://localhost:8000/api/token/health"
echo "   curl http://localhost:8000/api/teams/health"
echo ""
echo "⏹  Press CTRL+C to stop the server"
echo "======================================"
echo ""

# Start uvicorn
python3 -m uvicorn apps.backend.main:app --reload --port 8000

