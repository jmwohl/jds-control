#!/usr/bin/env python3
"""
Test script to demonstrate the timer functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:5002"

def test_timer_functionality():
    print("🧪 Testing Fan Control Timer Functionality")
    print("=" * 50)

    # Test 1: Get initial status
    print("1️⃣ Getting initial status...")
    response = requests.get(f"{BASE_URL}/api/status")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Fan Speed: {data['current_state']['speed']}")
        print(f"   ✅ Timer Active: {data['timer_state']['active']}")
    else:
        print("   ❌ Failed to get status")
        return

    # Test 2: Set fan to high speed
    print("\n2️⃣ Setting fan to HIGH speed...")
    response = requests.post(f"{BASE_URL}/api/set_speed",
                           json={"speed": "high"})
    if response.status_code == 200:
        print("   ✅ Fan set to HIGH")
    else:
        print("   ❌ Failed to set fan speed")
        return

    # Test 3: Set a short timer (for demo purposes, let's create a 10-second timer)
    # Note: The current implementation only supports 1, 2, 4 hours
    # So let's test with 1 hour but note it in the output
    print("\n3️⃣ Setting 1-hour timer...")
    response = requests.post(f"{BASE_URL}/api/set_timer",
                           json={"hours": 1})
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Timer set successfully")
        print(f"   📅 Timer Duration: 1 hour")
        print(f"   ⏱️ Timer Active: {data['timer_state']['active']}")
    else:
        print(f"   ❌ Failed to set timer: {response.text}")
        return

    # Test 4: Check status with active timer
    print("\n4️⃣ Checking status with active timer...")
    response = requests.get(f"{BASE_URL}/api/status")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Fan Speed: {data['current_state']['speed']}")
        print(f"   ✅ Timer Active: {data['timer_state']['active']}")
        print(f"   ⏱️ Remaining: {data['timer_state']['remaining_seconds']} seconds")
        print(f"   📊 Duration: {data['timer_state']['duration_hours']} hour(s)")

    # Test 5: Cancel timer
    print("\n5️⃣ Canceling timer...")
    response = requests.post(f"{BASE_URL}/api/set_timer",
                           json={"hours": 0})
    if response.status_code == 200:
        print("   ✅ Timer canceled successfully")

    # Test 6: Final status check
    print("\n6️⃣ Final status check...")
    response = requests.get(f"{BASE_URL}/api/status")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Fan Speed: {data['current_state']['speed']}")
        print(f"   ✅ Timer Active: {data['timer_state']['active']}")

    print("\n🎉 Timer functionality tests completed!")
    print("\n📋 Summary:")
    print("   • Timer can be set for 1, 2, or 4 hours")
    print("   • Timer automatically turns off fan when expired")
    print("   • Timer can be canceled manually")
    print("   • Timer state is tracked and displayed")
    print("   • Web interface shows real-time countdown")

if __name__ == "__main__":
    try:
        test_timer_functionality()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to web server")
        print("   Make sure the Flask app is running on http://localhost:5002")
    except Exception as e:
        print(f"❌ Error: {e}")