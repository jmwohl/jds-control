#!/usr/bin/env python3
"""
Test script to simulate button presses for the fan control system.
This demonstrates the GPIO button functionality in mock mode.
"""

import time
import sys
import os

# Add the current directory to the path so we can import fan_control
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fan_control

def test_button_simulation():
    """Test button functionality by simulating button presses"""
    print("=== Testing Button Functionality ===")
    print("Current state:")
    print(f"Speed: {fan_control.speed_states[fan_control.current_speed_index]}")
    print(f"Timer: {fan_control.timer_states[fan_control.current_timer_index]}")
    print()

    print("Simulating speed button presses...")
    for i in range(5):  # Full cycle + one more
        print(f"\n--- Speed Button Press {i+1} ---")
        fan_control.GPIO.simulate_button_press(fan_control.SPEED_BUTTON_GPIO)
        time.sleep(0.6)  # Wait for debounce
        print(f"Current speed: {fan_control.speed_states[fan_control.current_speed_index]}")

    print("\n" + "="*50)
    print("Simulating timer button presses...")
    for i in range(5):  # Full cycle + one more
        print(f"\n--- Timer Button Press {i+1} ---")
        fan_control.GPIO.simulate_button_press(fan_control.TIMER_BUTTON_GPIO)
        time.sleep(0.6)  # Wait for debounce
        print(f"Current timer: {fan_control.timer_states[fan_control.current_timer_index]}")

if __name__ == "__main__":
    test_button_simulation()