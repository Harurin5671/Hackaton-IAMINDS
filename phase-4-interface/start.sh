#!/bin/bash

# GhostEnergy AI - Startup Script
# This script starts both the FastAPI backend and Angular frontend

echo "👻 Starting GhostEnergy AI..."

# Start FastAPI Backend
echo "🚀 Starting FastAPI backend on port 8000..."
cd "$(dirname "$0")/api"
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start Angular Frontend
echo "🌐 Starting Angular frontend on port 4200..."
cd "../angular-app"
npm start &
FRONTEND_PID=$!

echo "✅ Both services are starting up!"
echo "📊 Dashboard will be available at: http://localhost:4200"
echo "🔗 API will be available at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
