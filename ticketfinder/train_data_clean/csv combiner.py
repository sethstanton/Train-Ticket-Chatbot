import pandas as pd
import os

csv_directory = r'C:\Users\ryanl\Documents\Artificial Intelligence\AI project\AI-project\AICW2\mychatbots\ticketfinder\train_data_clean'

csv_files = [file for file in os.listdir(csv_directory) if file.endswith('.csv')]

dataframes = []

# Loop through the CSV files and read each one into a dataframe
for file in csv_files:
    file_path = os.path.join(csv_directory, file)
    df = pd.read_csv(file_path)
    dataframes.append(df)

# Concatenate all dataframes into a single dataframe
cdf = pd.concat(dataframes, ignore_index=True)

cdf.to_csv('train_data_combined.csv', index=False)