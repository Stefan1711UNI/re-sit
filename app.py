from flask import Flask, render_template

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

# Endpoint to receive JSON data from the Arduino
@app.route('/update-data', methods=['POST'])
def update_data():
    global sensor_data
    if request.is_json:
        sensor_data = request.get_json()  # Update the global data
        return jsonify({"message": "Data received successfully"}), 200
    return jsonify({"error": "Invalid data format"}), 400