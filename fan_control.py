#!/usr/bin/env python3
import sys

# Try to import RPi.GPIO, fall back to mock for development/testing
try:
    import RPi.GPIO as GPIO
    MOCK_MODE = False
    print("Running on Raspberry Pi with real GPIO")
except ImportError:
    print("RPi.GPIO not available - using mock GPIO for development/testing")
    MOCK_MODE = True

    # Mock GPIO class for development on non-Pi systems
    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        IN = "IN"
        HIGH = True
        LOW = False
        PUD_UP = "PUD_UP"
        PUD_DOWN = "PUD_DOWN"
        RISING = "RISING"
        FALLING = "FALLING"
        BOTH = "BOTH"

        _pin_states = {}
        _pin_modes = {}
        _callbacks = {}

        @classmethod
        def setmode(cls, mode):
            print(f"[MOCK] GPIO.setmode({mode})")

        @classmethod
        def setwarnings(cls, enabled):
            print(f"[MOCK] GPIO.setwarnings({enabled})")

        @classmethod
        def setup(cls, pin, mode, pull_up_down=None):
            cls._pin_modes[pin] = mode
            if mode == cls.IN:
                cls._pin_states[pin] = cls.HIGH  # Default to HIGH for pulled-up input
            else:
                cls._pin_states[pin] = cls.LOW  # Default to LOW for output
            pull_str = f", pull_up_down={pull_up_down}" if pull_up_down else ""
            print(f"[MOCK] GPIO.setup(pin={pin}, mode={mode}{pull_str})")

        @classmethod
        def output(cls, pin, state):
            cls._pin_states[pin] = state
            state_name = "HIGH" if state else "LOW"
            print(f"[MOCK] GPIO.output(pin={pin}, state={state_name})")

        @classmethod
        def input(cls, pin):
            state = cls._pin_states.get(pin, cls.HIGH)
            return state

        @classmethod
        def add_event_detect(cls, pin, edge, callback=None, bouncetime=200):
            print(f"[MOCK] GPIO.add_event_detect(pin={pin}, edge={edge}, bouncetime={bouncetime})")
            if callback:
                cls._callbacks[pin] = callback

        @classmethod
        def remove_event_detect(cls, pin):
            print(f"[MOCK] GPIO.remove_event_detect(pin={pin})")
            if pin in cls._callbacks:
                del cls._callbacks[pin]

        @classmethod
        def cleanup(cls):
            print("[MOCK] GPIO.cleanup()")
            cls._pin_states.clear()
            cls._pin_modes.clear()
            cls._callbacks.clear()

        @classmethod
        def simulate_button_press(cls, pin):
            """Simulate a button press for testing"""
            if pin in cls._callbacks:
                print(f"[MOCK] Simulating button press on pin {pin}")
                cls._callbacks[pin](pin)

    GPIO = MockGPIO()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# === YOUR MAPPING ===
RELAY_LOW_GPIO  = 26  # low speed
RELAY_MED_GPIO  = 20  # medium speed
RELAY_HIGH_GPIO = 21  # high speed

# === BUTTON MAPPING ===
SPEED_BUTTON_GPIO = 16  # Speed cycling button
TIMER_BUTTON_GPIO = 19  # Timer cycling button

# Button state tracking
speed_states = ['off', 'low', 'med', 'high']
timer_states = ['off', '1hr', '2hr', '4hr']
current_speed_index = 0
current_timer_index = 0

# Last press time for debouncing
import time
last_speed_press = 0
last_timer_press = 0
DEBOUNCE_TIME = 0.5  # 500ms debounce


def speed_button_callback(pin):
    """Handle speed button press - cycles through off, low, med, high"""
    global current_speed_index, last_speed_press

    current_time = time.time()
    if current_time - last_speed_press < DEBOUNCE_TIME:
        return  # Ignore rapid presses

    last_speed_press = current_time

    # Cycle to next speed
    current_speed_index = (current_speed_index + 1) % len(speed_states)
    new_speed = speed_states[current_speed_index]

    print(f"Speed button pressed: Setting fan to {new_speed}")
    set_speed(new_speed)


