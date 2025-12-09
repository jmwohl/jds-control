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

# Auto-detect platform and install appropriate requirements
if [ ! -f ".requirements_installed" ]; then
    echo "📦 Installing platform-specific requirements..."

    # Check if running on Raspberry Pi
    if [[ $(uname -m) == "arm"* ]] || [[ $(uname -m) == "aarch64" ]]; then
        echo "🍓 Detected Raspberry Pi - installing GPIO support..."
        pip install -r requirements-rpi.txt
    else
        echo "💻 Detected development environment - installing base requirements..."
        pip install -r requirements-dev.txt
    fi

    # Mark requirements as installed
    touch .requirements_installed
    echo "✅ Requirements installed successfully!"
fi

# Start the web application
python web_app.py