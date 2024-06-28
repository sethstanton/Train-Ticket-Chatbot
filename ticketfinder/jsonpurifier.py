import json
from .config import (data_path, pred_data_path)


def purify_json():
    """
    Resets the JSON file to a default state with predefined keys and values.

    Args:
    file_path (str): The path to the JSON file to clear.
    """
    default_data = {
    "chosen_origin_str": "Norwich",
    "chosen_dest_str": None,
    "arrive_date_str": None,
    "arrive_time_str": None,
    "leave_date_str": None,
    "leave_time_str": None,
    "ticket_type": None,
    "leave_arrive": None,
    "origin_code": "NRW",
    "dest_code": None,
    "chosen_intention": None,
    "flag_loc": 0,
    "station_selector": False,
    "station1" : None,
    "station2" : None,
    "station3" : None,
    "station4" : None,
    "station5" : None,
    "selected": None
}

    try:
        with open(data_path, 'w') as file:
            json.dump(default_data, file, indent=4)  
        print("JSON file has been reset to default.")
    except Exception as e:
        print(f"An error occurred: {e}")

def purify_pred_json():
    """
    Resets the JSON file to a default state with predefined keys and values.

    Args:
    file_path (str): The path to the JSON file to clear.
    """
    default_data = {
        "chosen_origin_str": None,
        "chosen_dest_str": None,
        "date_str": None,
        "time_str": None,

        "delay": None,
        "current_station": None,
        "pred_type": None,

        "origin_code": None,
        "dest_code": None,
        "current_code": None,

        "flag_loc": 0,
        "pred_station_selector": False,
        "pred_station1": None,
        "pred_station2": None,
        "pred_selected": None
}

    try:
        with open(pred_data_path, 'w') as file:
            json.dump(default_data, file, indent=4)  
        print("JSON file has been reset to default.")
    except Exception as e:
        print(f"An error occurred: {e}")


