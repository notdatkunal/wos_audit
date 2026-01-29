#!/bin/bash

PORT=8089
VENV_DIR="venv"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please create one based on the instructions in README.md"
fi

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

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    # Use python3 if available, otherwise python
    if command -v python3 >/dev/null 2>&1; then
        python3 -m venv $VENV_DIR
    else
        python -m venv $VENV_DIR
    fi
fi

# Determine the python executable path
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    PYTHON_EXE="$VENV_DIR/Scripts/python"
else
    PYTHON_EXE="$VENV_DIR/bin/python"
fi

# Install dependencies
echo "Installing dependencies in virtual environment..."
$PYTHON_EXE -m pip install -r requirements.txt

# Start the app
echo "Starting app on port $PORT using virtual environment..."
# Using python -m uvicorn is often more reliable than calling uvicorn directly if PATH is not set
nohup $PYTHON_EXE -m uvicorn main:app --host 0.0.0.0 --port $PORT > app.log 2>&1 &

echo "App starting in background. checking logs..."
sleep 2
cat app.log
