from flask import Flask, render_template, request, jsonify
import json
import socket
from motor_controller import move, start_swim, stop_swim, current_state, swim_config, load_current_state

app = Flask(__name__)

# Get the hostname of the device
hostname = socket.gethostname()

@app.route('/')
def index():
    load_current_state()
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
# Function to save current config settings
def set_config():
    data = request.json
    try:
        with open('swim_config.json', 'w') as f:
            json.dump(data, f)
        global swim_config
        swim_config = data
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/move', methods=['POST'])
def move_route():
    data = request.json
    move(data['direction'], int(data['distance']), int(data['speed']), data['respect_limits'])
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)