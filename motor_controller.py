import json
import random
import RPi.GPIO as gpio
from time import sleep

# Disable GPIO warnings
gpio.setwarnings(False)

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
    with open('current_state.json', 'w') as f:
        json.dump(current_state, f)

# Function to save current state
def save_current_state():
    with open('current_state.json', 'w') as f:
        json.dump(current_state, f)

def move(direction, distance, speed, respect_limits=True):

    # Setup GPIO
    gpio.setmode(gpio.BCM)
    gpio.setup(motor_config['direction_pin'], gpio.OUT)
    gpio.setup(motor_config['pulse_pin'], gpio.OUT)
    
    # convert human-readable strings to GPIO values
    if direction == "up":
        direction_value = motor_config['motor_direction_up']
    elif direction == "down":
        direction_value = motor_config['motor_direction_down']
    else:
        raise ValueError("Invalid direction value. Use 'up' or 'down'.")
    
    # prepare values from disk storage for use
    height = int(current_state['current_height'])
    max = int(swim_config['limit_height_upper'])
    min = int(swim_config['limit_height_lower'])

    # Print the movement details
    print(f"Moving {direction} (type: {type(direction)}) for {distance} units (type: {type(distance)}) at speed {speed} (type: {type(speed)})")
    
    # Check if movement should respect limits
    if respect_limits:
        # Adjust distance if moving up and exceeding upper limit
        if direction == "up" and height + distance > max:
            distance = max - height
        # Adjust distance if moving down and exceeding lower limit
        elif direction == "down" and height - distance < min:
            distance = height - min
    
    # Set the motor direction
    gpio.output(motor_config['direction_pin'], direction_value)
    
    # Generate pulses to move the motor
    for _ in range(distance * motor_config['pulses_per_rotation']):
        gpio.output(motor_config['pulse_pin'], gpio.HIGH)  # Set pulse pin high
        sleep(1 / speed)  # Wait for the duration inversely proportional to speed
        gpio.output(motor_config['pulse_pin'], gpio.LOW)  # Set pulse pin low
        sleep(1 / speed)  # Wait again for the duration inversely proportional to speed
    
    # Update the current height based on the direction of movement
    if direction == "up":
        current_state['current_height'] += distance
    else:
        current_state['current_height'] -= distance
    
    # Save the updated current state to a file
    save_current_state()

def set_limit(option, value):
    if option in swim_config:
        swim_config[option] = value
        with open('swim_config.json', 'w') as f:
            json.dump(swim_config, f)

def start_swim():
    print("Starting swim")
    try:
        gpio.setmode(gpio.BCM)
        while True:
            # Convert current_height into int
            current_height = int(current_state['current_height'])
            # Convert swim_config values to integers
            distance_up_swim = int(swim_config['distance_up_swim'])
            speed_up_swim = int(swim_config['speed_up_swim'])
            distance_down_swim_min = int(swim_config['distance_down_swim_min'])
            distance_down_swim_max = int(swim_config['distance_down_swim_max'])
            speed_down_swim = int(swim_config['speed_down_swim'])
            limit_height_upper = int(swim_config['limit_height_upper'])
            limit_height_lower = int(swim_config['limit_height_lower'])

            # Check if the next up movement would exceed the upper limit
            if current_height + distance_up_swim <= limit_height_upper:
                move("up", distance_up_swim, speed_up_swim)
            else:
                print("Skipping up movement due to upper limit")
            random_distance = random.randint(distance_down_swim_min, distance_down_swim_max)
            # Check if the next down movement would exceed the lower limit
            if int(current_state['current_height']) - int(random_distance) >= limit_height_lower:
                print(f"Random down distance: {random_distance}")
                move("down", random_distance, speed_down_swim)
            else:
                print("Skipping down movement due to lower limit")
    except KeyboardInterrupt:
        stop_swim()

def stop_swim():
    print("Stopping swim and cleaning up GPIO")
    gpio.cleanup()

# Main section
#if __name__ == "__main__":
#    try:
#        if swim_config.get('swim_on_boot', False):
#            start_swim()
#        else:
#            print("Swim on boot is disabled.")
#    except KeyboardInterrupt:
#        stop_swim()