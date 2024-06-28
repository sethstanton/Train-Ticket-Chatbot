import pandas as pd
import os

csv = 'train_data_combined.csv'

data = pd.read_csv(csv)

data['ID'] = 0

current_id = 0
for i in range(len(data)):
    if data.iloc[i]['tpl'] == 'LIVST':
        current_id += 1
    data.at[i, 'ID'] = current_id

data = data[['ID'] + data.columns[:-1].tolist()]

data.head()

data.to_csv('train_data_combined_with_id.csv', index=False)
