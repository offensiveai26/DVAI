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

# Check Python (need 3.11-3.13)
PYTHON=""
for cmd in python3.13 python3.12 python3.11 python3; do
    if command -v $cmd &> /dev/null; then
        ver=$($cmd -c "import sys; print(sys.version_info.minor)")
        if [ "$ver" -ge 11 ] && [ "$ver" -le 13 ]; then
            PYTHON=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "${RED}✗ No compatible Python found (need 3.11-3.13)${NC}"
    echo -e "${RED}  Your python3 is $(python3 --version 2>/dev/null || echo 'not installed')${NC}"
    echo -e "${YELLOW}  Fix: brew install python@3.13${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Using $($PYTHON --version)${NC}"
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
    $PYTHON -m venv venv
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
