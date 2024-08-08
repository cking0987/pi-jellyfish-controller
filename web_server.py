import subprocess
import socket
from flask import Flask, render_template, request, redirect, url_for, jsonify
import motor_controller

app = Flask(__name__)

@app.route('/')
def home():
    hostname = socket.gethostname()
    return render_template('index.html', hostname=hostname)

# sending functional commands to the motor
@app.route('/action', methods=['POST'])
def handle_action():
    action = request.form['action']
    if action == 'manual_up':
        motor_controller.manual_up(200,False)
    elif action == 'manual_down':
        motor_controller.manual_down(200,False)
    elif action == 'stop':
        motor_controller.stop()
    elif action == 'set_upper_limit':
        motor_controller.set_upper_limit()
    elif action == 'set_lower_limit':
        motor_controller.set_lower_limit()
    elif action == 'manual_up_no_limits':
        motor_controller.manual_up(100,True)
    elif action == 'manual_down_no_limits':
        motor_controller.manual_down(100,True)
    return redirect(url_for('home'))

# getting data from the motor
@app.route('/get_motor_status')
def motor_status():
    status = motor_controller.get_motor_status()
    return jsonify(status)

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=80)
    finally:
        motor_controller.cleanup()
