#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}"
echo "  ____  __     ___    ___ "
echo " |  _ \\ \\ \\   / / \\  |_ _|"
echo " | | | | \\ \\ / / _ \\  | | "
echo " | |_| |  \\ V / ___ \\ | | "
echo " |____/    \\_/_/   \\_\\___|"
echo ""
echo -e " Damn Vulnerable AI${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found. Install it first.${NC}"
    exit 1
fi

# Check Python version (3.11-3.13 required)
PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.minor}')")
if [ "$PY_VERSION" -gt 13 ]; then
    echo -e "${RED}✗ Python 3.${PY_VERSION} detected - not yet supported${NC}"
    echo -e "${RED}  DVAI requires Python 3.11-3.13 (pydantic-core doesn't support 3.14+)${NC}"
    echo -e "${YELLOW}  Fix: brew install python@3.13 && python3.13 -m venv backend/venv${NC}"
    exit 1
elif [ "$PY_VERSION" -lt 11 ]; then
    echo -e "${RED}✗ Python 3.${PY_VERSION} detected - too old${NC}"
    echo -e "${RED}  DVAI requires Python 3.11-3.13${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Python 3.${PY_VERSION} detected${NC}"
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js not found. Install it first.${NC}"
    exit 1
fi

# Check Ollama (optional)
if command -v ollama &> /dev/null; then
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama detected - full LLM mode${NC}"
    else
        echo -e "${YELLOW}! Ollama installed but not running. Start with: ollama serve${NC}"
        echo -e "${YELLOW}  Continuing in simulation mode...${NC}"
    fi
else
    echo -e "${YELLOW}! Ollama not found - running in simulation mode${NC}"
    echo -e "${YELLOW}  Install for real LLM: brew install ollama${NC}"
fi
echo ""

# Backend setup
echo -e "${GREEN}Starting backend...${NC}"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
python3 -m uvicorn app.main:app --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Frontend setup
echo -e "${GREEN}Starting frontend...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
fi
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for services
sleep 3
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DVAI is running!${NC}"
echo -e "${GREEN}  Open: http://localhost:3000${NC}"
echo -e "${GREEN}  API:  http://localhost:8000${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Press Ctrl+C to stop"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo 'Stopped.'; exit 0" INT
wait
