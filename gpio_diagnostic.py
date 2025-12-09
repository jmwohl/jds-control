#!/usr/bin/env python3
"""
GPIO diagnostic script to identify what's preventing edge detection
"""
import sys

# Try to import RPi.GPIO
try:
    import RPi.GPIO as GPIO
    print("✓ RPi.GPIO imported successfully")
except ImportError as e:
    print(f"✗ Failed to import RPi.GPIO: {e}")
    sys.exit(1)

# GPIO pins to test
SPEED_BUTTON_GPIO = 16
TIMER_BUTTON_GPIO = 19

def test_gpio_basic():
    """Test basic GPIO functionality"""
    print("\n=== Basic GPIO Test ===")

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        print("✓ GPIO mode set to BCM")

        # Test pin setup
        GPIO.setup(SPEED_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(TIMER_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"✓ GPIO pins {SPEED_BUTTON_GPIO} and {TIMER_BUTTON_GPIO} configured as inputs")

        # Test reading pin values
        speed_val = GPIO.input(SPEED_BUTTON_GPIO)
        timer_val = GPIO.input(TIMER_BUTTON_GPIO)
        print(f"✓ Speed button (pin {SPEED_BUTTON_GPIO}): {'HIGH' if speed_val else 'LOW'}")
        print(f"✓ Timer button (pin {TIMER_BUTTON_GPIO}): {'HIGH' if timer_val else 'LOW'}")

        return True

    except Exception as e:
        print(f"✗ Basic GPIO test failed: {e}")
        return False

def test_edge_detection():
    """Test edge detection setup"""
    print("\n=== Edge Detection Test ===")

    def dummy_callback(pin):
        print(f"Callback triggered for pin {pin}")

    # Test speed button
    try:
        print(f"Testing edge detection on pin {SPEED_BUTTON_GPIO}...")
        GPIO.add_event_detect(SPEED_BUTTON_GPIO, GPIO.FALLING,
                             callback=dummy_callback, bouncetime=200)
        print(f"✓ Edge detection added successfully to pin {SPEED_BUTTON_GPIO}")

        # Remove it
        GPIO.remove_event_detect(SPEED_BUTTON_GPIO)
        print(f"✓ Edge detection removed from pin {SPEED_BUTTON_GPIO}")

    except Exception as e:
        print(f"✗ Edge detection failed on pin {SPEED_BUTTON_GPIO}: {e}")
        return False

    # Test timer button
    try:
        print(f"Testing edge detection on pin {TIMER_BUTTON_GPIO}...")
        GPIO.add_event_detect(TIMER_BUTTON_GPIO, GPIO.FALLING,
                             callback=dummy_callback, bouncetime=200)
        print(f"✓ Edge detection added successfully to pin {TIMER_BUTTON_GPIO}")

        # Remove it
        GPIO.remove_event_detect(TIMER_BUTTON_GPIO)
        print(f"✓ Edge detection removed from pin {TIMER_BUTTON_GPIO}")

    except Exception as e:
        print(f"✗ Edge detection failed on pin {TIMER_BUTTON_GPIO}: {e}")
        return False

    return True

def check_system_resources():
    """Check for processes that might be using GPIO"""
    print("\n=== System Resource Check ===")

    import subprocess
    import os

    # Check for other Python processes
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        python_processes = [line for line in result.stdout.split('\n') if 'python' in line.lower()]

        print("Python processes running:")
        for proc in python_processes:
            if proc.strip():
                print(f"  {proc}")

    except Exception as e:
        print(f"Could not check processes: {e}")

    # Check GPIO export status
    try:
        gpio_path = "/sys/class/gpio"
        if os.path.exists(gpio_path):
            exported = os.listdir(gpio_path)
            gpio_exports = [item for item in exported if item.startswith('gpio')]
            if gpio_exports:
                print(f"Exported GPIO pins: {gpio_exports}")
            else:
                print("No GPIO pins currently exported via sysfs")
    except Exception as e:
        print(f"Could not check GPIO exports: {e}")

def cleanup_and_retry():
    """Try to clean up and retry GPIO setup"""
    print("\n=== Cleanup and Retry Test ===")

    try:
        # Force cleanup
        GPIO.cleanup()
        print("✓ GPIO cleanup completed")

        # Wait a moment
        import time
        time.sleep(0.5)

        # Try again
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup pins
        GPIO.setup(SPEED_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(TIMER_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Try edge detection
        def test_callback(pin):
            pass

        GPIO.add_event_detect(SPEED_BUTTON_GPIO, GPIO.FALLING,
                             callback=test_callback, bouncetime=200)
        print(f"✓ Edge detection works after cleanup on pin {SPEED_BUTTON_GPIO}")

        GPIO.remove_event_detect(SPEED_BUTTON_GPIO)
        print("✓ Cleanup and retry successful")
        return True

    except Exception as e:
        print(f"✗ Cleanup and retry failed: {e}")
        return False

if __name__ == "__main__":
    print("GPIO Edge Detection Diagnostic Tool")
    print("=" * 40)

    try:
        # Run tests
        basic_ok = test_gpio_basic()
        if basic_ok:
            edge_ok = test_edge_detection()
            if not edge_ok:
                check_system_resources()
                cleanup_and_retry()

    finally:
        try:
            GPIO.cleanup()
            print("\nFinal GPIO cleanup completed")
        except:
            pass

    print("\nDiagnostic complete!")