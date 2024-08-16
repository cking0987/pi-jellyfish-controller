import json
from time import sleep
import RPi.GPIO as gpio

# Load motor parameters from motor_config.json
with open('motor_config.json', 'r') as f:
    motor_config = json.load(f)

# Load swim parameters from swim_config.json
with open('swim_config.json', 'r') as f:
    swim_config = json.load(f)

# Setup GPIO
gpio.setmode(gpio.BCM)
gpio.setup(motor_config['direction_pin'], gpio.OUT)
gpio.setup(motor_config['pulse_pin'], gpio.OUT)

# Motor control functions
def move(direction, distance, speed, respect_limits=True):
    if respect_limits:
        if direction == motor_config['cw_direction'] and distance > swim_config['limit_height_upper']:
            distance = swim_config['limit_height_upper']
        elif direction == motor_config['ccw_direction'] and distance < swim_config['limit_height_lower']:
            distance = swim_config['limit_height_lower']
    
    gpio.output(motor_config['direction_pin'], direction)
    for _ in range(distance * motor_config['pulses_per_rotation']):
        gpio.output(motor_config['pulse_pin'], gpio.HIGH)
        sleep(speed)
        gpio.output(motor_config['pulse_pin'], gpio.LOW)
        sleep(speed)

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