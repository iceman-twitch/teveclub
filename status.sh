#!/bin/bash
# Check status of Teveclub Django application

PID_FILE="logs/gunicorn.pid"

echo "==================================="
echo "Teveclub Django Status"
echo "==================================="

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Status: NOT RUNNING"
    echo "PID file not found: $PID_FILE"
    exit 1
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p $PID > /dev/null 2>&1; then
    echo "Status: RUNNING"
    echo "PID: $PID"
    echo ""
    echo "Process details:"
    ps -p $PID -o pid,ppid,cmd,etime,%cpu,%mem
    echo ""
    echo "Listening on:"
    netstat -tlnp 2>/dev/null | grep $PID || ss -tlnp 2>/dev/null | grep $PID
else
    echo "Status: NOT RUNNING"
    echo "PID file exists but process $PID is not running"
    echo "Removing stale PID file..."
    rm -f "$PID_FILE"
    exit 1
fi

echo "==================================="
