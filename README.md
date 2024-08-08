# pi-jellyfish-controller

For the love of the sea. This project allows a Raspberry Pi to be used to control a motor to raise and lower an artificial jellyfish. Most aspects of the movement are configurable via a web interface.

## web_server.py

web_server.py starts a Flask app which allows us to execute python scripts via a web service. If your pi is named "fisher1", you can access it at http://fisher1.local

## jellyfish.service

This is the service that starts on boot. The file itself needs to be located at `/etc/systemd/system/jellyfish.service`.

To restart the service manually, run `sudo systemctl restart jellyfish`. This should be used when changes are made to the Flask app running as the service. You can verify the status after restarting by running `sudo systemctl status jellyfish`.

If you make changes to the service file itself (/etc/systemd/system/jellyfish.service), run `sudo systemctl daemon-reload` to reload the systemd manager config.

## motor_controller.py

All the actual communication with the motor including state management of things like motor speed and current height are handled by motor_controller.py.
