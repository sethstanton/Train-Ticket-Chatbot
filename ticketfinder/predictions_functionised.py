import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from datetime import datetime

from .utils import get_train_data

def load_and_clean_data():
    """
    Load and clean the training dataset from a source, process various data types, and prepare it for analysis.
    
    The function fetches data, parses datetime fields, drops unnecessary columns, converts codes to numeric values,
    and imputes missing values for numeric columns. It outputs the cleaned DataFrame with the modified schema.
    
    Steps included:
    - Fetch data into a DataFrame.
    - Parse specified datetime columns to datetime format, coercing errors.
    - Drop columns that are not required or are mostly empty.
    - Convert specific code columns to numeric types, filling missing values with 0.
    - Impute missing values in numeric columns using the median of each column.

    :return: Cleaned pandas DataFrame ready for further analysis, with unnecessary columns removed and data types properly formatted.
"""
    data = pd.DataFrame(list(get_train_data()))
    print("Data fetched and initial types:\n", data.dtypes)  

    time_columns = ['wtp', 'wtd', 'pass_at', 'pta', 'ptd', 'arr_at', 'dep_at']  
    for col in time_columns:
        data[col] = pd.to_datetime(data[col], errors='coerce', format='%H:%M:%S')  

    columns_to_drop = ['arr_et', 'arr_wet', 'dep_et', 'dep_wet', 'pass_wet']  
    data.drop(columns=columns_to_drop, inplace=True)

    for col in ['cr_code', 'lr_code']:
        data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

    numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
    if numeric_columns:
        imputer = SimpleImputer(strategy='median')
        data[numeric_columns] = imputer.fit_transform(data[numeric_columns])

    print("Data types after processing:\n", data.dtypes)  
    return data

def calculate_features(data):
    """
    Calculate time-based and boolean features for a dataset. This function processes the input DataFrame by computing
    delay durations and converting boolean values to integer flags.

    Steps included:
    - Compute the 'arrival_delay' by calculating the difference between 'arr_at' and 'pta', then converting the result to minutes.
    - Compute the 'departure_delay' by calculating the difference between 'dep_at' and 'ptd', then converting the result to minutes.
    - Convert boolean columns indicating item removal (like 'arr_removed', 'pass_removed') into integer flags for analytical convenience.

    :param data: pandas DataFrame containing the train data with columns for arrival and departure times.
    :return: pandas DataFrame with additional features like delays and flags added, suitable for further analysis.
"""
    if 'arr_at' in data.columns and 'pta' in data.columns:
        data['arrival_delay'] = (data['arr_at'] - data['pta']).dt.total_seconds() / 60
    if 'dep_at' in data.columns and 'ptd' in data.columns:
        data['departure_delay'] = (data['dep_at'] - data['ptd']).dt.total_seconds() / 60

    for col in ['arr_removed', 'pass_removed']:
        data[col + '_flag'] = data[col].astype(int)

    print("Features calculated successfully. Data preview:\n", data.head())
    return data

def train_and_evaluate(data):
    """
    Train and evaluate a RandomForest model on numeric features from the provided dataset. This function processes
    the input DataFrame by handling missing values, standardising features, and preparing data splits for training
    and testing. It then trains a RandomForestRegressor, makes predictions, and evaluates the results using mean squared
    error (MSE), mean absolute error (MAE), and root mean squared error (RMSE).

    Steps included:
    - Handle missing values in numeric columns using median imputation.
    - Standardise features to have a mean of zero and a standard deviation of one.
    - Split the dataset into training and testing sets.
    - Train a RandomForestRegressor model on the training data.
    - Predict the target on the testing data.
    - Calculate and return the model's MSE, MAE, and RMSE.

    :param data: pandas DataFrame containing the dataset with at least one numeric column and the target column 'arrival_delay'.
    :return: Tuple containing the trained model, MSE, MAE, and RMSE of the predictions on the test set.
    
    :raises ValueError: If the input data is empty or lacks a valid target column.
"""
    if data.empty:
        raise ValueError("No data available for training.")

    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()

    if numeric_cols:
        imputer = SimpleImputer(strategy='median')
        data[numeric_cols] = imputer.fit_transform(data[numeric_cols])

    X = data[numeric_cols]  
    y = data['arrival_delay'] if 'arrival_delay' in data.columns else None

    if y is None or y.isna().all():
        raise ValueError("No valid target data for model training.")

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mse)

    return model, mse, mae, rmse

def visualise_data(data):
    """
    Visualise the distribution and average delays of arrival and departure times in the dataset. This function
    creates histograms to display the frequency distribution of arrival and departure delays, followed by bar charts
    showing the average delays by station.

    Steps included:
    - Plot histograms of arrival and departure delays to show their distribution.
    - Calculate and plot the average arrival and departure delays by station using bar charts.

    The visualisations are displayed in two separate figures, each containing two subplots for clarity and detail.

    :param data: pandas DataFrame containing 'arrival_delay', 'departure_delay', and 'tpl' columns.
"""
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))
    data['arrival_delay'].dropna().hist(bins=50, ax=axes[0], color='skyblue')
    axes[0].set_title('Distribution of Arrival Delays (in minutes)')
    axes[0].set_xlabel('Minutes')
    axes[0].set_ylabel('Frequency')
    data['departure_delay'].dropna().hist(bins=50, ax=axes[1], color='lightgreen')
    axes[1].set_title('Distribution of Departure Delays (in minutes)')
    axes[1].set_xlabel('Minutes')
    axes[1].set_ylabel('Frequency')
    plt.tight_layout()
    plt.show()
    avg_arrival_delays = data.groupby('tpl')['arrival_delay'].mean()
    avg_departure_delays = data.groupby('tpl')['departure_delay'].mean()
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))
    avg_arrival_delays.sort_values().plot(kind='bar', ax=axes[0], color='skyblue')
    axes[0].set_title('Average Arrival Delays by Station')
    axes[0].set_xlabel('Station')
    axes[0].set_ylabel('Average Delay (minutes)')
    axes[0].tick_params(labelrotation=90)
    avg_departure_delays.sort_values().plot(kind='bar', ax=axes[1], color='lightgreen')
    axes[1].set_title('Average Departure Delays by Station')
    axes[1].set_xlabel('Station')
    axes[1].set_ylabel('Average Delay (minutes)')
    axes[1].tick_params(labelrotation=90)
    plt.tight_layout()
    plt.show()
