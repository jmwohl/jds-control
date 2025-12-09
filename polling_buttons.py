#!/usr/bin/env python3
"""
Alternative button handling using polling instead of edge detection
"""
import time
import threading

try:
    import RPi.GPIO as GPIO
    MOCK_MODE = False
except ImportError:
    MOCK_MODE = True
    # Mock GPIO for testing
    class MockGPIO:
        BCM = "BCM"
        IN = "IN"
        PUD_UP = "PUD_UP"
        HIGH = 1
        LOW = 0

        @classmethod
        def setmode(cls, mode): pass
        @classmethod
        def setwarnings(cls, enabled): pass
        @classmethod
        def setup(cls, pin, mode, pull_up_down=None): pass
        @classmethod
        def input(cls, pin): return cls.HIGH
        @classmethod
        def cleanup(cls): pass

    GPIO = MockGPIO()

class PollingButtonHandler:
    """Button handler using polling instead of edge detection"""

    def __init__(self, speed_pin=16, timer_pin=19):
        self.speed_pin = speed_pin
        self.timer_pin = timer_pin
        self.running = False
        self.thread = None

        # Button state tracking
        self.last_speed_state = GPIO.HIGH
        self.last_timer_state = GPIO.HIGH
        self.last_speed_press = 0
        self.last_timer_press = 0
        self.debounce_time = 0.5

        # Callbacks
        self.speed_callback = None
        self.timer_callback = None

        # Setup GPIO
        self.setup_gpio()

    def setup_gpio(self):
        """Setup GPIO pins"""
        try:
            if not MOCK_MODE:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                GPIO.setup(self.speed_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(self.timer_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                print(f"✓ Polling button handler: GPIO pins {self.speed_pin}, {self.timer_pin} configured")
        except Exception as e:
            print(f"✗ Error setting up GPIO for polling: {e}")

    def set_speed_callback(self, callback):
        """Set callback for speed button"""
        self.speed_callback = callback

    def set_timer_callback(self, callback):
        """Set callback for timer button"""
        self.timer_callback = callback

    def start(self):
        """Start polling for button presses"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._poll_buttons, daemon=True)
        self.thread.start()
        print("✓ Button polling started")

    def stop(self):
        """Stop polling"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("✓ Button polling stopped")

    def _poll_buttons(self):
        """Poll buttons for state changes"""
        while self.running:
            try:
                current_time = time.time()

                # Check speed button
                if not MOCK_MODE:
                    speed_state = GPIO.input(self.speed_pin)
                    # Button pressed = LOW (due to pull-up)
                    if (self.last_speed_state == GPIO.HIGH and
                        speed_state == GPIO.LOW and
                        current_time - self.last_speed_press > self.debounce_time):

                        self.last_speed_press = current_time
                        if self.speed_callback:
                            try:
                                self.speed_callback(self.speed_pin)
                            except Exception as e:
                                print(f"Error in speed callback: {e}")

                    self.last_speed_state = speed_state

                    # Check timer button
                    timer_state = GPIO.input(self.timer_pin)
                    if (self.last_timer_state == GPIO.HIGH and
                        timer_state == GPIO.LOW and
                        current_time - self.last_timer_press > self.debounce_time):

                        self.last_timer_press = current_time
                        if self.timer_callback:
                            try:
                                self.timer_callback(self.timer_pin)
                            except Exception as e:
                                print(f"Error in timer callback: {e}")

                    self.last_timer_state = timer_state

                time.sleep(0.1)  # Poll every 100ms

            except Exception as e:
                print(f"Error in button polling: {e}")
                time.sleep(1)  # Wait longer on error

    def cleanup(self):
        """Cleanup resources"""
        self.stop()
        if not MOCK_MODE:
            try:
                GPIO.cleanup()
            except:
                pass

# Test the polling handler
if __name__ == "__main__":
    def test_speed_press(pin):
        print(f"Speed button pressed! (pin {pin})")

    def test_timer_press(pin):
        print(f"Timer button pressed! (pin {pin})")

    handler = PollingButtonHandler()
    handler.set_speed_callback(test_speed_press)
    handler.set_timer_callback(test_timer_press)

    print("Starting button polling test...")
    print("Press buttons to test. Ctrl+C to exit.")

    try:
        handler.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        handler.cleanup()