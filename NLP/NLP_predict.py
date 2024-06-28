from NLP_functions import *
import pandas as pd
from fuzzywuzzy import process

nlp = spacy.load("en_core_web_sm")

pdf = pd.read_csv(pred_stations_path)
pdf['combined'] = pdf['name'] + ' ' + pdf['longname.name_alias']



multiple_loc = False

def pred_missing_info_response():
    global final_chatbot
    global printout

    if pd_data['pred_type'] == None:
        printout.append("Please Choose a Prediction Type.")
        printout.append("You can choose from 'future train' or 'active train'.")

    if pd_data['pred_type'] == 'future train':
        if pd_data['chosen_origin_str'] is not None and pd_data['chosen_dest_str'] is not None and pd_data['date_str'] is not None and pd_data['time_str'] is not None:
            printout.append("You want to predict for a train traveling from " + pd_data['chosen_origin_str'] + " to " + pd_data['chosen_dest_str'] + " on " + pd_data['date_str'] + " at " + pd_data['time_str'] + ".")
            if final_chatbot:
                printout.append("If you don't have any other questions you can type bye.")

        if pd_data['chosen_origin_str'] is None:
            printout.append("Please tell me the station you want to travel from.")

        if pd_data['chosen_dest_str'] is None:
            printout.append("Please tell me the station you want to travel to.")

        if pd_data['date_str'] is None:
            printout.append("Please tell me the date you want to travel on.")

        if pd_data['time_str'] is None:
            printout.append("Please tell me the time you want to travel at.")

    if pd_data['pred_type'] == 'active train':
        if pd_data['chosen_dest_str'] is not None and pd_data['current_station'] is not None and pd_data['delay'] is not None:
            pd_data['date_str'] = date_conversion("today")
            pd_data['time_str'] = time_conversion("now")
            printout.append("You want to predict for a train journey that you are currently on, at the moment you are at " + pd_data['current_station'] + " and you are experiencing a delay of " + str(pd_data['delay']) + ".")
            if final_chatbot:
                printout.append("If you don't have any other questions you can type bye.")

        if pd_data['current_station'] is None:
            printout.append("Please tell me the station you are currently at.")

        if pd_data['chosen_dest_str'] is None:
            printout.append("Please tell me the station you want to travel to.")

        if pd_data['delay'] is None:
            printout.append("Please tell me the delay you are experiencing.")

def check_type(user_input , loc):
    user_input = user_input.lower()
    ticket_list = ['future train','active train']

    for ticket in ticket_list:
        if ticket in user_input:
            pd_data['pred_type'] = ticket_list[ticket_list.index(ticket)]
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)
            if loc == 1:
                return ticket_list[ticket_list.index(ticket)]

    if loc == 1:
        return None

def pred_similar_stations(target):
    global pdf
    station_names = [(name,idx) for idx, name in enumerate(pdf['combined'])]
    top_matches = process.extract(target, station_names, limit=2)

    results = [{'matched station': match[0][0], 'similarity score': match[1],
                'index': i+1, 'original index': match[0][1]} for i, match in enumerate(top_matches)]
    return results

def pred_station_selector(target_station):
    pd_data['pred_station_selector'] = True
    with open(pred_data_path, 'w') as file:
        json.dump(pd_data, file, indent=4)

    global printout
    global pdf

    similar_stations = pred_similar_stations(target_station)
    printout.append("Did you mean one of these stations? (Please enter the index of the station you want to select)")

    for station in similar_stations:
        printout.append(f"{station['index']} Station: {station['matched station']}, Similarity Score: {station['similarity score']}")
        pd_data[f"pred_station{station['index']}"] = similar_stations[station['index'] - 1]['original index']

    with open(pred_data_path, 'w') as file:
        json.dump(pd_data, file, indent=4)


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


