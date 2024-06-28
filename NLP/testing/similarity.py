from fuzzywuzzy import process
import pandas as pd

# Function to find the top 5 matching station names
df = pd.read_csv('data/stations.csv')
df['combined'] = df['name'] + ' ' + df['longname.name_alias']




def find_similar_stations(target, df):
    station_names = [(name,idx) for idx, name in enumerate(df['combined'])]
    top_matches = process.extract(target, station_names, limit=5)

    results = [{'matched station': match[0][0], 'similarity score': match[1],
                'index': i+1, 'original index': match[0][1]} for i, match in enumerate(top_matches)]
    return results


# Main function to drive the program
def station_selector(target_station):
    # Replace 'your_spreadsheet.xlsx' with the path to your spreadsheet
    similar_stations = find_similar_stations(target_station, df)

    for station in similar_stations:
        print(f"{station['index']} Station: {station['matched station']}, Similarity Score: {station['similarity score']}")

    selected_station = int(input("Enter the index of the station you want to select: "))

    station_df_index = similar_stations[selected_station-1]['original index']
    station_name = df.iloc[station_df_index]['name']
    station_tiploc = df.iloc[station_df_index]['tiploc']

    return station_name, station_tiploc


# Run the program
if __name__ == "__main__":
    target_station = input("Enter the name of the station you want to search for: ")
    station_name, station_tiploc = station_selector(target_station)

    print(f"Selected Station: {station_name}, Tiploc: {station_tiploc}")
