import json
import random
import RPi.GPIO as gpio
from time import sleep

# Disable GPIO warnings
gpio.setwarnings(False)

# function to load motor parameters from motor_config.json
def load_motor_config():
    global motor_config
    with open('motor_config.json', 'r') as f:
        motor_config = json.load(f)

# set default motor parameters
motor_config = {
	"direction_pin": 23,
	"pulse_pin": 24,
	"motor_direction_up": 0,
	"motor_direction_down": 1,
	"pulses_per_rotation": 200,
	"pulse_duration": 0.001
}

# update motor parameters from disk storage
load_motor_config()

# function to load swim parameters from swim_config.json
def load_swim_config():
    global swim_config
    with open('swim_config.json', 'r') as f:
        swim_config = json.load(f)

# set default swim parameters
swim_config = {
    "limit_height_upper": 25,
    "limit_height_lower": 0,
    "speed_up_swim": 800,
    "speed_down_swim": 400,
    "distance_up_swim": 3,
    "distance_down_swim_min": 1,
    "distance_down_swim_max": 5
}

# update swim parameters from disk storage
load_swim_config()

# function to load current state from current_state.json
def load_current_state():
    try:
        with open('current_state.json', 'r') as f:
            global current_state
            current_state = json.load(f)
            print(f"current_state updated from disk and is now {current_state}")
    except FileNotFoundError:
        current_state = {'current_height': 0}
        with open('current_state.json', 'w') as f:
            json.dump(current_state, f)

# set default current state
current_state = {
    "current_height": 0
}

# update current state from disk storage
load_current_state()

# function to save current state to disk
def save_current_state():
    with open('current_state.json', 'w') as f:
        json.dump(current_state, f)

# function to update the current height
def update_height(direction, distance):
    global current_state
    if direction == "up":
        print(f"Up movement means changing value of current_height from {current_state['current_height']} to {current_state['current_height'] + distance}")
        current_state['current_height'] += distance
        print(f"current_state['current_height'] is now {current_state['current_height']}")
    else:
        print(f"Down movement means changing value of current_height from {current_state['current_height']} to {current_state['current_height'] - distance}")
        current_state['current_height'] -= distance
        print(f"current_state['current_height'] is now {current_state['current_height']}")
    save_current_state() # save new height to disk

# function to get motor status
def get_motor_status():
    load_current_state()
    print(f"from motor_controller: current_state is {current_state}")
    return {
        "currentHeight": current_state['current_height']
    }

# function to control motor movement
def move(direction, distance, speed, respect_limits=True):

    # run these two functions before each movement in case the values on disk have changed
    load_swim_config()
    load_current_state()

    print(f"{swim_config}")

    # set GPIO mode
    gpio.setmode(gpio.BCM)

    # set up GPIO pins
    gpio.setup(motor_config['direction_pin'], gpio.OUT)
    gpio.setup(motor_config['pulse_pin'], gpio.OUT)
    
    # convert human-readable parameter strings to GPIO values
    if direction == "up":
        direction_value = motor_config['motor_direction_up']
    elif direction == "down":
        direction_value = motor_config['motor_direction_down']
    else:
        raise ValueError("Invalid direction value. Use 'up' or 'down'.")

    # Set the motor direction
    gpio.output(motor_config['direction_pin'], direction_value)

    # convert values from disk storage to integers so we don't get calc errors
    height = int(current_state['current_height'])
    max = int(swim_config['limit_height_upper'])
    min = int(swim_config['limit_height_lower'])

    # Print the movement plan
    print(f"Planning to move {direction} (type: {type(direction)}) for {distance} units (type: {type(distance)}) at speed {speed} (type: {type(speed)})")

    # Check if movement should respect limits
    if (respect_limits == True):
        print(f"respect limits is enabled")
        # Adjust distance if moving up and exceeding upper limit
        if direction == "up" and height + distance > max:
            print(f"up distance ({distance} is too much.")
            distance = max - height
            print(f"up distance reduced to {distance}")
        # Adjust distance if moving down and exceeding lower limit
        elif direction == "down" and height - distance < min:
            print(f"down distance ({distance} is too much.")
            distance = height - min
            print(f"down distance reduced to {distance}")
    else:
        print(f"respect limits is disabled")

    # Generate pulses to move the motor
    for _ in range(distance * motor_config['pulses_per_rotation']):
        gpio.output(motor_config['pulse_pin'], gpio.HIGH)  # Set pulse pin high
        sleep(1 / speed)  # Wait for the duration inversely proportional to speed
        gpio.output(motor_config['pulse_pin'], gpio.LOW)  # Set pulse pin low
        sleep(1 / speed)  # Wait again for the duration inversely proportional to speed
    
    # Update the current height based on the direction of movement
    update_height(direction, distance)

def start_swim():
    print("Starting swim")
    
    # always check disk to see if things have changed
    load_swim_config()

    try:
        while True:
            move("up", int(swim_config['distance_up_swim']), int(swim_config['speed_up_swim']), True)
            
            # set a random distance for the down movement
            random_distance = random.randint(int(swim_config['distance_down_swim_min']), int(swim_config['distance_down_swim_max']))

            move("down", random_distance, int(swim_config['speed_down_swim']), True)
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