#!/usr/bin/env python3
"""
Button diagnostic script for troubleshooting hardware buttons
"""
import sys
import time

# Import the fan control module
try:
    import RPi.GPIO as GPIO
    MOCK_MODE = False
    print("Running on Raspberry Pi with real GPIO")
except ImportError:
    print("RPi.GPIO not available - button testing not available in mock mode")
    print("This script must be run on a Raspberry Pi with RPi.GPIO installed")
    sys.exit(1)

# Button GPIO pins (from fan_control.py)
SPEED_BUTTON_GPIO = 16  # Speed cycling button
TIMER_BUTTON_GPIO = 19  # Timer cycling button

def test_button_hardware():
    """Test button hardware directly"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Setup buttons
    GPIO.setup(SPEED_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TIMER_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    print("=== Button Hardware Test ===")
    print(f"Speed button on GPIO {SPEED_BUTTON_GPIO} (Physical pin 36)")
    print(f"Timer button on GPIO {TIMER_BUTTON_GPIO} (Physical pin 35)")
    print("")
    print("Button states (HIGH=not pressed, LOW=pressed):")
    print("Press Ctrl+C to exit")
    print("")

    try:
        while True:
            speed_state = GPIO.input(SPEED_BUTTON_GPIO)
            timer_state = GPIO.input(TIMER_BUTTON_GPIO)

            speed_text = "NOT PRESSED" if speed_state else "PRESSED    "
            timer_text = "NOT PRESSED" if timer_state else "PRESSED    "

            print(f"\rSpeed: {speed_text} | Timer: {timer_text}", end="", flush=True)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nTest completed.")
    finally:
        GPIO.cleanup()

def test_button_events():
    """Test button event detection"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Setup buttons
    GPIO.setup(SPEED_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TIMER_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Event callback functions
    def speed_pressed(pin):
        print(f"SPEED BUTTON PRESSED! (GPIO {pin})")

    def timer_pressed(pin):
        print(f"TIMER BUTTON PRESSED! (GPIO {pin})")

    # Add event detection
    GPIO.add_event_detect(SPEED_BUTTON_GPIO, GPIO.FALLING,
                         callback=speed_pressed, bouncetime=200)
    GPIO.add_event_detect(TIMER_BUTTON_GPIO, GPIO.FALLING,
                         callback=timer_pressed, bouncetime=200)

    print("=== Button Event Detection Test ===")
    print("Waiting for button presses...")
    print("Press Ctrl+C to exit")
    print("")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nTest completed.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 button_test.py [hardware|events]")
        print("")
        print("  hardware - Test button hardware directly (real-time state)")
        print("  events   - Test button event detection (interrupt-based)")
        sys.exit(1)

    test_type = sys.argv[1].lower()

    if test_type == "hardware":
        test_button_hardware()
    elif test_type == "events":
        test_button_events()
    else:
        print(f"Unknown test type: {test_type}")
        print("Use 'hardware' or 'events'")
        sys.exit(1)