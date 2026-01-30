#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

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
        taskkill //F //PID $PID || true # Ignore error if process already gone
    else
        echo "No process found on port $PORT"
    fi
else
    PID=$(lsof -t -i:$PORT || true)
    if [ -z "$PID" ]; then
        PID=$(netstat -tlnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1 || true)
    fi
    
    if [ -n "$PID" ]; then
        echo "Killing process $PID running on port $PORT"
        kill -9 $PID || true
    else
        echo "No process found on port $PORT"
    fi
fi

# Determine python command for creation
PYTHON_CMD="python"
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v py >/dev/null 2>&1; then
    PYTHON_CMD="py"
elif ! command -v python >/dev/null 2>&1; then
    echo "Error: Python not found. Please install Python."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR using $PYTHON_CMD..."
    $PYTHON_CMD -m venv $VENV_DIR
fi

# Determine the python executable path inside venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    PYTHON_EXE="$VENV_DIR/Scripts/python"
    PIP_EXE="$VENV_DIR/Scripts/pip"
else
    PYTHON_EXE="$VENV_DIR/bin/python"
    PIP_EXE="$VENV_DIR/bin/pip"
fi

# Ensure venv python exists
if [ ! -f "$PYTHON_EXE" ]; then
    echo "Error: Virtual environment python not found at $PYTHON_EXE"
    # Fallback for some windows setups where Scripts might be bin or vice versa? 
    # Usually standard venv structure is reliable.
    exit 1
fi

# Install dependencies
echo "Installing dependencies in virtual environment..."
"$PYTHON_EXE" -m pip install -r requirements.txt

# Start the app
echo "Starting app on port $PORT using virtual environment..."
# Run in background
nohup "$PYTHON_EXE" -m uvicorn main:app --host 0.0.0.0 --port $PORT > app.log 2>&1 &

echo "App starting in background. Checking logs..."
sleep 3
if [ -f "app.log" ]; then
    cat app.log
else
    echo "app.log not created yet."
fi
