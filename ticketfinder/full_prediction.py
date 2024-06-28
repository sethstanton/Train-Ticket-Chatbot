import pandas as pd
from .config import (pred_dataset_path)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load data from CSV
def load_data(file_path):
    return pd.read_csv(file_path)

# Preprocess the data
def preprocess_data(data):
    # Convert time columns to datetime
    data['pta'] = pd.to_datetime(data['pta'], format='%H:%M:%S', errors='coerce')
    data['ptd'] = pd.to_datetime(data['ptd'], format='%H:%M:%S', errors='coerce')
    data['arr_at'] = pd.to_datetime(data['arr_at'], format='%H:%M:%S', errors='coerce')
    data['dep_at'] = pd.to_datetime(data['dep_at'], format='%H:%M:%S', errors='coerce')
    
    # Fill missing time values
    data['pta'].fillna(pd.to_datetime('00:00:00', format='%H:%M:%S'), inplace=True)
    data['ptd'].fillna(pd.to_datetime('00:00:00', format='%H:%M:%S'), inplace=True)
    data['arr_at'].fillna(pd.to_datetime('00:00:00', format='%H:%M:%S'), inplace=True)
    data['dep_at'].fillna(pd.to_datetime('00:00:00', format='%H:%M:%S'), inplace=True)
    
    # Extract hour and minute from time columns
    for col in ['pta', 'ptd', 'arr_at', 'dep_at']:
        data[col + '_hour'] = data[col].dt.hour
        data[col + '_minute'] = data[col].dt.minute
    
    # Drop original datetime columns
    data.drop(columns=['pta', 'ptd', 'arr_at', 'dep_at'], inplace=True)
    
    # Handle missing values in numeric columns
    numeric_cols = data.select_dtypes(include='number').columns
    data[numeric_cols] = data[numeric_cols].fillna(0)
    
    # Filter rows with dep_delay > 5 minutes (0.083333 hours)
    data = data[data['dep_delay'] > 0.083333]
    
    return data

# Train the Ridge regression model
def train_model(data):
    # Define features and target variable
    features = ['tpl', 'pta_hour', 'pta_minute', 'ptd_hour', 'ptd_minute', 'arr_delay', 'dep_delay']
    target = 'arr_delay'
    
    # Encode categorical variables
    data = pd.get_dummies(data, columns=['tpl'], drop_first=True)
    
    # Ensure features are in the dataframe
    features = [col for col in features if col in data.columns]
    
    # Split the data into training and testing sets
    X = data[features]
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and fit the Ridge regressor with polynomial features
    poly = PolynomialFeatures(degree=2, include_bias=False)
    scaler = StandardScaler()
    model = Ridge()
    
    # Create a pipeline
    pipeline = make_pipeline(poly, scaler, model)
    pipeline.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = pipeline.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    #print(f"Mean Squared Error: {mse}")
    
    return pipeline, features

# Predict the delay with added variability for realism
def predict_delay(model, current_station, dep_delay, feature_columns):
    # Create a sample input data
    input_data = {
        'tpl': current_station,
        'dep_delay': dep_delay,
        'pta_hour': 0, 
        'pta_minute': 0,
        'ptd_hour': 0,
        'ptd_minute': 0,
        'arr_delay': 0
    }
    
    # Convert to DataFrame and encode categorical variables
    input_df = pd.DataFrame([input_data])
    input_df = pd.get_dummies(input_df, columns=['tpl'], drop_first=True)
    
    # Ensure the input data has the same columns as the training data
    for col in feature_columns:
        if col not in input_df.columns:
            input_df[col] = 0
    
    # Predict the delay
    predicted_delay = model.predict(input_df[feature_columns])[0]
    
    # Convert delay from decimal hours to minutes and add variability
    predicted_delay_minutes = (predicted_delay * 60) * np.random.uniform(1, 1.5)
    predicted_delay_minutes = max(dep_delay, min(dep_delay*2.5, predicted_delay_minutes))
    
    return predicted_delay_minutes

# Main function to load, preprocess, train, and predict
def pred_model_main(current_station, dest_station, dep_delay):
    #file_path = '/content/train_data_combined_with_id.csv'
    #file_path = '.train_data_clean/train_data_combined_with_id.csv'
    file_path = pred_dataset_path
    data = load_data(file_path)
    data = preprocess_data(data)
    model, feature_columns = train_model(data)
    
    # Example prediction
    current_station = 'LIVST'
    dest_station = 'NRCH'
    dep_delay = 0.5
    delay_prediction = predict_delay(model, current_station, dep_delay, feature_columns)
    return delay_prediction
    print(f'Predicted delay at {dest_station}: {delay_prediction:.2f} hours')

if __name__ == "__main__":
    current_station = 'LIVST'
    dest_station = 'NRCH'
    dep_delay = 0.1
    dep_delay1 = 0.3
    dep_delay2 = 0.5
    dep_delay3 = 0.7
    dep_delay4 = 1
    dep_delay5 = 2
    dep_delay6 = 5
    print(pred_model_main(current_station, dest_station, dep_delay))
    print(pred_model_main(current_station, dest_station, dep_delay1))
    print(pred_model_main(current_station, dest_station, dep_delay2))
    print(pred_model_main(current_station, dest_station, dep_delay3))
    print(pred_model_main(current_station, dest_station, dep_delay4))
    print(pred_model_main(current_station, dest_station, dep_delay5))
    print(pred_model_main(current_station, dest_station, dep_delay6))


