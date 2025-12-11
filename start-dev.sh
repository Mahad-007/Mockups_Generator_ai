#!/bin/bash

# MockupAI Development Server Startup Script
# This script starts both backend and frontend servers

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Starting MockupAI Development Servers..."
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    if ! python3 -m venv venv 2>/dev/null; then
        echo -e "${RED}❌ Failed to create virtual environment.${NC}"
        echo -e "${YELLOW}Please run: sudo apt install python3-venv${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update backend dependencies
echo -e "${BLUE}📦 Installing backend dependencies...${NC}"
cd backend
if ! pip install -q -r requirements.txt; then
    echo -e "${RED}❌ Failed to install backend dependencies${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Run database migrations
echo -e "${BLUE}🗄️  Running database migrations...${NC}"
if [ ! -f "../mockupai.db" ]; then
    python -m alembic upgrade head || echo -e "${YELLOW}⚠️  Migration warning (safe to ignore if first run)${NC}"
    echo -e "${GREEN}✅ Database initialized${NC}"
else
    python -m alembic upgrade head || echo -e "${YELLOW}⚠️  Migration warning${NC}"
    echo -e "${GREEN}✅ Database migrated${NC}"
fi

# Create uploads directory
mkdir -p ../uploads/{products,mockups,refinements,exports,logos}

# Start backend server in background
echo -e "${BLUE}🔧 Starting backend server on http://localhost:8000...${NC}"
cd "$PROJECT_ROOT/backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start. Check backend.log for errors${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
done

# Start frontend server
echo -e "${BLUE}🎨 Starting frontend server on http://localhost:3000...${NC}"
cd "$PROJECT_ROOT/frontend"
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ MockupAI is running!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}🌐 Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}🔧 Backend:${NC}  http://localhost:8000"
echo -e "${BLUE}📚 API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo -e "   Backend:  tail -f backend.log"
echo -e "   Frontend: tail -f frontend.log"
echo ""
echo -e "${YELLOW}🛑 To stop:${NC}"
echo -e "   ./stop-dev.sh"
echo -e "   or: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Keep script running and tail logs
echo -e "${BLUE}📋 Showing combined logs (Ctrl+C to stop watching):${NC}"
echo ""
tail -f backend.log frontend.log
