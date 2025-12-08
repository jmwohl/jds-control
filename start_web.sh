#!/bin/bash
# Fan Control Web Interface Startup Script

echo "🚀 Starting Fan Control Web Interface..."

# Change to the script directory
cd "$(dirname "$0")"

# Kill any existing processes first
echo "🧹 Cleaning up any existing processes..."
./kill_web.sh

# Activate virtual environment
source venv/bin/activate

# Start the web application
python web_app.py