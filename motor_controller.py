# motor_controller.py
import RPi.GPIO as GPIO
import atexit
import threading
from time import sleep
import json
import os

# File to store persistent data
DATA_FILE = 'motor_data.json'

# Load persistent data
def load_data():
    global current_height, max_height, min_height
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
            current_height[0] = data.get('current_height', 0)
            max_height = data.get('max_height', 50)
            min_height = data.get('min_height', 0)

# Save persistent data
def save_data():
    data = {
        'current_height': current_height[0],
        'max_height': max_height,
        'min_height': min_height
    }
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

# instance-specific GPIO settings
direction_pin = 20
pulse_pin = 21
cw_direction = 0  # Clockwise (Up)
ccw_direction = 1  # Counter-Clockwise (Down)

# motor parameters
pulses_per_rotation = 200
pulse_duration = .001

# starting values for limits, speed, and position
max_height = 50
min_height = 0
natural_speed_up_rpm = 100
natural_speed_down_rpm = 60
speed_rpm = 50
current_height = [0]

# If there is motor data available on disk, load that to update the variables
load_data()

# Movement control
manual_thread = None
stop_event = threading.Event()

# safer way to set up GPIO pins
def safe_gpio_setup(pin, mode):
    try:
        GPIO.setup(pin, mode)
    except RuntimeError as e:
        print(f"Warning: {e} - Attempting to continue")
        GPIO.cleanup()  # Attempt a cleanup
        GPIO.setup(pin, mode)  # Try to setup again after cleanup

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
safe_gpio_setup(direction_pin, GPIO.OUT)
safe_gpio_setup(pulse_pin, GPIO.OUT)

def move_motor(direction, speed_rpm, ignore_limits=False):
    global current_height
    pulse_gap = (60 / (speed_rpm * pulses_per_rotation)) - pulse_duration

    GPIO.output(direction_pin, direction)
    while not stop_event.is_set():
        for _ in range(pulses_per_rotation):  # Complete one full rotation
            if stop_event.is_set():
                break
            GPIO.output(pulse_pin, GPIO.HIGH)
            sleep(pulse_duration)
            GPIO.output(pulse_pin, GPIO.LOW)
            sleep(pulse_gap)

        # Update current_height based on direction
        if direction == cw_direction:
            current_height[0] += 1  # Increase by one full rotation
        else:
            current_height[0] -= 1  # Decrease by one full rotation

        # Stop motor at limits
        if not ignore_limits and (current_height[0] >= max_height or current_height[0] <= min_height):
            stop_event.set()  # Stop the motor if limits are reached


def manual_up(speed_rpm, ignore_limits):
    global manual_thread
    stop_event.clear()  # Clear stop event in case it was set
    if manual_thread and manual_thread.is_alive():
        return  # Return if a movement is already in progress
    manual_thread = threading.Thread(target=move_motor, args=(cw_direction, speed_rpm, ignore_limits))
    manual_thread.start()

def manual_down(speed_rpm, ignore_limits):
    global manual_thread
    stop_event.clear()
    if manual_thread and manual_thread.is_alive():
        return
    manual_thread = threading.Thread(target=move_motor, args=(ccw_direction, speed_rpm, ignore_limits))
    manual_thread.start()

def set_upper_limit():
    global max_height, current_height
    max_height = current_height[0]
    save_data() # save updated values to disk

def set_lower_limit():
    global min_height, current_height
    min_height = current_height[0]
    save_data() # save updated values to disk

def get_motor_status():
    return {
        "minHeight": min_height,
        "maxHeight": max_height,
        "naturalSpeedUp": natural_speed_up_rpm,
        "naturalSpeedDown": natural_speed_down_rpm,
        "currentHeight": current_height[0],
    }

def stop():
    stop_event.set()
    if manual_thread:
        manual_thread.join()

def cleanup():
    save_data() # save all current data to disk on cleanup
    GPIO.cleanup()

atexit.register(cleanup)