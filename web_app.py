#!/usr/bin/env python3
"""
Fan Control Web Interface

A simple Flask web application to control the fan speeds via a web interface.
Compatible with both Raspberry Pi (real GPIO) and macOS (mock GPIO) environments.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
from datetime import datetime, timedelta
import threading
import time

# Import our fan control module
import fan_control

app = Flask(__name__)

# Current fan state
current_state = {
    'speed': 'off',
    'last_changed': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'mock_mode': fan_control.MOCK_MODE
}

# Timer state
timer_state = {
    'active': False,
    'duration_hours': 0,
    'start_time': None,
    'end_time': None,
    'remaining_seconds': 0
}

# Safety timer state (6 hours max runtime)
safety_timer_state = {
    'active': False,
    'start_time': None,
    'max_hours': 6,
    'remaining_seconds': 0
}

# Timer thread references
timer_thread = None
safety_timer_thread = None


@app.route('/')
def index():
    """Main control interface."""
    update_timer_remaining()
    update_safety_timer_remaining()
    return render_template('index.html',
                         current_state=current_state,
                         timer_state=timer_state,
                         safety_timer_state=safety_timer_state,
                         mock_mode=fan_control.MOCK_MODE)


@app.route('/set_speed/<speed>')
def set_speed(speed):
    """Set fan speed via URL parameter."""
    return handle_speed_change(speed)


@app.route('/set_speed', methods=['POST'])
def set_speed_post():
    """Set fan speed via POST request."""
    speed = request.form.get('speed')
    return handle_speed_change(speed)


@app.route('/api/set_speed', methods=['POST'])
def api_set_speed():
    """API endpoint for setting fan speed."""
    data = request.get_json()
    speed = data.get('speed') if data else None

    if not speed:
        return jsonify({'error': 'Speed parameter required'}), 400

    success, message = change_fan_speed(speed)

    if success:
        return jsonify({
            'success': True,
            'message': message,
            'current_state': current_state
        })
    else:
        return jsonify({'error': message}), 400


@app.route('/api/status')
def api_status():
    """API endpoint for getting current fan status."""
    update_timer_remaining()
    update_safety_timer_remaining()
    return jsonify({
        'current_state': current_state,
        'timer_state': timer_state,
        'safety_timer_state': safety_timer_state
    })


@app.route('/set_timer/<int:hours>')
def set_timer_route(hours):
    """Set timer via URL parameter."""
    return handle_timer_change(hours)


@app.route('/cancel_timer')
def cancel_timer_route():
    """Cancel timer via URL."""
    return handle_timer_change(0)


@app.route('/api/set_timer', methods=['POST'])
def api_set_timer():
    """API endpoint for setting timer."""
    data = request.get_json()
    hours = data.get('hours') if data else None

    if hours is None:
        return jsonify({'error': 'Hours parameter required'}), 400

    if hours == 0:
        cancel_timer()
        # Reset safety timer since this is user interaction
        if current_state['speed'] != 'off':
            start_safety_timer()
        return jsonify({
            'success': True,
            'message': 'Timer cancelled',
            'timer_state': timer_state
        })

    if hours not in [1, 2, 4]:
        return jsonify({'error': 'Invalid timer duration. Must be 1, 2, or 4 hours'}), 400

    success, message = set_timer(hours)

    # Reset safety timer since this is user interaction
    if current_state['speed'] != 'off':
        start_safety_timer()

    if success:
        return jsonify({
            'success': True,
            'message': message,
            'timer_state': timer_state
        })
    else:
        return jsonify({'error': message}), 400


def handle_timer_change(hours):
    """Handle timer change and redirect back to main page."""
    if hours == 0:
        cancel_timer()
    else:
        set_timer(hours)
    return redirect(url_for('index'))


@app.route('/cycle_speed')
def cycle_speed_route():
    """Cycle to the next speed setting."""
    # Access the cycling variables from fan_control
    fan_control.current_speed_index = (fan_control.current_speed_index + 1) % len(fan_control.speed_states)
    new_speed = fan_control.speed_states[fan_control.current_speed_index]

    # Set the new speed
    fan_control.set_speed(new_speed)
    current_state['speed'] = new_speed

    # Handle safety timer
    if new_speed == 'off':
        cancel_safety_timer()
    else:
        start_safety_timer()

    return redirect(url_for('index'))


@app.route('/cycle_timer')
def cycle_timer_route():
    """Cycle to the next timer setting."""
    # Access the cycling variables from fan_control
    fan_control.current_timer_index = (fan_control.current_timer_index + 1) % len(fan_control.timer_states)
    new_timer = fan_control.timer_states[fan_control.current_timer_index]

    # Handle timer setting
    if new_timer == 'off':
        cancel_timer()
    else:
        # Convert timer state to hours (e.g., '1hr' -> 1)
        hours = int(new_timer.replace('hr', ''))
        set_timer(hours)

    # Reset safety timer since this is user interaction
    if current_state['speed'] != 'off':
        start_safety_timer()

    return redirect(url_for('index'))


@app.route('/api/cycle_speed', methods=['POST'])
def api_cycle_speed():
    """API endpoint for cycling speed."""
    fan_control.current_speed_index = (fan_control.current_speed_index + 1) % len(fan_control.speed_states)
    new_speed = fan_control.speed_states[fan_control.current_speed_index]

    fan_control.set_speed(new_speed)
    current_state['speed'] = new_speed

    # Handle safety timer
    if new_speed == 'off':
        cancel_safety_timer()
    else:
        start_safety_timer()

    return jsonify({
        'success': True,
        'message': f'Speed cycled to {new_speed}',
        'speed': new_speed,
        'current_state': current_state
    })


@app.route('/api/cycle_timer', methods=['POST'])
def api_cycle_timer():
    """API endpoint for cycling timer."""
    fan_control.current_timer_index = (fan_control.current_timer_index + 1) % len(fan_control.timer_states)
    new_timer = fan_control.timer_states[fan_control.current_timer_index]

    if new_timer == 'off':
        cancel_timer()
        message = 'Timer cycled to off'
    else:
        hours = int(new_timer.replace('hr', ''))
        success, message = set_timer(hours)
        if not success:
            return jsonify({'error': message}), 400
        message = f'Timer cycled to {new_timer}'

    # Reset safety timer since this is user interaction
    if current_state['speed'] != 'off':
        start_safety_timer()

    return jsonify({
        'success': True,
        'message': message,
        'timer_state': timer_state
    })


def handle_speed_change(speed):
    """Handle speed change and redirect back to main page."""
    if not speed:
        return redirect(url_for('index'))

    success, message = change_fan_speed(speed)
    return redirect(url_for('index'))


def change_fan_speed(speed):
    """Change the fan speed and update current state."""
    speed = speed.lower()

    # Validate speed
    valid_speeds = ['off', 'low', 'med', 'high']
    if speed not in valid_speeds:
        return False, f"Invalid speed: {speed}. Must be one of {valid_speeds}"

    try:
        # Set the fan speed
        if speed == 'off':
            fan_control.all_off()
            # Cancel timers when manually turning off
            cancel_timer()
            cancel_safety_timer()
        else:
            fan_control.set_speed(speed)
            # Start or reset safety timer when fan is turned on
            start_safety_timer()

        # Update current state
        current_state['speed'] = speed
        current_state['last_changed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        message = f"Fan speed set to: {speed.upper()}"
        if fan_control.MOCK_MODE:
            message += " (MOCK MODE)"

        return True, message

    except Exception as e:
        error_message = f"Error setting fan speed: {str(e)}"
        return False, error_message


def update_timer_remaining():
    """Update the remaining time for an active timer."""
    if timer_state['active'] and timer_state['end_time']:
        now = datetime.now()
        remaining = timer_state['end_time'] - now
        if remaining.total_seconds() > 0:
            remaining_seconds = remaining.total_seconds()
            # Round up to next full minute for better display (shows 2:00 instead of 1:59)
            timer_state['remaining_seconds'] = int(remaining_seconds) + (60 - int(remaining_seconds) % 60) if int(remaining_seconds) % 60 > 0 else int(remaining_seconds)
        else:
            timer_state['remaining_seconds'] = 0
            if timer_state['active']:
                # Timer expired, turn off fan
                timer_expired()


def set_timer(hours):
    """Set a timer for the specified number of hours."""
    global timer_thread

    # Cancel existing timer
    cancel_timer()

    # Set new timer
    timer_state['active'] = True
    timer_state['duration_hours'] = hours
    timer_state['start_time'] = datetime.now()
    timer_state['end_time'] = timer_state['start_time'] + timedelta(hours=hours)
    timer_state['remaining_seconds'] = hours * 3600

    # Start timer thread
    timer_thread = threading.Thread(target=timer_worker)
    timer_thread.daemon = True
    timer_thread.start()

    return True, f"Timer set for {hours} hour{'s' if hours != 1 else ''}"


def cancel_timer():
    """Cancel the active timer."""
    timer_state['active'] = False
    timer_state['duration_hours'] = 0
    timer_state['start_time'] = None
    timer_state['end_time'] = None
    timer_state['remaining_seconds'] = 0


def timer_expired():
    """Handle timer expiration by turning off the fan."""
    change_fan_speed('off')


def start_safety_timer():
    """Start or reset the 6-hour safety timer."""
    global safety_timer_thread

    # Cancel existing safety timer
    cancel_safety_timer()

    # Only start safety timer if fan is not off
    if current_state['speed'] == 'off':
        return

    # Set new safety timer
    safety_timer_state['active'] = True
    safety_timer_state['start_time'] = datetime.now()
    safety_timer_state['remaining_seconds'] = safety_timer_state['max_hours'] * 3600

    # Start safety timer thread
    safety_timer_thread = threading.Thread(target=safety_timer_worker)
    safety_timer_thread.daemon = True
    safety_timer_thread.start()

    print(f"Safety timer started: Fan will auto-stop after {safety_timer_state['max_hours']} hours of continuous operation")


def cancel_safety_timer():
    """Cancel the safety timer."""
    safety_timer_state['active'] = False
    safety_timer_state['start_time'] = None
    safety_timer_state['remaining_seconds'] = 0


def safety_timer_worker():
    """Background thread for safety timer countdown."""
    while safety_timer_state['active'] and safety_timer_state['remaining_seconds'] > 0:
        time.sleep(1)
        if safety_timer_state['active']:
            safety_timer_state['remaining_seconds'] -= 1

    # Safety timer expired
    if safety_timer_state['active'] and safety_timer_state['remaining_seconds'] <= 0:
        print("SAFETY TIMER EXPIRED: Fan has been running for 6+ hours. Automatically turning off for safety.")
        safety_timer_expired()


def safety_timer_expired():
    """Handle safety timer expiration by forcing fan off."""
    safety_timer_state['active'] = False
    # Force fan off for safety
    fan_control.all_off()
    current_state['speed'] = 'off'
    current_state['last_changed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Also cancel regular timer if active
    cancel_timer()


def update_safety_timer_remaining():
    """Update safety timer remaining time."""
    if safety_timer_state['active'] and safety_timer_state['start_time']:
        elapsed = datetime.now() - safety_timer_state['start_time']
        total_seconds = safety_timer_state['max_hours'] * 3600
        remaining = max(0, total_seconds - int(elapsed.total_seconds()))
        safety_timer_state['remaining_seconds'] = remaining
    else:
        safety_timer_state['remaining_seconds'] = 0


def timer_expired():
    """Handle timer expiration."""
    timer_state['active'] = False
    change_fan_speed('off')
    print("Timer expired - Fan turned off automatically")


def timer_worker():
    """Background worker thread to monitor timer expiration."""
    while timer_state['active']:
        update_timer_remaining()
        if timer_state['remaining_seconds'] <= 0 and timer_state['active']:
            timer_expired()
            break
        time.sleep(1)  # Check every second


if __name__ == '__main__':
    print("Starting Fan Control Web Interface...")
    print(f"Mock Mode: {fan_control.MOCK_MODE}")
    print("Access the interface at: http://localhost:5002")

    # Initialize to off state
    change_fan_speed('off')

    # Run the Flask app
    app.run(host='0.0.0.0', port=5002, debug=True)