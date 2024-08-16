import json
from time import sleep
import RPi.GPIO as gpio

# Load motor parameters from motor_config.json
with open('motor_config.json', 'r') as f:
    motor_config = json.load(f)

# Load swim parameters from swim_config.json
with open('swim_config.json', 'r') as f:
    swim_config = json.load(f)

# Load current state from current_state.json
try:
    with open('current_state.json', 'r') as f:
        current_state = json.load(f)
except FileNotFoundError:
    current_state = {'current_height': 0}

# Setup GPIO
gpio.setmode(gpio.BCM)
gpio.setup(motor_config['direction_pin'], gpio.OUT)
gpio.setup(motor_config['pulse_pin'], gpio.OUT)

# Function to save current state
def save_current_state():
    with open('current_state.json', 'w') as f:
        json.dump(current_state, f)

# Motor control functions
def move(direction, distance, speed, respect_limits=True):
    if respect_limits:
        if direction == motor_config['cw_direction'] and current_state['current_height'] + distance > swim_config['limit_height_upper']:
            distance = swim_config['limit_height_upper'] - current_state['current_height']
        elif direction == motor_config['ccw_direction'] and current_state['current_height'] - distance < swim_config['limit_height_lower']:
            distance = current_state['current_height'] - swim_config['limit_height_lower']
    
    gpio.output(motor_config['direction_pin'], direction)
    for _ in range(distance * motor_config['pulses_per_rotation']):
        gpio.output(motor_config['pulse_pin'], gpio.HIGH)
        sleep(speed)
        gpio.output(motor_config['pulse_pin'], gpio.LOW)
        sleep(speed)
    
    # Update current height and save state
    if direction == motor_config['cw_direction']:
        current_state['current_height'] += distance
    else:
        current_state['current_height'] -= distance
    save_current_state()

def set_limit(option, value):
    if option in swim_config:
        swim_config[option] = value
        with open('swim_config.json', 'w') as f:
            json.dump(swim_config, f)

def start_swim():
    move(motor_config['cw_direction'], swim_config['distance_up_swim'], swim_config['speed_up_swim'])
    move(motor_config['ccw_direction'], swim_config['distance_down_swim_max'], swim_config['speed_down_swim'])

def stop_swim():
    gpio.cleanup()

# Example usage
if __name__ == '__main__':
    try:
        start_swim()
    except KeyboardInterrupt:
        stop_swim()