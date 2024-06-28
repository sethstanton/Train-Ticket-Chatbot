import os

SUB_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

past_inputs = os.path.join(SUB_BASE_DIR, 'ticketfinder', 'data', 'past_inputs.csv')
data_path = os.path.join(SUB_BASE_DIR, 'ticketfinder', 'data', 'data.json')
reset_path = os.path.join(SUB_BASE_DIR, 'ticketfinder', 'data', 'reset.json')

intentions_path = os.path.join(SUB_BASE_DIR, 'ticketfinder', 'data', 'intentions.json')
sentences_path = os.path.join(SUB_BASE_DIR, 'ticketfinder', 'data', 'sentences.txt')
stations_path = os.path.join(SUB_BASE_DIR, 'ticketfinder', 'data', 'stations.csv')

pred_data_path = os.path.join(SUB_BASE_DIR, 'ticketfinder', 'data', 'pred_data.json')
pred_reset_path = os.path.join(SUB_BASE_DIR, 'ticketfinder', 'data', 'pred_reset.json')
pred_stations_path = os.path.join(SUB_BASE_DIR, 'ticketfinder', 'data', 'pred_stations.csv')

pred_dataset_path = os.path.join(SUB_BASE_DIR, 'ticketfinder', 'train_data_clean', 'train_data_combined_with_id.csv')
