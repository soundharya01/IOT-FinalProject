# Concumner code
# Importing relevant modules
import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS
import paho.mqtt.client as mqtt
import json
import requests

# Load environment variables from ".env"
load_dotenv()

# InfluxDB config
INFLUXDB_URL = os.environ.get('https://iot-group6-service1.iotcloudserve.net')
TOKEN = os.environ.get('anC4AQca7Tu9XCxJn7l983g1at2JcBYyQ-x482LeIbUqsUI7LanQWdxxu8bjou13V_813n5JR4ZN8Ik2KUOzTA==')
ORG = os.environ.get('Group_6')
BUCKET = os.environ.get('Group_6')
client = InfluxDBClient(url=INFLUXDB_URL, token=TOKEN, org=ORG)
write_api = client.write_api('ELl32AOEoIN3PjZk-xdUzHVpqCjL7Xfvu8TYUUVRTknAhxOkB5kbjs7uxMiwRkwgmBVkIsQsi88jWjGcPd0Caw==')

# MQTT broker config
MQTT_BROKER_URL = os.environ.get('192.168.26.66')
MQTT_PUBLISH_TOPIC = os.environ.get('@shadow/data/update')
mqttc = mqtt.Client()

# REST API endpoint for predicting output
PREDICT_URL = os.environ.get('https://iot-group6-service1.iotcloudserve.net/add_data')

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client connects to the broker."""
    print("Connected with result code "+str(rc))

# Subscribe to a topic
mqttc.subscribe(MQTT_PUBLISH_TOPIC)

def on_message(client, userdata, msg):
    """ The callback for when a PUBLISH message is received from the server."""
    print(msg.topic+" "+str(msg.payload))

    # Write data to InfluxDB
    payload = json.loads(msg.payload)
    write_to_influxdb(payload)

    # POST data to predict the output label
    json_data = json.dumps(payload)
    post_to_predict(json_data)

# Function to post to real-time prediction endpoint
def post_to_predict(data):
    response = requests.post(PREDICT_URL, data=data)
    if response.status_code == 200:
        print("POST request successful")
    else:
        print("POST request failed!", response.status_code)

# Function to write data to InfluxDB
def write_to_influxdb(data):
    # Construct JSON string with sensor data
    sensor_data = {
        "SHT4xTemperature": data["SHT4xTemperature"],
        "SHT4xHumidity": data["SHT4xHumidity"],
        "BMP280Temperature": data["BMP280Temperature"],
        "BMP280Pressure": data["BMP280Pressure"]
    }
    json_data = {"data": sensor_data}
    json_string = json.dumps(json_data)

    # Write data to InfluxDB
    write_api.write(BUCKET, ORG, json_string)

## MQTT logic - Register callbacks and start MQTT client
mqttc.on_connect = on_connect
mqttc.on_message = on_message

try:
    mqttc.connect(MQTT_BROKER_URL, 1883)
    print("Connected to MQTT Broker")
except Exception as e:
    print("Failed to connect to MQTT Broker:", e)

mqttc.loop_forever()