#!/bin/bash

PORT=8089

echo "Checking for existing process on port $PORT..."

# Try to find PID (Works on Windows Git Bash and Linux)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    PID=$(netstat -ano | grep ":$PORT " | awk '{print $5}' | head -n 1)
    if [ -n "$PID" ] && [ "$PID" != "0" ]; then
        echo "Killing process $PID running on port $PORT (Windows)"
        taskkill //F //PID $PID
    else
        echo "No process found on port $PORT"
    fi
else
    PID=$(lsof -t -i:$PORT)
    if [ -z "$PID" ]; then
        PID=$(netstat -tlnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1)
    fi
    
    if [ -n "$PID" ]; then
        echo "Killing process $PID running on port $PORT"
        kill -9 $PID
    else
        echo "No process found on port $PORT"
    fi
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the app
echo "Starting app on port $PORT..."
# Using python -m uvicorn is often more reliable than calling uvicorn directly if PATH is not set
nohup python -m uvicorn main:app --host 0.0.0.0 --port $PORT > app.log 2>&1 &

echo "App starting in background. checking logs..."
sleep 2
cat app.log
