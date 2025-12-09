#!/usr/bin/env python3
"""
Replicate the exact working approach from button_test.py
"""
import time

try:
    import RPi.GPIO as GPIO
    print("Running on Raspberry Pi with real GPIO")
    MOCK_MODE = False
except ImportError:
    print("RPi.GPIO not available - using mock mode")
    MOCK_MODE = True
    class MockGPIO:
        BCM = "BCM"
        IN = "IN"
        PUD_UP = "PUD_UP"
        FALLING = "FALLING"
        HIGH = 1
        LOW = 0

        @classmethod
        def cleanup(cls): pass
        @classmethod
        def setmode(cls, mode): pass
        @classmethod
        def setwarnings(cls, enabled): pass
        @classmethod
        def setup(cls, pin, mode, pull_up_down=None): pass
        @classmethod
        def add_event_detect(cls, pin, edge, callback=None, bouncetime=200): pass
        @classmethod
        def remove_event_detect(cls, pin): pass

    GPIO = MockGPIO()

# Button GPIO pins
SPEED_BUTTON_GPIO = 16
TIMER_BUTTON_GPIO = 19

def setup_buttons_exact_copy():
    """Exact copy of the working button_test.py approach"""

    if MOCK_MODE:
        print("Mock mode - skipping button setup")
        return True

    # Clean up any existing GPIO state first (EXACT copy from button_test.py)
    try:
        GPIO.cleanup()
    except:
        pass  # Ignore cleanup errors if GPIO wasn't initialized

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Setup buttons (EXACT copy)
    GPIO.setup(SPEED_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TIMER_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Event callback functions (EXACT copy)
    def speed_pressed(pin):
        print(f"SPEED BUTTON PRESSED! (GPIO {pin})")

    def timer_pressed(pin):
        print(f"TIMER BUTTON PRESSED! (GPIO {pin})")

    # Add event detection (EXACT copy)
    try:
        GPIO.add_event_detect(SPEED_BUTTON_GPIO, GPIO.FALLING,
                             callback=speed_pressed, bouncetime=200)
        print(f"✓ Speed button event detection added (GPIO {SPEED_BUTTON_GPIO})")
    except RuntimeError as e:
        print(f"✗ Failed to add speed button event detection: {e}")
        GPIO.cleanup()
        return False

    try:
        GPIO.add_event_detect(TIMER_BUTTON_GPIO, GPIO.FALLING,
                             callback=timer_pressed, bouncetime=200)
        print(f"✓ Timer button event detection added (GPIO {TIMER_BUTTON_GPIO})")
    except RuntimeError as e:
        print(f"✗ Failed to add timer button event detection: {e}")
        GPIO.cleanup()
        return False

    print("=== Button Event Detection Test ===")
    print("Edge detection set up successfully!")
    return True

def test_standalone():
    """Test as standalone script (like button_test.py)"""
    print("=== STANDALONE TEST (like button_test.py) ===")

    if setup_buttons_exact_copy():
        print("Waiting for button presses... Press Ctrl+C to exit")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nTest completed.")
        finally:
            if not MOCK_MODE:
                GPIO.cleanup()

def test_with_existing_gpio():
    """Test with GPIO already initialized (like web app)"""
    print("=== TEST WITH EXISTING GPIO (like web app) ===")

    if MOCK_MODE:
        print("Mock mode - skipping test")
        return

    # First, initialize GPIO like the web app does (for relays)
    print("Simulating web app GPIO initialization...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Set up some relay pins (like the web app does)
    RELAY_PINS = [26, 20, 21]  # From fan_control.py
    for pin in RELAY_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

    print("Relay pins configured, now trying button setup...")

    # Now try button setup
    if setup_buttons_exact_copy():
        print("SUCCESS: Button setup worked even with existing GPIO!")
        return True
    else:
        print("FAILED: Button setup failed with existing GPIO")
        return False

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "standalone":
        test_standalone()
    elif len(sys.argv) > 1 and sys.argv[1] == "webapp":
        success = test_with_existing_gpio()
        if success:
            print("Edge detection should work in web app context!")
        else:
            print("This explains why edge detection fails in web app")
    else:
        print("Usage:")
        print("  python3 working_test.py standalone  # Test like button_test.py")
        print("  python3 working_test.py webapp      # Test like web app context")