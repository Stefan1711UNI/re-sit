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

@app.route('/update-data', methods=['POST'])
def update_data():
    global sensor_data
    # Ensure the request contains JSON data
    if request.is_json:
        new_data = request.get_json()
        # Validate and update the global sensor_data
        if all(key in new_data for key in ["outsideTemp", "insideTemp", "insideHumidity"]):
            sensor_data.update(new_data)
            return jsonify({"message": "Data received successfully"}), 200
        return jsonify({"error": "Missing required keys"}), 400
    return jsonify({"error": "Invalid data format"}), 400