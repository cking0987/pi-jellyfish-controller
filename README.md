# pi-jellyfish-controller

*For the love of the sea.*

This project allows an artificial jellyfish to be controlled (raised and lowered automatically) by a Raspberry Pi and a stepper motor. The movement is highly configurable via web interface and is designed to look organic.

## Hardware components

1. **Raspberry Pi** - This runs a tiny web server for configuring the movement and the Python script for controlling the motor. I tested thoroughly on Raspberry Pi 4 Model B/1GB, but a lower-powered pi would probably suffice.
2. **Stepper motor** - This project is designed for a ***NEMA-23*** stepper motor, which was sufficient to control jellyfish weighing ~15lbs or ~6.8kgs.
3. **Motor controller** - A motor controller handles all of the actual electrical signals going directly to the motor. It allows us to send simple 5v pulses from the Raspberry Pi GPIO, and it will convert those to useable voltage/amperage. It will also handle monitoring of the shaft rotation position. I used a ***DM542T*** motor controller.
4. **Power supply** - I used a 48V power supply rated for 10A continuous current.
5. **Linear power transmission** - How will you convert the rotation of the motor's shaft to the up/down movement needed by the jellyfish? The specifics of this will vary greatly based on the specific application, but I will outline the basic components I used:
   1. 10mm shaft (matching the stepper motor shaft diameter). This was mounted directly to the motor with a 10mm-10mm shaft coupler, and held in place with surface-mounted ball bearings (mounted to the same surface as the motor).
   2. Shaft collar. I used a flange mount shaft collar to attach the end of the steel rope to the shaft. When the shaft turns, the steel rope spools on the shaft in between the shaft collar and the mounted ball bearing.
   3. Pulleys. A series of pulleys transferred the direction of the steel rope all the way to the top of where the jellyfish hangs from. Make sure to use pulleys with an adequately large diameter, as the cheaper smaller pulleys will wear out the steel rope surprisingly quickly, even if the pulley itself can handle the weight load.

## Software components (files)

1. **app.py** - This is the Flask app that runs the web server, which is used for configuring the jellyfish movement.
2. **motor_controller.py** - This is the Python script that contains all of the logic for interacting with the motor, including the "swim" functions.
3. **motor_config.json** - Stores config settings for the motor/motor controller.
4. **swim_config.json** - Stores config setting for the jellyfish movement. This is where the config settings from the web interface are stored.
5. **current_state.json** - Stores the current 'height' of the jellyfish. This allows continuous operation even after a hard reset. Note that this file is gitignored so that you can `git pull` a new version of the repo without erasing the current state.
6. **templates** - This folder contains the page templates for the two pages in the Flask app.

## Initial setup

Assuming you are starting from a fresh Raspberry Pi OS that is connected to your local network...

### Install prereqs

``` sh
sudo apt update
sudo apt install python3-pip
sudo pip3 install flask --break-system-packages
```

### Set up git

```sh
# install git
sudo apt install git
# generate a new key
ssh-keygen -t ed25519 -C "YOUR_EMAIL_ADDRESS"
# add it to the keychain
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
# Now log in to Github and add a new SSH key. To get the public key:
cat ~/.ssh/id_ed25519.pub

# Once the SSH key has been added to Github...

# clone this repo
git clone git@github.com:cking0987/pi-jellyfish-controller.git
cd pi-jellyfish-controller
```

### Setting up the service

This sets up the Flask app as a service that runs automatically on boot. Note that the jellyfish will not start swimming on boot (I ran into too many issues with that). It's just the web server that starts on boot and waits for you to manually start the swimming function.

```sh
sudo cp jellyfish.service /etc/systemd/system/jellyfish.service
sudo systemctl daemon-reload
sudo systemctl start jellyfish
sudo systemctl enable jellyfish # enable the service to start of boot
sudo systemctl status jellyfish # verify that the service is running 
```

## Normal operation

Once everything is set up and running, you should be able to access the Pi at `HOSTNAME.local`, where HOSTNAME is the name of your Raspberry Pi. Once there, click the link at the bottom to go to the config page. Here, you will find all of the settings configured in *swim_config.json*, as well as the ability to manually move the jellyfish up and down. Use this page to play around with your particular setup to figure out which setting work best. Once you've set everything up to your liking, navigate back to the homepage and click "Start swim".