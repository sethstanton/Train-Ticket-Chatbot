from .NLP_functions import *
from .full_prediction import *
from datetime import datetime, timedelta
import pandas as pd
from fuzzywuzzy import process

nlp = spacy.load("en_core_web_sm")

pdf = pd.read_csv(pred_stations_path)
pdf['combined'] = pdf['name'] + ' ' + pdf['longname.name_alias']



multiple_loc = False

# The stations.csv file contains another column which we have labelled as 'Bad' which contains the extended name of the station
# This function is used to convert the tiploc code to the extended name of the station, as the extended name is used for the prediction model
def tiploc_to_extended_name(tiploc):
    result = pdf.loc[pdf['tiploc'] == tiploc, 'Bad']
    if not result.empty:
        return result.iloc[0]
    return None

# This function is used to give a response to the user if the user has not provided all the necessary information for the prediction
# The user is asked to provide the missing information in order to make a prediction.
# If the user has provided all the necessary information, the prediction is made and the user is given the prediction
def pred_missing_info_response():
    global final_chatbot
    global printout

    if pd_data['chosen_dest_str'] is not None and pd_data['current_station'] is not None and pd_data['delay'] is not None:
        pd_data['date_str'] = date_conversion("today")
        pd_data['time_str'] = time_conversion("now")
        printout.append("You want to predict for a train journey that you are currently on, at the moment you are at " + pd_data['current_station'] + " and you are experiencing a delay of " + str(pd_data['delay']) + " minutes.")
        if final_chatbot:
            curr_stat = tiploc_to_extended_name(pd_data['current_code'])
            dest_stat = tiploc_to_extended_name(pd_data['dest_code'])

            prediction = pred_model_main(curr_stat, dest_stat, pd_data['delay'])
            pred_secs = prediction * 3600
            pred_time_short = round(prediction, 2)
            pred_time = datetime.now() + timedelta(seconds=pred_secs)
            pred_time_str = pred_time.strftime("%H:%M")
            printout.append("The predicted delay at " + pd_data['chosen_dest_str'] + " is " + str(pred_time_short) + " hours, which is expected to arrive at " + pred_time_str + ".")
            printout.append("If you don't have any other questions you can type bye.")

    if pd_data['current_station'] is None:
        printout.append("Please tell me the station you are currently at.")

    if pd_data['chosen_dest_str'] is None:
        printout.append("Please tell me the station you want to travel to.")

    if pd_data['delay'] is None:
        printout.append("Please tell me the delay you are experiencing.")

# This function is used to find the top 2 stations that are similar to the station that the user has entered
def pred_similar_stations(target):
    global pdf
    station_names = [(name,idx) for idx, name in enumerate(pdf['combined'])]
    top_matches = process.extract(target, station_names, limit=2)

    results = [{'matched station': match[0][0], 'similarity score': match[1],
                'index': i+1, 'original index': match[0][1]} for i, match in enumerate(top_matches)]
    return results

# This function is used to return the top 2 stations that are similar to the station that the user has entered
def pred_station_selector(target_station):
    pd_data['pred_station_selector'] = True
    with open(pred_data_path, 'w') as file:
        json.dump(pd_data, file, indent=4)

    global printout
    global pdf

    similar_stations = pred_similar_stations(target_station)
    printout.append("Did you mean one of these stations? (Please enter the index of the station you want to select)")

    for station in similar_stations:
        printout.append(f"{station['index']} Station: {station['matched station']}")
        pd_data[f"pred_station{station['index']}"] = similar_stations[station['index'] - 1]['original index']

    with open(pred_data_path, 'w') as file:
        json.dump(pd_data, file, indent=4)

# This function is used to convert the input response from the user to the station that the user has selected
def pred_selected_station(selected_station):
    pd_data['pred_station_selector'] = False
    with open(pred_data_path, 'w') as file:
        json.dump(pd_data, file, indent=4)
    station_pdf_index = pd_data[f'pred_station{selected_station}']
    station_name = pdf.iloc[station_pdf_index]['name']
    station_tiploc = pdf.iloc[station_pdf_index]['tiploc']

    for i in range (1, 3):
        pd_data[f'pred_station{i}'] = None
    with open(pred_data_path, 'w') as file:
        json.dump(pd_data, file, indent=4)

    return station_name, station_tiploc


