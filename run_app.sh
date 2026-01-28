#!/bin/bash

PORT=8089

# Kill any existing process on the specified port
PID=$(netstat -tlnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1)
if [ -z "$PID" ]; then
    echo "No process running on port $PORT"
else
    echo "Killing process $PID running on port $PORT"
    kill $PID
    # Wait for the process to actually terminate
    sleep 1
fi

# Start the app in the background
nohup uvicorn main:app --host 0.0.0.0 --port $PORT > app.log 2>&1 &
echo "App started on port $PORT in background. Logs are in app.log"
