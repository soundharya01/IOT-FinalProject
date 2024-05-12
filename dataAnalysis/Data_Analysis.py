# Importing relevant modules
import joblib
import pandas as pd
from flask import Flask, jsonify
from paho.mqtt.client import Client as MqttClient
from dotenv import load_dotenv
import os
import json

# Load the trained model
knn_model = joblib.load('knn_model.pkl')
model_columns = joblib.load("knn_model_columns.pkl")

# Load environment variables from ".env"
load_dotenv()

# MQTT config
MQTT_BROKER = os.environ.get('MQTT_URL')
MQTT_TOPIC = os.environ.get('MQTT_PUBLISH_TOPIC')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))

# Create Flask app
app = Flask(__name__)

# Create MQTT client
mqtt_client = MqttClient(client_id="FlaskClient")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

# Callback function for MQTT message
def on_message(client, userdata, message):
    try:
        # Decode message payload
        json_data = json.loads(message.payload.decode('utf-8'))
        # Convert JSON data to DataFrame
        query = pd.DataFrame([json_data])
        # Extract features from data
        feature_sample = query[model_columns]
        # Predict using the model
        predict_sample = knn_model.predict(feature_sample)
        print("Predicted BMP280Temperature:", predict_sample[0])

        # Optionally, you can save the predicted value to a database or return it as JSON
        # For example, to return as JSON:
        prediction_response = {"Predicted BMP280Temperature": float(predict_sample[0])}
        app.response_class(response=json.dumps(prediction_response), status=200, mimetype='application/json')

    except Exception as e:
        # Handle errors
        print("Error:", str(e))

# Set MQTT client callback
mqtt_client.on_message = on_message
mqtt_client.subscribe(MQTT_TOPIC)
mqtt_client.loop_start()

if __name__ == '__main__':
    app.run(debug=False)
