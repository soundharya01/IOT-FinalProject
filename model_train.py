import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Load the dataset
df = pd.read_csv('train_set.csv')
df.drop(columns=['time'], axis=1, inplace=True)

# Define the features and target
features = ['SHT4xTemperature', 'SHT4xHumidity', 'BMP280Pressure']   # Features excluding BMP280Temperature
target = 'BMP280Temperature'  # Use BMP280Temperature as the target variable

# Split the data into features (X) and target (y)
X = df[features]
y = df[target]

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Initialize and train the KNN regressor model
knn_model = KNeighborsRegressor(n_neighbors=3, weights='distance')  # Use KNeighborsRegressor for regression
knn_model.fit(X_train, y_train)

# Validate the model performance on the test set
y_pred = knn_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print("Mean Squared Error:", mse)
print("R-squared Score:", r2)

# Plot actual vs predicted values
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, color='blue')
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], linestyle='--', color='red', linewidth=2)
plt.xlabel('Actual BMP280Temperature')
plt.ylabel('Predicted BMP280Temperature')
plt.title('Actual vs Predicted BMP280Temperature')
plt.show()

# Export the trained model for later use
joblib.dump(features, 'knn_model_columns.pkl')
joblib.dump(knn_model, 'knn_model.pkl')
print('Model and columns dumped')
