#!/bin/bash
# Kill Fan Control Web App Processes

echo "🔍 Looking for fan control processes..."

# Find processes using our ports
PIDS=$(lsof -ti:5001,5002 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "✅ No processes found using ports 5001 or 5002"
else
    echo "📋 Found processes using ports 5001/5002:"
    lsof -i:5001,5002

    echo ""
    echo "💀 Killing processes: $PIDS"
    kill -9 $PIDS 2>/dev/null

    # Wait a moment and check again
    sleep 1
    REMAINING=$(lsof -ti:5001,5002 2>/dev/null)

    if [ -z "$REMAINING" ]; then
        echo "✅ All processes killed successfully!"
    else
        echo "⚠️  Some processes may still be running:"
        lsof -i:5001,5002
    fi
fi

# Also kill any python web_app.py processes
WEB_PIDS=$(pgrep -f "python.*web_app.py" 2>/dev/null)
if [ ! -z "$WEB_PIDS" ]; then
    echo "🐍 Found web_app.py processes: $WEB_PIDS"
    kill -9 $WEB_PIDS 2>/dev/null
    echo "✅ Killed web_app.py processes"
fi

echo "🎉 Cleanup complete! Ports 5001 and 5002 should be free now."