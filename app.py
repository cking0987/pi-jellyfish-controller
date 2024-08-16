from flask import Flask, render_template, request, jsonify
import json
import socket
from motor_controller import move, set_limit, start_swim, stop_swim, current_state, swim_config

app = Flask(__name__)

# Get the hostname of the device
hostname = socket.gethostname()

@app.route('/')
def index():
    return render_template('index.html', current_height=current_state['current_height'], hostname=hostname)

@app.route('/start_swim', methods=['POST'])
def start_swim_route():
    start_swim()
    return jsonify(success=True)

@app.route('/stop_swim', methods=['POST'])
def stop_swim_route():
    stop_swim()
    return jsonify(success=True)

@app.route('/config')
def config():
    return render_template('config.html', swim_config=swim_config, hostname=hostname)

@app.route('/set_config', methods=['POST'])
def set_config():
    data = request.json
    for key, value in data.items():
        set_limit(key, value)
    return jsonify(success=True)

@app.route('/move', methods=['POST'])
def move_route():
    data = request.json
    move(data['direction'], data['distance'], data['speed'], data['respect_limits'])
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)