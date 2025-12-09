#!/usr/bin/env python3
"""
Diagnostic script to test button callback integration
"""

# Try importing the modules
try:
    print("Importing fan_control...")
    import fan_control
    print(f"✓ fan_control imported successfully (Mock Mode: {fan_control.MOCK_MODE})")
except ImportError as e:
    print(f"✗ Failed to import fan_control: {e}")
    exit(1)

# Check if callback functions exist
print("\nChecking callback registration functions:")
if hasattr(fan_control, 'register_speed_change_callback'):
    print("✓ register_speed_change_callback exists")
else:
    print("✗ register_speed_change_callback missing")

if hasattr(fan_control, 'register_timer_change_callback'):
    print("✓ register_timer_change_callback exists")
else:
    print("✗ register_timer_change_callback missing")

# Test callback registration
def test_speed_callback(speed):
    print(f"TEST: Speed callback called with: {speed}")

def test_timer_callback(timer):
    print(f"TEST: Timer callback called with: {timer}")

try:
    print("\nTesting callback registration:")
    fan_control.register_speed_change_callback(test_speed_callback)
    print("✓ Speed callback registered successfully")

    fan_control.register_timer_change_callback(test_timer_callback)
    print("✓ Timer callback registered successfully")

    print("\nCallback registration test completed successfully!")

except Exception as e:
    print(f"✗ Error during callback registration: {e}")
    import traceback
    traceback.print_exc()

# Test button simulation (if in mock mode)
if fan_control.MOCK_MODE:
    print("\nTesting button simulation (Mock Mode):")
    try:
        # Simulate button presses
        fan_control.speed_button_callback(16)
        fan_control.timer_button_callback(19)
        print("✓ Button simulation completed")
    except Exception as e:
        print(f"✗ Error during button simulation: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\nRunning on real hardware - skipping simulation test")

print("\nDiagnostic complete!")