# This is essentially the main function that is used to predict the delay of a train journey
def pred_ner_response(user_input):



    doc = nlp(user_input)
    chosen_dest = []
    chosen_time = []
    chosen_cur_stat = []
    global printout

    # First we check if the user has entered any entities and then we check if the entities are of the correct type
    # and then we store the entities in the correct variables
    if any(doc.ents):
        for ent in doc.ents:
            ent_index = ent.start
            if doc[ent_index - 1].text.lower() == "from" or doc[ent_index - 1].text.lower() == "at":
                if ent.label_ in loc_types:
                    chosen_cur_stat.append(ent.text)
            if doc[ent_index - 1].text.lower() == "to":
                if ent.label_ in loc_types:
                    chosen_dest.append(ent.text)
            if ent.label_ == "TIME":
                chosen_time.append(ent.text)

        # If the user has entered a location, we raise a flag to indicate that the user has entered a location
        # and then find the top 2 stations that are similar to the station that the user has entered
        # We then ask the user to select the station that they want to choose
        # after the user has selected the station, we convert the input response from the user to the station that the user has selected
        # We then store the station that the user has selected in the correct variable

        # Then we continue the process for the original user input and check if the user has entered a time or destination

        if chosen_cur_stat != [] and pd_data['flag_loc'] < 1:
            pd_data['flag_loc'] = 1
            pd_data['current_station'] = " ".join(chosen_cur_stat)
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)
            pred_station_selector(pd_data['current_station'])
            return printout.insert(0, True)

        if pd_data['pred_station_selector'] and pd_data['flag_loc'] == 1:
            pd_data['current_station'], pd_data['current_code'] = pred_selected_station(pd_data['pred_selected'])
            pd_data['flag_loc'] = 0
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)
            printout.append(
                "" + "You want to predict for a train journey that you are currently on, at the moment you are at " +
                pd_data['current_station'] + ".")

        if chosen_dest != [] and pd_data['flag_loc'] < 2:
            pd_data['flag_loc'] = 2
            pd_data['chosen_dest_str'] = " ".join(chosen_dest)
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)
            pred_station_selector(pd_data['chosen_dest_str'])
            return printout.insert(0, True)

        if pd_data['pred_station_selector'] and pd_data['flag_loc'] == 2:
            pd_data['chosen_dest_str'], pd_data['dest_code'] = pred_selected_station(pd_data['pred_selected'])
            pd_data['flag_loc'] = 0
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)
            printout.append("" + "You want to predict for a train traveling to " + pd_data['chosen_dest_str'] + ".")

        if chosen_time:
            delay_beforecon = " ".join(chosen_time)
            pd_data['delay'] = pred_time_conversion(delay_beforecon)
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)
            printout.append("" + "You are currently experiencing a delay of " + str(pd_data['delay']) + " minutes.")

        pred_missing_info_response()
        printout.insert(0, True)
        return

    printout.insert(0, False)
    return

# This function is used to respond to the user if the user has entered all the necessary information for the prediction, this is different from the pred_missing_info_response function
# as this function is used to respond to the user if the user has already entered all the necessary information for the prediction
    
def pred_ticket_response():
    global final_chatbot
    global printout

    if pd_data['chosen_origin_str'] is not None and pd_data['current_station'] is not None and pd_data['delay'] is not None:
        pd_data['date_str'] = date_conversion("today")
        pd_data['time_str'] = time_conversion("now")
        printout.append("You want to predict for a train journey that you are currently on, at the moment you are at " + pd_data['current_station'] + " and you are experiencing a delay of " + pd_data['delay'] + ".")
        if final_chatbot:
            printout.append("If you don't have any other questions you can type bye.")

    if pd_data['current_station'] is None:
        printout.append("Please tell me the station you are currently at.")

    if pd_data['chosen_dest_str'] is None:
        printout.append("Please tell me the station you want to travel to.")

    if pd_data['delay'] is None:
        printout.append("Please tell me the delay you are experiencing.")
        
    

