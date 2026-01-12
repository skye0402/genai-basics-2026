#!/bin/bash
# Backend API Testing Script

echo "=========================================="
echo "🧪 Backend API Testing"
echo "=========================================="
echo ""

# Get script directory and backend directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
TEST_LOG="$SCRIPT_DIR/backend.log"

# Start backend in background
echo "🚀 Starting backend server..."
cd "$BACKEND_DIR"
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$TEST_LOG" 2>&1 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Check if server is running
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend failed to start!"
    cat "$TEST_LOG"
    exit 1
fi

echo "✓ Backend started (PID: $BACKEND_PID)"
echo ""

# Test 1: Root endpoint
echo "=========================================="
echo "Test 1: Root Endpoint (GET /)"
echo "=========================================="
curl -s http://localhost:8000/ | python3 -m json.tool
echo ""

# Test 2: Health endpoint
echo "=========================================="
echo "Test 2: Health Check (GET /health)"
echo "=========================================="
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# Test 3: Chat stream with product keyword
echo "=========================================="
echo "Test 3: Chat Stream - Product Request"
echo "=========================================="
echo "Request: POST /api/chat-stream"
echo "Message: 'show me products'"
echo ""
curl -s -X POST http://localhost:8000/api/chat-stream \
  -H "Content-Type: application/json" \
  -d '{"message": "show me products"}' \
  | head -50
echo ""
echo ""

# Test 4: Chat stream with sales keyword
echo "=========================================="
echo "Test 4: Chat Stream - Sales Request"
echo "=========================================="
echo "Request: POST /api/chat-stream"
echo "Message: 'show me sales data'"
echo ""
curl -s -X POST http://localhost:8000/api/chat-stream \
  -H "Content-Type: application/json" \
  -d '{"message": "show me sales data"}' \
  | head -50
echo ""
echo ""

# Test 5: Chat stream with default response
echo "=========================================="
echo "Test 5: Chat Stream - Default Response"
echo "=========================================="
echo "Request: POST /api/chat-stream"
echo "Message: 'hello'"
echo ""
curl -s -X POST http://localhost:8000/api/chat-stream \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}' \
  | head -30
echo ""
echo ""

# Cleanup
echo "=========================================="
echo "🧹 Cleanup"
echo "=========================================="
kill $BACKEND_PID 2>/dev/null
echo "✓ Backend stopped"
echo ""

echo "=========================================="
echo "✅ Testing Complete!"
echo "=========================================="
