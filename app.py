from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Define a model
class sensor_data(db.Model):
    entry = db.Column(db.Integer, primary_key=True)
    dht22_temp = db.Column(db.Integer, nullable=False)
    dht22_hum = db.Column(db.Integer, nullable=False)
    lm35 = db.Column(db.Integer, nullable=False)
    time_stamp = db.Column(db.String(16), nullable=False)

    def __repr__(self):
        return f"<Data {self.entry}, DHT22_temp: {self.dht22_temp}, DHT22_hum: {self.dht22_hum}, LM35: {self.lm35}, Time: {self.time_stamp}>"

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live_data')
def data():
    return render_template('data.html', received_data=received_data)

# Placeholder for storing sensor data
received_data = {
    "outsideTemp": 0.0,
    "insideTemp": 0.0,
    "insideHumidity": 0
}

@app.route('/update-data', methods=['POST'])
def update_data():
    global received_data
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    # Process the data (print/log, etc.)
    print(data)
    received_data.update(data)

    #extract the data
    dht22_temp = data['dht22_temp']
    dht22_hum = data['dht22_hum']
    lm35 = data['lm35']

    if not all([dht22_temp, dht22_hum, lm35]):
        return jsonify({"error": "Missing required data"}), 400
    # Add the data to the database  
    add_entry(dht22_temp,dht22_hum,lm35)

    # Respond with acknowledgment
    return jsonify({"message": "Data received successfully", "data": data}), 200
    
def add_entry(dht22_temp,dht22_hum,lm35):
    time_format = datetime.now().strftime("%Y-%m-%d/%H:%M")
    new_data = sensor_data(dht22_temp=dht22_temp, dht22_hum=dht22_hum, lm35=lm35, time_stamp=time_format)
    db.session.add(new_data)
    db.session.commit()

#data_view page
@app.route('/data_view')
def data_view():
    return render_template('data_view.html')
    
@app.route('/get-sensor-data', methods=['GET'])
def get_sensor_data():
    data = sensor_data.query.all()
    data_dict = []
    for entry in data:
        data_dict.append({"dht22_temp": entry.dht22_temp, "dht22_hum": entry.dht22_hum, "lm35": entry.lm35, "time_stamp": entry.time_stamp})
    return jsonify(data_dict)

# app.config["TEMPLATES_AUTO_RELOAD"] = True

# if __name__ == '__main__':
#     app.run(debug=True)

# for rule in app.url_map.iter_rules():
#     print(f"Route: {rule}, Endpoint: {rule.endpoint}")