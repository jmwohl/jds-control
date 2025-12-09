# Fan Control System

A Raspberry Pi fan control system with both command-line and web interfaces. Compatible with macOS for development and testing.

## Features

- **Cross-Platform**: Works on Raspberry Pi (real GPIO) and macOS/Linux (mock GPIO for testing)
- **Command Line Interface**: Direct control via terminal commands
- **Web Interface**: Beautiful, responsive web control panel
- **REST API**: JSON API for integration with other systems
- **Mock Mode**: Full development and testing capability without hardware

## Files

- `fan_control.py` - Core fan control module with GPIO handling
- `web_app.py` - Flask web application and REST API
- `templates/index.html` - Web interface template
- `start_web.sh` - Startup script for the web interface
- `requirements.txt` - Python dependencies

## Setup

### 1. Clone/Download the files
All files should be in the same directory.

### 2. Install Dependencies

#### Method 1: Auto-Detection (Recommended)
The startup script automatically detects your platform:

```bash
# Create virtual environment
python3 -m venv venv

# The startup script will auto-install the correct requirements
./start_web.sh
```

#### Method 2: Manual Installation

**On macOS/Linux (Development):**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies (no GPIO)
pip install -r requirements-dev.txt
```

**On Raspberry Pi:**
```bash
# Install system packages
sudo apt update
sudo apt install python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Raspberry Pi dependencies (includes GPIO)
pip install -r requirements-rpi.txt
```

#### Method 3: Universal Requirements
```bash
# This works on both platforms (uses environment markers)
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
# Direct control (works on both Pi and macOS)
python3 fan_control.py off    # Turn fan off
python3 fan_control.py low    # Set to low speed
python3 fan_control.py med    # Set to medium speed
python3 fan_control.py high   # Set to high speed
```

### Web Interface

#### Start the web server:
```bash
# Using the startup script
./start_web.sh

# Or manually
source venv/bin/activate
python web_app.py
```

#### Access the interface:
- Open your browser to: http://localhost:5001
- The interface shows current status and provides control buttons
- Works on desktop and mobile devices

### REST API

#### Get Status:
```bash
curl http://localhost:5001/api/status
```

Response:
```json
{
  "speed": "off",
  "last_changed": "2025-12-06 23:15:30",
  "mock_mode": true
}
```

#### Set Speed:
```bash
# Set to high speed
curl -X POST -H "Content-Type: application/json" \
     -d '{"speed":"high"}' \
     http://localhost:5001/api/set_speed

# Set to off
curl -X POST -H "Content-Type: application/json" \
     -d '{"speed":"off"}' \
     http://localhost:5001/api/set_speed
```

## Hardware Configuration

### GPIO Pins (Raspberry Pi)
- Pin 26: Low Speed Relay
- Pin 20: Medium Speed Relay
- Pin 21: High Speed Relay

### Active Level Setting
The relays are configured for **active HIGH** operation. If your relays are active-LOW (most common), edit `fan_control.py`:

```python
# Change these lines in fan_control.py:
ACTIVE_LEVEL = GPIO.LOW      # Change to LOW for active-low relays
INACTIVE_LEVEL = GPIO.HIGH   # Change to HIGH for active-low relays
```

## Development Mode

When running on macOS or any system without RPi.GPIO:
- Automatically detects and switches to mock mode
- All GPIO operations are logged to console
- Full functionality for testing logic
- Web interface clearly indicates "Development Mode"

Example mock output:
```
RPi.GPIO not available - using mock GPIO for development/testing
[MOCK] GPIO.setmode(BCM)
[MOCK] GPIO.setup(pin=26, mode=OUT)
[MOCK] GPIO.output(pin=26, state=HIGH)
[MOCK] Fan speed set to: HIGH (GPIO pin 21)
```

## Security Notes

- The web interface runs on all network interfaces (0.0.0.0) for convenience
- For production use, consider:
  - Adding authentication
  - Running behind a reverse proxy
  - Using HTTPS
  - Restricting network access

## Troubleshooting

### Port 5001 is busy
If port 5001 is in use, edit `web_app.py` and change the port number:
```python
app.run(host='0.0.0.0', port=5002, debug=True)  # Change 5001 to 5002
```

### Permission errors on Raspberry Pi
GPIO operations may require sudo:
```bash
sudo python3 fan_control.py high
sudo python3 web_app.py  # For web interface
```

### Virtual environment issues
If you have problems with the virtual environment:
```bash
# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```