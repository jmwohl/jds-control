#!/usr/bin/env python3
"""
Test the polling button detection independently
"""
import time
import threading

try:
    import RPi.GPIO as GPIO
    print("Running on Raspberry Pi with real GPIO")
    MOCK_MODE = False
except ImportError:
    print("RPi.GPIO not available")
    exit(1)

SPEED_BUTTON_GPIO = 16
TIMER_BUTTON_GPIO = 19

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SPEED_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TIMER_BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Button state tracking
last_speed_state = GPIO.input(SPEED_BUTTON_GPIO)
last_timer_state = GPIO.input(TIMER_BUTTON_GPIO)
last_speed_press = 0
last_timer_press = 0
DEBOUNCE_TIME = 0.5

# Polling variables
polling_active = True

def speed_callback(pin):
    print(f"SPEED BUTTON CALLBACK TRIGGERED! Pin {pin}")

def timer_callback(pin):
    print(f"TIMER BUTTON CALLBACK TRIGGERED! Pin {pin}")

def poll_buttons():
    """Poll buttons for state changes - debug version"""
    global last_speed_state, last_timer_state, last_speed_press, last_timer_press

    print("Polling thread started")

    while polling_active:
        try:
            current_time = time.time()

            # Read current states
            speed_state = GPIO.input(SPEED_BUTTON_GPIO)
            timer_state = GPIO.input(TIMER_BUTTON_GPIO)

            # Debug: Print states every few seconds
            if int(current_time) % 5 == 0:
                speed_text = "HIGH" if speed_state else "LOW"
                timer_text = "HIGH" if timer_state else "LOW"
                print(f"Debug: Speed={speed_text}, Timer={timer_text}")

            # Check speed button (HIGH -> LOW transition)
            if (last_speed_state == GPIO.HIGH and
                speed_state == GPIO.LOW and
                current_time - last_speed_press > DEBOUNCE_TIME):

                print(f"SPEED BUTTON PRESS DETECTED! {last_speed_state} -> {speed_state}")
                last_speed_press = current_time
                speed_callback(SPEED_BUTTON_GPIO)

            last_speed_state = speed_state

            # Check timer button
            if (last_timer_state == GPIO.HIGH and
                timer_state == GPIO.LOW and
                current_time - last_timer_press > DEBOUNCE_TIME):

                print(f"TIMER BUTTON PRESS DETECTED! {last_timer_state} -> {timer_state}")
                last_timer_press = current_time
                timer_callback(TIMER_BUTTON_GPIO)

            last_timer_state = timer_state

            time.sleep(0.1)  # Poll every 100ms

        except Exception as e:
            print(f"Error in polling: {e}")
            time.sleep(1)

def test_polling():
    """Test polling button detection"""
    print("=== Polling Button Test ===")
    print(f"Initial states: Speed={GPIO.input(SPEED_BUTTON_GPIO)}, Timer={GPIO.input(TIMER_BUTTON_GPIO)}")
    print("Starting polling thread...")

    # Start polling thread
    poll_thread = threading.Thread(target=poll_buttons, daemon=True)
    poll_thread.start()

    print("Press buttons to test. Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping polling...")
        global polling_active
        polling_active = False
        poll_thread.join(timeout=2)
        print("Test completed.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    test_polling()