from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return render_template('data.html', sensor_data=sensor_data)

# Placeholder for storing sensor data
sensor_data = {
    "outsideTemp": 0.0,
    "insideTemp": 0.0,
    "insideHumidity": 0
}

@app.route('/update-data', methods=['POST'])
def update_data():
    global sensor_data
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    # Process the data (print/log, etc.)
    print(data)
    sensor_data.update(data)

    # Respond with acknowledgment
    return jsonify({"message": "Data received successfully", "data": data}), 200
    