def timer_button_callback(pin):
    """Handle timer button press - cycles through off, 1hr, 2hr, 4hr"""
    global current_timer_index, last_timer_press

    current_time = time.time()
    if current_time - last_timer_press < DEBOUNCE_TIME:
        return  # Ignore rapid presses

    last_timer_press = current_time

    # Cycle to next timer setting
    current_timer_index = (current_timer_index + 1) % len(timer_states)
    new_timer = timer_states[current_timer_index]

    print(f"Timer button pressed: Setting timer to {new_timer}")

    # For now, just print the timer selection
    # The actual timer functionality will be handled by the web app
    if new_timer == 'off':
        print("Timer disabled")
    else:
        print(f"Timer set to {new_timer} (web app will handle actual timing)")


def setup_buttons():
    """Setup GPIO pins for button inputs"""
    try:
        # Setup button pins as inputs with pull-up resistors
        GPIO.setup(SPEED_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(TIMER_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Add interrupt detection for button presses (falling edge = button press)
        GPIO.add_event_detect(SPEED_BUTTON_GPIO, GPIO.FALLING,
                            callback=speed_button_callback, bouncetime=200)
        GPIO.add_event_detect(TIMER_BUTTON_GPIO, GPIO.FALLING,
                            callback=timer_button_callback, bouncetime=200)

        print("Button GPIO pins configured successfully")
        print(f"Speed button on pin {SPEED_BUTTON_GPIO}")
        print(f"Timer button on pin {TIMER_BUTTON_GPIO}")

    except Exception as e:
        print(f"Error setting up buttons: {e}")


# === ACTIVE LEVEL SETTING ===
# Most Pi relay boards are active-LOW: pin LOW = relay ON.
# If your relays behave inverted, change these two lines so:
ACTIVE_LEVEL = GPIO.HIGH
INACTIVE_LEVEL = GPIO.LOW
# ACTIVE_LEVEL   = GPIO.LOW
# INACTIVE_LEVEL = GPIO.HIGH

SPEED_PINS = {
    "low":  RELAY_LOW_GPIO,
    "med":  RELAY_MED_GPIO,
    "high": RELAY_HIGH_GPIO,
}


def test_buttons():
    """Test button functionality in mock mode"""
    import time
    if not MOCK_MODE:
        print("Button testing only available in mock mode")
        return

    print("\n=== Testing Button Functionality ===")
    print("Current states:")
    print(f"Speed: {speed_states[current_speed_index]}")
    print(f"Timer: {timer_states[current_timer_index]}")

    print("\nSimulating speed button presses...")
    for i in range(5):
        print(f"\nPress {i+1}:")
        GPIO.simulate_button_press(SPEED_BUTTON_GPIO)
        time.sleep(0.6)  # Wait longer than debounce time

    print("\nSimulating timer button presses...")
    for i in range(5):
        print(f"\nPress {i+1}:")
        GPIO.simulate_button_press(TIMER_BUTTON_GPIO)
        time.sleep(0.6)  # Wait longer than debounce time


# Setup pins as outputs and default them all OFF
for pin in SPEED_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, INACTIVE_LEVEL)

# Setup button pins for physical control
setup_buttons()


def all_off():
    """Turn all speed relays off."""
    for pin in SPEED_PINS.values():
        GPIO.output(pin, INACTIVE_LEVEL)
    if MOCK_MODE:
        print("[MOCK] All fan relays turned OFF")


def set_speed(speed_name: str):
    """
    speed_name: 'off', 'low', 'med', 'high'
    Ensures only one relay is active at a time.
    """
    # Always start by turning everything off
    all_off()

    # Then enable the specific speed, if requested
    if speed_name in SPEED_PINS:
        GPIO.output(SPEED_PINS[speed_name], ACTIVE_LEVEL)
        if MOCK_MODE:
            print(f"[MOCK] Fan speed set to: {speed_name.upper()} (GPIO pin {SPEED_PINS[speed_name]})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: sudo ./fan_control.py [off|low|med|high|test]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "test":
        test_buttons()
        sys.exit(0)
    elif cmd == "off":
        set_speed("off")
    elif cmd == "low":
        set_speed("low")
    elif cmd == "med":
        set_speed("med")
    elif cmd in ("high", "hi"):
        set_speed("high")
    else:
        print("Unknown command:", cmd)
        sys.exit(1)

    # NOTE: No GPIO.cleanup() here on purpose.
    # We want the relays to stay in their last state after exit.
    mode_indicator = " (MOCK MODE)" if MOCK_MODE else ""
    print(f"Set speed: {cmd}{mode_indicator}")


# Test command is handled in the main section above
