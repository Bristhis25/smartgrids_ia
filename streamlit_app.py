import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

# Step 1: Simulate or Load Energy Data
# For simplicity, we simulate a dataset with features like temperature, time of day, and energy demand.
np.random.seed(42)
data_size = 1000
data = {
    "Temperature": np.random.uniform(0, 40, data_size),  # Temperature in Celsius
    "HourOfDay": np.random.randint(0, 24, data_size),    # Hour of the day (0-23)
    "DayOfWeek": np.random.randint(0, 7, data_size),     # Day of the week (0=Monday, 6=Sunday)
    "EnergyDemand": np.random.uniform(50, 500, data_size)  # Simulated energy demand in kWh
}
df = pd.DataFrame(data)

# Step 2: Preprocess the Data
X = df[["Temperature", "HourOfDay", "DayOfWeek"]]  # Features
y = df["EnergyDemand"]  # Target variable

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 3: Train a Machine Learning Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 4: Make Predictions
y_pred = model.predict(X_test)

# Step 5: Evaluate the Model
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")

# Step 6: Visualize Predictions vs Actual Values
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.7, color="blue")
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color="red", linestyle="--")
plt.xlabel("Actual Energy Demand (kWh)")
plt.ylabel("Predicted Energy Demand (kWh)")
plt.title("Actual vs Predicted Energy Demand")
plt.show()
