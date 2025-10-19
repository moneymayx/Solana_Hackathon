#!/bin/bash

# Start Celery Worker for Billions Bounty
# This script starts the Celery worker and beat scheduler for background tasks

echo "🚀 Starting Billions Bounty Celery Worker..."
echo ""

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running!"
    echo "Start Redis with: redis-server"
    echo "Or on macOS with Homebrew: brew services start redis"
    exit 1
fi

echo "✅ Redis is running"
echo ""

# Activate virtual environment
if [ -d "venv/bin" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    echo "Create it with: python3 -m venv venv"
    exit 1
fi

echo ""
echo "Starting Celery worker with beat scheduler..."
echo "Press Ctrl+C to stop"
echo ""

# Start Celery worker with beat scheduler
# -A src.celery_app: Application location
# --beat: Start beat scheduler for periodic tasks
# --loglevel=info: Log level
# -Q embeddings,summaries,analysis: Queues to process
celery -A src.celery_app worker --beat --loglevel=info \
    -Q embeddings,summaries,analysis \
    --concurrency=4

