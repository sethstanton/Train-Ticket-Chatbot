
import requests

# Function to fetch train departure details
def fetch_train_departures(source, destination):
    # Set up your API credentials and endpoint
    app_id = '8842e8f5'
    app_key = '53e0a655551e596f087ad503c9493fef'
    url = f"https://transportapi.com/v3/uk/train/station/{source}/live.json"

    # Parameters for the API request
    params = {
        'app_id': app_id,
        'app_key': app_key,
        'calling_at': destination,
        'darwin': 'false',
        'train_status': 'passenger'
    }

    # Making the API request
    response = requests.get(url, params=params)
    data = response.json()

    return data

# Function to print train departure details in a readable format
def display_departure_details(data):
    if 'departures' in data and 'all' in data['departures']:
        print(f"Train departures from {data['station_name']} (Station Code: {data['station_code']}):")
        for departure in data['departures']['all']:
            print(f"Train to {departure['destination_name']}")
            print(f"  Train UID: {departure['train_uid']}")
            print(f"  Platform: {departure['platform']}")
            print(f"  Operator: {departure['operator_name']}")
            print(f"  Aimed Departure Time: {departure['aimed_departure_time']}")
            print(f"  Status: {departure['status']}")
            print(f"  Departure Estimate: {departure.get('best_departure_estimate_mins', 'No estimate available')} minutes")
            print("-" * 40)
    else:
        print("No departures available or data missing.")

# Main program
def main():
    # User input
    source = input("Enter the source station code: ")
    destination = input("Enter the destination station code: ")

    # Fetch train departures
    departures_data = fetch_train_departures(source, destination)

    # Display the train departures
    display_departure_details(departures_data)

if __name__ == "__main__":
    main()