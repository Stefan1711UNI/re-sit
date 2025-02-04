from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#model for the sensor_data table
class sensor_data(db.Model):
    entry = db.Column(db.Integer, primary_key=True)
    dht22_temp = db.Column(db.Integer, nullable=False)
    dht22_hum = db.Column(db.Integer, nullable=False)
    lm35 = db.Column(db.Integer, nullable=False)
    time_stamp = db.Column(db.String(16), nullable=False)

    def __repr__(self):
        return f"<Data {self.entry}, DHT22_temp: {self.dht22_temp}, DHT22_hum: {self.dht22_hum}, LM35: {self.lm35}, Time: {self.time_stamp}>"

#initializes the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')


#live_data page
@app.route('/live_data')
def data():
    return render_template('data.html')

@app.route('/get_current_data', methods=['GET'])
def get_current_data():
    return jsonify(received_data)

#placeholder for the received data
received_data = {
    "outsideTemp": 0.0,
    "insideTemp": 0.0,
    "insideHumidity": 0
}

#recives data from ardunio and updates the received_data dictionary
@app.route('/update_data', methods=['POST'])
def update_data():
    global received_data
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    #update the received_data dictionary
    received_data.update(data)

    #extract the data
    dht22_temp = data['dht22_temp']
    dht22_hum = data['dht22_hum']
    lm35 = data['lm35']

    if not all([dht22_temp, dht22_hum, lm35]):
        return jsonify({"error": "Missing required data"}), 400
    #add the data to the database  
    add_entry(dht22_temp,dht22_hum,lm35)

    #send a response
    return jsonify({"message": "Data received successfully", "data": data}), 200


#adds the data to the database
def add_entry(dht22_temp,dht22_hum,lm35):
    time_format = datetime.now().strftime("%Y-%m-%d/%H:%M")
    new_data = sensor_data(dht22_temp=dht22_temp, dht22_hum=dht22_hum, lm35=lm35, time_stamp=time_format)
    db.session.add(new_data)
    db.session.commit()


#data_view page
@app.route('/data_view')
def data_view():
    return render_template('data_view.html')
    
#gets the data from the database and returns it as a JSON object, only the last 24 hours of data
@app.route('/get_sensor_data', methods=['GET'])
def get_sensor_data():
    #get the latest entry by time_stamp
    timeStamp = sensor_data.query.order_by(sensor_data.entry.desc()).first().time_stamp
    if timeStamp is None:
        print("No entries found in the sensor_data table.")
        return jsonify({"error": "No entries found"}), 404
    #make sure it is in the correct format
    timeStamp = datetime.strptime(timeStamp, "%Y-%m-%d/%H:%M")

    #get the time 24 hours ago
    oneDay = timeStamp - timedelta(days=1)

    validEntries = []
    
    #filtes the data to only include the last 24 hours
    sensor_entries = sensor_data.query.filter(sensor_data.time_stamp >= oneDay).order_by(sensor_data.entry.asc()).all()
    if not sensor_entries:
        print("No entries found within the last 24 hours.")

    #adds the data to the validEntries list
    for entry in sensor_entries:
        validEntries.append({"dht22_temp": entry.dht22_temp, "dht22_hum": entry.dht22_hum, "lm35": entry.lm35, "time_stamp": entry.time_stamp})
    
    if not validEntries:
        print("No valid entries found.")
    
    #returns the data as a JSON object
    return jsonify(validEntries)


@app.route('/test')
def test():
    return render_template('test.html')


#gets the last 24 hours in hour intervals
@app.route('/get_past_time', methods=['GET'])
def get_past_time():
    latest_entry = sensor_data.query.order_by(sensor_data.entry.desc()).first()
    timeStamp = latest_entry.time_stamp
    timeStamp = datetime.strptime(timeStamp, "%Y-%m-%d/%H:%M")
    time_marks = []

    #gets each hour mark
    for i in range(24):
        time_marks.append((timeStamp - timedelta(hours=i)).hour)
    #reverse the list to get the hours from oldest to newest
    time_marks.reverse()
    #return the list as a JSON object
    return jsonify(time_marks)
