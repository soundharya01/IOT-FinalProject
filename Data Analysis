import os

# Set the path to the git executable
os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = r'C:\Program Files\Git\cmd\git.exe'

import git
from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

app = Flask(__name__)

# InfluxDB Credentials
INFLUXDB_URL = 'https://iot-group6-service1.iotcloudserve.net'
TOKEN = 'anC4AQca7Tu9XCxJn7l983g1at2JcBYyQ-x482LeIbUqsUI7LanQWdxxu8bjou13V_813n5JR4ZN8Ik2KUOzTA=='
ORG = 'Group_6'
BUCKET = 'Group_6'

# Initialize InfluxDB client
influxdb_client = InfluxDBClient(url=INFLUXDB_URL, token=TOKEN)

# Initialize an empty DataFrame to store sensor data
sensor_data = pd.DataFrame(
    columns=['SHT4xTemperature', 'SHT4xHumidity', 'BMP280Temperature', 'BMP280Pressure', 'target_variable'])

# Route for handling GET requests for fetching data from InfluxDB
@app.route('/get_data', methods=['GET'])
def get_data():
    query = f'from(bucket: "{BUCKET}") |> range(start: -1h)'
    result = influxdb_client.query_api().query(query, org=ORG)
    data = result.to_dataframe()
    return jsonify(data.to_dict())

# Route for handling POST requests for adding data
@app.route('/add_data', methods=['POST'])
def add_data():
    global sensor_data
    req_data = request.get_json()
    if req_data:
        sensor_data = sensor_data.append(req_data, ignore_index=True)
        return jsonify({"message": "Data added successfully"})
    else:
        return jsonify({"error": "No data provided"}), 400


# Route for training machine learning model
@app.route('/train_model', methods=['POST'])
def train_model():
    global sensor_data
    if len(sensor_data) >= 100:
        # Load your dataset from CSV
        dataset = pd.read_csv("BMP_temp.csv")

        # Assuming your dataset has columns "time" and "BMP280_temp"
        # Convert "time" to datetime format
        dataset['time'] = pd.to_datetime(dataset['time'])

        # Sort dataset by time (if not already sorted)
        dataset.sort_values(by='time', inplace=True)

        # Assuming you want to keep the latest 500 records
        dataset = dataset.tail(500)

        # Drop any rows with missing values
        dataset.dropna(inplace=True)

        # Extract features and target variable
        x_label = np.array(dataset['BMP280_temp']).reshape(-1, 1)
        y_label = np.array(dataset['target_variable']).reshape(-1, 1)  # You need to define the target variable

        # Split dataset into train and test sets
        x_train, x_test, y_train, y_test = train_test_split(x_label, y_label, test_size=0.2, random_state=100)

        # Initialize and train linear regression model
        regression_model = LinearRegression()
        regression_model.fit(x_train, y_train)

        # Save the trained model
        joblib.dump(regression_model, 'regression_model.pkl')

        # Save the columns used by the model (if needed)
        regression_model_columns = ['BMP280_temp']  # Adjust accordingly
        joblib.dump(regression_model_columns, 'regression_model_columns.pkl')

        # Define objectives for the analysis
        objectives = "To predict T_degC based on BMP280 temperature readings."

        # Initialize Git repository (if needed)
        # repo = git.Repo.init('.')
        # git_repo = git.Git(repo.working_dir)
        # git_repo.add(all=True)
        # git_repo.commit('-m', 'Trained linear regression model and defined objectives.')

        return jsonify({"message": "Model trained successfully", "objectives": objectives}), 200
    else:
        return jsonify({"error": "Insufficient data for training"}), 400

# Route for real-time predictions
@app.route('/predict', methods=['POST'])
def predict():
    global sensor_data
    req_data = request.get_json()
    if req_data:
        new_data = pd.DataFrame(req_data, index=[0])  # Convert request data to DataFrame
        X_new = new_data.drop(columns=['target_variable'])  # Extract features
        # Load the trained model from disk
        model = joblib.load('regression_model.pkl')  # Load your trained model here
        # Make predictions
        predictions = model.predict(X_new)
        return jsonify({"predictions": predictions.tolist()}), 200
    else:
        return jsonify({"error": "No data provided"}), 400

if __name__ == '__main__':
    app.run()
