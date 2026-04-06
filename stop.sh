#!/bin/bash
echo "Stopping DVAI..."
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null
echo "Stopped."
