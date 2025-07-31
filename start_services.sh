#!/bin/bash

# MindFlora Service Startup Script
echo "🚀 Starting MindFlora Services..."

# Activate virtual environment
source mindflora/bin/activate

# Start backend server
echo "📡 Starting API Gateway on port 8000..."
cd api_gateway
uvicorn api_gateway.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "🌐 Starting Frontend on port 8080..."
cd ../frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

# Test both services
echo "🧪 Testing services..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
fi

if curl -s http://localhost:8080/ > /dev/null; then
    echo "✅ Frontend is running on http://localhost:8080"
else
    echo "❌ Frontend failed to start"
fi

echo ""
echo "🎉 MindFlora is ready!"
echo "📱 Frontend: http://localhost:8080"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt signal
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait 