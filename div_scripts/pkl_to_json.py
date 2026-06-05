import os
import pickle
import json

def convert_pickle_to_json(pickle_file_path, json_file_path):
    # Load data from pickle file
    with open(pickle_file_path, 'rb') as pickle_file:
        data = pickle.load(pickle_file)

    # Write data to JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file)

def convert_all_pickles_in_dir(dir_path):
    for filename in os.listdir(dir_path):
        if filename.endswith('.pkl'):
            pickle_file_path = os.path.join(dir_path, filename)
            json_file_path = os.path.join(dir_path, filename.replace('.pkl', '.json'))
            convert_pickle_to_json(pickle_file_path, json_file_path)

# Usage
convert_all_pickles_in_dir(r'C:\Users\jdr\OneDrive - Multiconsult\Skrivebord\10245026-01_ep_H1_3\pkl')