def pred_ner_response(user_input):



    doc = nlp(user_input)
    chosen_origin = []
    chosen_dest = []
    chosen_date = []
    chosen_time = []
    chosen_cur_stat = []
    global printout

    # this checks the user input to see if they have entered a ticket type anywhere in the sentence allowing the user to phrase their sentence in any way
    check_type(user_input, 0)

    if pd_data['pred_type'] == None:
        pred_missing_info_response()
        printout.insert(0, True)
        return

    if pd_data['pred_type'] == 'future train':
        for ent in doc.ents:
            ent_index = ent.start
            if doc[ent_index - 1].text.lower() == "from":
                if ent.label_ in loc_types:
                    chosen_origin.append(ent.text)
            if doc[ent_index - 1].text.lower() == "to":
                if ent.label_ in loc_types:
                    chosen_dest.append(ent.text)

            if ent.label_ == "ORDINAL":
                chosen_date.append(ent.text)
            if ent.label_ == "DATE":
                chosen_date.append(ent.text)
            if ent.label_ == "TIME":
                chosen_time.append(ent.text)

        if chosen_origin != [] and pd_data['flag_loc'] < 1:
            pd_data['flag_loc'] = 1
            pd_data['chosen_origin_str'] = " ".join(chosen_origin)
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)
            pred_station_selector(pd_data['chosen_origin_str'])
            return printout.insert(0, True)

        if pd_data['pred_station_selector'] and pd_data['flag_loc'] == 1:
            pd_data['chosen_origin_str'], pd_data['origin_code'] = pred_selected_station(pd_data['pred_selected'])
            pd_data['flag_loc'] = 0
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)
            printout.append("" + "You want to predict for a train traveling from " + pd_data['chosen_origin_str'] + ".")

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

        if may_check(user_input):
            if "May" not in chosen_date:
                chosen_date.append("May")

        if chosen_time:
            chosen_time_beforecon = " ".join(chosen_time)
            pd_data['time_str'] = time_conversion(chosen_time_beforecon)
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)
            printout.append("" + "You want to travel at " + pd_data['time_str'] + ".")

        if chosen_date:
            chosen_date_before = " ".join(chosen_date)
            cleaned_date = clean_date(chosen_date_before)
            chosen_date_date = date_conversion(cleaned_date)
            pd_data['date_str'] = "".join(chosen_date_date)
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)
            printout.append("" + "You want to travel on " + pd_data['date_str'] + ".")


        pred_missing_info_response()
        printout.insert(0, True)
        return

                
    if pd_data['pred_type'] == 'active train':
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
                "" + "You want to predict for a train journey that you are currently on, at the moment you are at " + pd_data['current_station'] + ".")

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
    
def pred_ticket_response(type):
    global final_chatbot
    global printout

    if type == 'future train':
        printout.append("You have selected to predict for a future train.")
        if pd_data['chosen_origin_str'] is not None and pd_data['chosen_dest_str'] is not None and pd_data['date_str'] is not None and pd_data['time_str'] is not None:
            printout.append("You want to predict for a train traveling from " + pd_data['chosen_origin_str'] + " to " + pd_data['chosen_dest_str'] + " on " + pd_data['date_str'] + " at " + pd_data['time_str'] + ".")
            if final_chatbot:
                printout.append("If you don't have any other questions you can type bye.")

        if pd_data['chosen_origin_str'] is None:
            printout.append("Please tell me the station you want to travel from.")

        if pd_data['chosen_dest_str'] is None:
            printout.append("Please tell me the station you want to travel to.")

        if pd_data['date_str'] is None:
            printout.append("Please tell me the date you want to travel on.")

        if pd_data['time_str'] is None:
            printout.append("Please tell me the time you want to travel at.")

    if type == 'active train':
        printout.append("You have selected to predict for an active train.")
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

def pred_expert_response(user_input):
    global printout
    type = check_type(user_input, 1)
    if type != None:
        pred_ticket_response(type)
        printout.insert(0,True)
        return
        
    printout.insert(0,False)
    return
        
    

