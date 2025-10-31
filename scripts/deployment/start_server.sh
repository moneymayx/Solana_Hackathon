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
echo "✓ Starting server on http://0.0.0.0:8000 (accessible from network)"
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
echo "   Local:      http://localhost:8000/docs"
echo "   Network:    http://192.168.0.206:8000/docs"
echo "   Swagger UI: http://localhost:8000/docs"
echo "   ReDoc:      http://localhost:8000/redoc"
echo ""
echo "📱 Mobile App:"
echo "   Make sure your device is on the same WiFi network"
echo "   Backend URL: http://192.168.0.206:8000"
echo ""
echo "🔍 Test endpoints:"
echo "   curl http://localhost:8000/api/context/health"
echo "   curl http://localhost:8000/api/token/health"
echo "   curl http://localhost:8000/api/teams/health"
echo ""
echo "⏹  Press CTRL+C to stop the server"
echo "======================================"
echo ""

# Start uvicorn with --host 0.0.0.0 to allow network connections (for mobile app)
python3 -m uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000 --reload

