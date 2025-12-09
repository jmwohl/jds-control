#!/usr/bin/env python3
"""
Test if importing fan_control affects edge detection
"""
import sys

try:
    import RPi.GPIO as GPIO
    print("✓ RPi.GPIO imported successfully")
except ImportError:
    print("RPi.GPIO not available")
    sys.exit(1)

# Test edge detection BEFORE importing fan_control
print("\n=== Testing edge detection BEFORE importing fan_control ===")

SPEED_BUTTON_GPIO = 16
TIMER_BUTTON_GPIO = 19

def test_callback(pin):
    print(f"Button pressed on pin {pin}")

try:
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SPEED_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(SPEED_BUTTON_GPIO, GPIO.FALLING, callback=test_callback, bouncetime=200)
    print("✓ Edge detection works BEFORE importing fan_control")
    GPIO.remove_event_detect(SPEED_BUTTON_GPIO)
except Exception as e:
    print(f"✗ Edge detection failed BEFORE importing fan_control: {e}")

# Now import fan_control and test again
print("\n=== Importing fan_control ===")
import fan_control
print(f"✓ fan_control imported (Mock Mode: {fan_control.MOCK_MODE})")

print("\n=== Testing edge detection AFTER importing fan_control ===")
try:
    GPIO.setup(SPEED_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(SPEED_BUTTON_GPIO, GPIO.FALLING, callback=test_callback, bouncetime=200)
    print("✓ Edge detection works AFTER importing fan_control")
    GPIO.remove_event_detect(SPEED_BUTTON_GPIO)
except Exception as e:
    print(f"✗ Edge detection failed AFTER importing fan_control: {e}")

print("\n=== Testing if specific GPIO pins are the issue ===")
# Test with a different pin
TEST_PIN = 18  # Different from speed/timer buttons

try:
    GPIO.setup(TEST_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(TEST_PIN, GPIO.FALLING, callback=test_callback, bouncetime=200)
    print(f"✓ Edge detection works on different pin {TEST_PIN}")
    GPIO.remove_event_detect(TEST_PIN)
except Exception as e:
    print(f"✗ Edge detection failed on different pin {TEST_PIN}: {e}")

# Try to set up the exact same way as button_test.py but with fan_control imported
print("\n=== Testing exact button_test.py sequence with fan_control imported ===")
try:
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SPEED_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TIMER_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(SPEED_BUTTON_GPIO, GPIO.FALLING, callback=test_callback, bouncetime=200)
    print(f"✓ Speed button edge detection works with fan_control imported")

    GPIO.add_event_detect(TIMER_BUTTON_GPIO, GPIO.FALLING, callback=test_callback, bouncetime=200)
    print(f"✓ Timer button edge detection works with fan_control imported")

except Exception as e:
    print(f"✗ Edge detection failed with fan_control imported: {e}")

finally:
    try:
        GPIO.cleanup()
    except:
        pass

print("\nTest complete!")