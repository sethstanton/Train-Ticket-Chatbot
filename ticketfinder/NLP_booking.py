from .NLP_functions import *
from .journey_new import *
import pandas as pd
from fuzzywuzzy import process

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

return_phrases = ['coming back', 'returning', 'return', 'departing', 'leaving', 'leave']

df = pd.read_csv(stations_path)
df['combined'] = df['name'] + ' ' + df['longname.name_alias']

# this function is used to format the price to 2 decimal places
def format_float(value):
    return "{:.2f}".format(value)



multiple_loc = False

# similar to the missing_info_response function in NLP_Predict this function is used to check if the user has given all the necessary information to the chatbot
# if the user has not given all the necessary information the chatbot will prompt the user to give the missing information
# if the user has given all the necessary information the chatbot will return the ticket price and a url to the user
# the chatbot will also prompt the user to ask any other questions or to end the conversation
def missing_info_response():
    global final_chatbot
    global printout

    if data['ticket_type'] is None:

        if data['arrive_date_str'] is not None and data['chosen_dest_str'] is not None:
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + ".")
            if final_chatbot:
                printout.append("Could you please tell me what kind of ticket you are looking for? (You can just ask for one way, round and open return tickets.)")

        if data['chosen_origin_str'] == "Norwich":
            printout.append("No Origin given. Defaulting to Norwich. (if you would like to change this please say 'from' and then the location)")

        if data['chosen_dest_str'] is None:
            printout.append("Please Choose a Destination.")

        if data['arrive_date_str'] is None:
            printout.append("Please Choose a Date.")

    if data['leave_arrive'] is None:
        printout.append("Please Choose if you want to depart or arrive at the time given.")
        printout.append("Just type 'leave' or 'arrive'.")

    if data['ticket_type'] == "one way" and data['leave_arrive'] is not None:
        if data['arrive_date_str'] is not None and data['chosen_dest_str'] is not None and data['arrive_time_str'] is not None and data['chosen_origin_str'] == "Norwich":
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " at " + data['arrive_time_str'] + " with a one way ticket.")
            printout.append("You have not provided a Origin, Default is Norwich, if you want to change this simply type 'from' and then the origin location.")
            if final_chatbot:
                price, url = one_way(data['origin_code'], data['dest_code'], data['arrive_date_str'], data['arrive_time_str'], data['leave_arrive'])
                if price is None:
                    printout.append("Sorry, I could not find a ticket for this journey.")
                else:
                    price = format_float(float(price))
                    printout.append("The price for this journey is £" + format_float(float(price)) + " .")
                printout.append(url)
                printout.append("If you don't have any other questions you can type bye.")
        if data['arrive_date_str'] is not None and data['chosen_dest_str'] is not None and data['arrive_time_str'] is not None and data['chosen_origin_str'] != "Norwich":
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " at " + data['arrive_time_str'] + " with a one way ticket.")
            if final_chatbot:
                price, url = one_way(data['origin_code'], data['dest_code'], data['arrive_date_str'],
                                     data['arrive_time_str'], data['leave_arrive'])
                if price is None:
                    printout.append("Sorry, I could not find a ticket for this journey.")
                else:
                    price = format_float(float(price))
                    printout.append("The price for this journey is £" + format_float(float(price)) + " .")
                printout.append(url)
                printout.append("If you don't have any other questions you can type bye.")
        if data['chosen_dest_str'] is None:
            printout.append("Please Choose a Destination.")
        if data['arrive_date_str'] is None:
            printout.append("Please Choose a Date.")
        if data['arrive_time_str'] is None:
            printout.append("Please Choose a Time.")

    if data['ticket_type'] == "open ticket" and data['leave_arrive'] is not None:
        if data['chosen_dest_str'] is not None and data['arrive_date_str'] is not None and data['chosen_origin_str'] == "Norwich":
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " with an open ticket.")
            printout.append("You have not provided a Origin, Default is Norwich, if you want to change this simply type 'from' and then the origin location.")
            if final_chatbot:
                price, url = open_ticket(dest=data['dest_code'], origin=data['origin_code'], date=data['arrive_date_str'], lor=data['leave_arrive'])
                if price is None:
                    printout.append("Sorry, I could not find a ticket for this journey.")
                else:
                    price = format_float(float(price))
                    printout.append("The price for this journey is £" + price + " .")
                printout.append(url)
                printout.append("If you don't have any other questions you can type bye.")

        if data['arrive_date_str'] is not None and data['chosen_dest_str'] is not None and data['chosen_origin_str'] != "Norwich":
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " with an open ticket.")
            if final_chatbot:
                price, url = open_ticket(dest=data['dest_code'], origin=data['origin_code'], date=data['arrive_date_str'], lor=data['leave_arrive'])
                if price is None:
                    printout.append("Sorry, I could not find a ticket for this journey.")
                else:
                    price = format_float(float(price))
                    printout.append("The price for this journey is £" + price + " .")
                printout.append(url)
                printout.append("If you don't have any other questions you can type bye.")
        if data['chosen_dest_str'] is None:
            printout.append("Please Choose a Destination.")
        if data['arrive_date_str'] is None:
            printout.append("Please Choose a Date.")

    if data['ticket_type'] == "round" and data['leave_arrive'] is not None:
        if data['chosen_dest_str'] is not None and data['arrive_date_str'] is not None and data['arrive_time_str'] is not None and data['leave_date_str'] is not None and data['leave_time_str'] is not None and data['chosen_origin_str'] == "Norwich":
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " at " + data['arrive_time_str'] + " with a round ticket.")
            printout.append("You want to return on " + data['leave_date_str'] + " at " + data['leave_time_str'] + ".")
            printout.append("You have not provided a Origin, Default is Norwich, if you want to change this simply type 'from' and then the origin location.")
            if final_chatbot:
                price, url = round_trip(data['origin_code'], data['dest_code'], data['arrive_date_str'],
                                   data['arrive_time_str'], data['leave_date_str'], data['leave_time_str'],
                                   data['leave_arrive'], data['leave_arrive'])
                if price is None:
                    printout.append("Sorry, I could not find a ticket for this journey.")
                else:
                    price = format_float(float(price))
                    printout.append("The price for this journey is £" + price + " .")
                printout.append(url)
                printout.append("If you don't have any other questions you can type bye.")
        if data['chosen_dest_str'] is not None and data['arrive_date_str'] is not None and data['arrive_time_str'] is not None and data['leave_date_str'] is not None and data['leave_time_str'] is not None and data['chosen_origin_str'] != "Norwich":
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " at " + data['arrive_time_str'] + " with a round ticket.")
            printout.append("You want to return on " + data['leave_date_str'] + " at " + data['leave_time_str'] + ".")
            if final_chatbot:
                price, url = round_trip(data['origin_code'], data['dest_code'], data['arrive_date_str'], data['arrive_time_str'], data['leave_date_str'], data['leave_time_str'], data['leave_arrive'], data['leave_arrive'])
                if price is None:
                    printout.append("Sorry, I could not find a ticket for this journey.")
                else:
                    price = format_float(float(price))
                    printout.append("The price for this journey is £" + price + " .")
                printout.append(url)
                printout.append("If you don't have any other questions you can type bye.")
        if data['chosen_dest_str'] is None:
            printout.append("Please Choose a Destination.")
        if data['arrive_date_str'] is None:
            printout.append("Please Choose a Date. To leave your origin on")
        if data['arrive_time_str'] is None:
            printout.append("Please Choose a Time. To leave your origin on")
        if data['leave_date_str'] is None:
            printout.append("Please Choose a Date to return.")
        if data['leave_time_str'] is None:
            printout.append("Please Choose a Time to return.")

    if data['ticket_type'] == "open return" and data['leave_arrive'] is not None:
        if data['chosen_dest_str'] is not None and data['arrive_date_str'] is not None and data['leave_date_str'] is not None and data['chosen_origin_str'] == "Norwich":
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " with an open return ticket.")
            printout.append("You want to return on " + data['leave_date_str'] + ".")
            printout.append("You have not provided a Origin, Default is Norwich, if you want to change this simply type 'from' and then the origin location.")
            if final_chatbot:
                price, url = open_return(data['origin_code'], data['dest_code'], data['arrive_date_str'], data['leave_date_str'], data['leave_arrive'], data['leave_arrive'])
                if price is None:
                    printout.append("Sorry, I could not find a ticket for this journey.")
                else:
                    price = format_float(float(price))
                    printout.append("The price for this journey is £" + price + " .")
                printout.append(url)
                printout.append("If you don't have any other questions you can type bye.")

        if data['chosen_dest_str'] is not None and data['arrive_date_str'] is not None and data['leave_date_str'] is not None and data['chosen_origin_str'] != "Norwich":
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " with an open return ticket.")
            printout.append("You want to return on " + data['leave_date_str'] + ".")
            if final_chatbot:
                price, url = open_return(data['origin_code'], data['dest_code'], data['arrive_date_str'],
                                    data['leave_date_str'], data['leave_arrive'], data['leave_arrive'])
                if price is None:
                    printout.append("Sorry, I could not find a ticket for this journey.")
                else:
                    price = format_float(float(price))
                    printout.append("The price for this journey is £" + price + " .")
                printout.append(url)
                printout.append("If you don't have any other questions you can type bye.")

        if data['chosen_dest_str'] is None:
            printout.append("Please Choose a Destination.")
        if data['arrive_date_str'] is None:
            printout.append("Please Choose a Date. To leave your origin on")
        if data['leave_date_str'] is None:
            printout.append("Please Choose a Date to return.")


# this function is used to enter the selected information into the data dictionary
# this is done as a separate function to make the main function more readable
def selection(chosen_time, chosen_origin, chosen_dest, chosen_date):

    global printout

    if chosen_time:
        chosen_time_beforecon = " ".join(chosen_time)
        data['arrive_time_str'] = time_conversion(chosen_time_beforecon)
        with open(data_path, 'w') as file:
            json.dump(data, file, indent=4)
        printout.append("" + "You want to travel at " + data['arrive_time_str'] + ".")

    if chosen_origin and data['flag_loc'] < 3:
        data['flag_loc'] = 3
        data['chosen_origin_str'] = " ".join(chosen_origin)
        with open(data_path, 'w') as file:
            json.dump(data, file, indent=4)
        station_selector(data['chosen_origin_str'])
        return True

    if data['station_selector'] and data['flag_loc'] == 3:
        data['chosen_origin_str'], data['origin_code'] = selected_station(data['selected'])
        data['flag_loc'] = 0
        with open(data_path, 'w') as file:
            json.dump(data, file, indent=4)
        printout.append("" + "You want to travel from " + data['chosen_origin_str'] + ".")

    if chosen_dest and data['flag_loc'] < 4:
        data['flag_loc'] = 4
        data['chosen_dest_str'] = " ".join(chosen_dest)
        with open(data_path, 'w') as file:
            json.dump(data, file, indent=4)
        station_selector(data['chosen_dest_str'])
        return True

    if data['station_selector'] and data['flag_loc'] == 4:
        data['chosen_dest_str'], data['dest_code'] = selected_station(data['selected'])
        data['flag_loc'] = 0
        with open(data_path, 'w') as file:
            json.dump(data, file, indent=4)
        printout.append("" + "You want to travel to " + data['chosen_dest_str'] + ".")

    if chosen_date:
        chosen_date_before = " ".join(chosen_date)
        cleaned_date = clean_date(chosen_date_before)
        chosen_date_date = date_conversion(cleaned_date)
        data['arrive_date_str'] = "".join(chosen_date_date)
        with open(data_path, 'w') as file:
            json.dump(data, file, indent=4)
        printout.append("" + "You want to travel on " + data['arrive_date_str'] + ".")

    if data['ticket_type'] is not None:
        printout.append("" + "You want to travel with a " + data['ticket_type'] + " ticket.")

# this function is used to check if the user has entered a ticket type in their input
# if the user has entered a ticket type the function will enter the ticket type into the data dictionary
def check_ticket(user_input , loc):
    user_input = user_input.lower()
    ticket_list = ['one way', 'round', 'open ticket', 'open return']

    for ticket in ticket_list:
        if ticket in user_input:
            data['ticket_type'] = ticket_list[ticket_list.index(ticket)]
            with open(data_path, 'w') as file:
                json.dump(data, file, indent=4)
            if loc == 1:
                return ticket_list[ticket_list.index(ticket)]

    if loc == 1:
        return None

# this function is used to find the top 5 stations that are similar to the target station
def find_similar_stations(target):
    global df
    station_names = [(name,idx) for idx, name in enumerate(df['combined'])]
    top_matches = process.extract(target, station_names, limit=5)

    results = [{'matched station': match[0][0], 'similarity score': match[1],
                'index': i+1, 'original index': match[0][1]} for i, match in enumerate(top_matches)]
    return results

# this function is used to return the most similar station to the station the user has entered
def station_selector(target_station):
    data['station_selector'] = True
    with open(data_path, 'w') as file:
        json.dump(data, file, indent=4)

    global printout
    global df

    similar_stations = find_similar_stations(target_station)
    printout.append("Here are the top 5 matching stations, please select the one you want to use:")

    for station in similar_stations:
        printout.append(f"{station['index']} Station: {station['matched station']}")
        data[f"station{station['index']}"] = similar_stations[station['index'] - 1]['original index']

    with open(data_path, 'w') as file:
        json.dump(data, file, indent=4)
    printout.append("Enter the index of the station you want to select:")

# this function is used to select the station the user has chosen from the list of similar stations
# the function will then store the station name and tiploc in the data dictionary
def selected_station(selected_station):
    data['station_selector'] = False
    with open(data_path, 'w') as file:
        json.dump(data, file, indent=4)
    station_df_index = data[f'station{selected_station}']
    station_name = df.iloc[station_df_index]['name']
    station_tiploc = df.iloc[station_df_index]['tiploc']

    for i in range (1, 6):
        data[f'station{i}'] = None
    with open(data_path, 'w') as file:
        json.dump(data, file, indent=4)

    return station_name, station_tiploc

# This is the main function that is called when the user enters a sentence into the chatbot
# this function will process the user input and determine what the user is asking for
def ner_response(user_input):

    # this is used to remove the word 'of' from the user input as it is not needed and can cause issues with the NER

    user_input = user_input.replace(" of", "")


    doc = nlp(user_input)
    chosen_origin = []
    chosen_dest = []
    chosen_date = []
    chosen_time = []
    global printout

    global multiple_loc

    global return_phrases

    multiple_loc = False

    # this checks the user input to see if they have entered a ticket type anywhere in the sentence allowing the user to phrase their sentence in any way
    check_ticket(user_input, 0)

    # this check the user input for the word 'from' as this word will always be present if the user is giving 2 locations in one input
    for key in doc:
        if key.text.lower() == "from":
            multiple_loc = True

    # this checks the user input for the specific words 'leave' and 'arrive' to determine if the user wants to leave or arrive at the time given
    if user_input == "leave":
        data['leave_arrive'] = "leave"
        with open(data_path, 'w') as file:
            json.dump(data, file, indent=4)
        printout.append("You have chosen to leave at the time you have given.")
        missing_info_response()
        printout.insert(0, True)
        return
        
    if user_input == "arrive":
        data['leave_arrive'] = "arrive"
        with open(data_path, 'w') as file:
            json.dump(data, file, indent=4)
        printout.append("You have chosen to arrive at your destination at the time you have given.")
        missing_info_response()
        printout.insert(0, True)
        return
        

    # this segment is specific for the ticket types 'round' and 'open return' as they require a return date and time which requires extra processing to separate the two dates and times
    if data['ticket_type'] == "round" or data['ticket_type'] == "open return":
        for phrase in return_phrases:
            if phrase in user_input:  # this checks the user input for the specific phrases that indicate a return date and time is given

                for ent in doc.ents:
                    if multiple_loc:
                        ent_index = ent.start
                        if doc[ent_index - 1].text.lower() == "from":
                            if ent.label_ in loc_types:
                                chosen_origin.append(ent.text)
                        if doc[ent_index - 1].text.lower() == "to":
                            if ent.label_ in loc_types:
                                chosen_dest.append(ent.text)
                    else:
                        if ent.label_ in loc_types:
                            chosen_dest.append(ent.text)

                # If the user has entered a location, we raise a flag to indicate that the user has entered a location
                # and then find the top 2 stations that are similar to the station that the user has entered
                # We then ask the user to select the station that they want to choose
                # after the user has selected the station, we convert the input response from the user to the station that the user has selected
                # We then store the station that the user has selected in the correct variable

                # Then we continue the process for the original user input and check if the user has entered a time or destination
                if chosen_origin != [] and data['flag_loc'] < 1:
                    data['flag_loc'] = 1
                    data['chosen_origin_str'] = " ".join(chosen_origin)
                    with open(data_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    station_selector(data['chosen_origin_str'])
                    return printout.insert(0, True)

                if data['station_selector'] and data['flag_loc'] == 1:
                    data['chosen_origin_str'], data['origin_code'] = selected_station(data['selected'])
                    data['flag_loc'] = 0
                    with open(data_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    printout.append("You want to go to " + data['chosen_origin_str'] + ".")


                if chosen_dest != [] and data['flag_loc'] < 2:
                    data['flag_loc'] = 2
                    data['chosen_dest_str'] = " ".join(chosen_dest)
                    with open(data_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    station_selector(data['chosen_dest_str'])
                    return printout.insert(0, True)

                if data['station_selector'] and data['flag_loc'] == 2:
                    data['chosen_dest_str'], data['dest_code'] = selected_station(data['selected'])
                    data['flag_loc'] = 0
                    with open(data_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    printout.append("" + "You want to go to " + data['chosen_dest_str'] + ".")


                # Return phrases located in the text indicate where the return date and time is located in the user input
                # We process each segment of the user input to find the date and time of the return journey and store it in the data dictionary

                go_date = []
                go_time = []

                back_date = []
                back_time = []

                segments = user_input.split(phrase)

                go_to = segments[0]
                come_back = segments[1]

                go_to = clean_date(go_to)
                come_back = clean_date(come_back)

                doc_go_to = nlp(go_to)
                doc_come_back = nlp(come_back)

                for go_ent in doc_go_to.ents:
                    if go_ent.label_ == "ORDINAL":
                        go_date.append(go_ent.text)
                    if go_ent.label_ == "DATE":
                        go_date.append(go_ent.text)
                    if go_ent.label_ == "TIME":
                        go_time.append(go_ent.text)

                for back_ent in doc_come_back.ents:
                    if back_ent.label_ == "ORDINAL":
                        back_date.append(back_ent.text)
                    if back_ent.label_ == "DATE":
                        back_date.append(back_ent.text)
                    if back_ent.label_ == "TIME":
                        back_time.append(back_ent.text)

                # If the time provided is in the format HH:MM we need to locate it in the text and convert it to a string
                # SpaCy cannot recognise this format as a time entity so we need to locate it manually
                time_pattern = r"\b\d{2}:\d{2}\b"

                if go_time == []:
                    match = re.search(time_pattern, go_to)
                    if match:
                        go_time.append(match.group())

                if back_time == []:
                    match = re.search(time_pattern, come_back)
                    if match:
                        back_time.append(match.group())

                if may_check(go_to):
                    if "May" not in go_date:
                        go_date.append("May")

                if may_check(come_back):
                    if "May" not in back_date:
                        back_date.append("May")

                if go_time != []:
                    ar_time_beforecon = " ".join(go_time)
                    data['arrive_time_str'] = time_conversion(ar_time_beforecon)
                    with open(data_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    printout.append("" + "You want to travel at " + data['arrive_time_str'] + ".")

                if go_date != []:
                    chosen_date_before = " ".join(go_date)
                    cleaned_date = clean_date(chosen_date_before)
                    chosen_date_date = date_conversion(cleaned_date)
                    data['arrive_date_str'] = "".join(chosen_date_date)
                    with open(data_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    printout.append("" + "You want to travel on " + data['arrive_date_str'] + ".")

                if back_time != []:
                    back_time_beforecon = " ".join(back_time)
                    data['leave_time_str'] = time_conversion(back_time_beforecon)
                    with open(data_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    printout.append("" + "You want to return at " + data['leave_time_str'] + ".")

                if back_date != []:
                    if len(back_date[0]) < 4:
                        if back_date[0].lower() not in weekdays:

                            ord = clean_ord(back_date[0])
                            ord = int(ord)

                            fixed_date = chosen_date_date[:-2] + str(ord)

                            leave_date_date = datetime.strptime(fixed_date, "%Y-%m-%d").strftime("%Y-%m-%d")

                            data['leave_date_str'] = "".join(leave_date_date)
                            with open(data_path, 'w') as file:
                                json.dump(data, file, indent=4)

                            printout.append("" + "You want to return on " + data['leave_date_str'] + ".")

                    else:
                        back_date_before = " ".join(back_date)
                        cleaned_date = clean_date(back_date_before)
                        back_date_date = date_conversion(cleaned_date)
                        data['leave_date_str'] = "".join(back_date_date)
                        with open(data_path, 'w') as file:
                            json.dump(data, file, indent=4)
                        printout.append("" + "You want to return on " + data['leave_date_str'] + ".")

                missing_info_response()
                printout.insert(0, True)
                return

    # IF the user has not asked for a return ticket we assume they are asking for a one way ticket, we then process the user input to find the date, time, origin and destination
    # if no origin is given we default to Norwich
    else:
        for token in doc:
            if token.pos_ == "VERB": # this checks the user input for a spcific verb as this is a good indicator that they are providing a several pieces of information
                choose = False
                if token.text.lower() in verbs:
                    choose = True
                if choose:
                    if any(doc.ents):
                        for ent in doc.ents:
                            if multiple_loc:
                                ent_index = ent.start
                                if doc[ent_index - 1].text.lower() == "from":
                                    if ent.label_ in loc_types:
                                        chosen_origin.append(ent.text)
                                if doc[ent_index - 1].text.lower() == "to":
                                    if ent.label_ in loc_types:
                                        chosen_dest.append(ent.text)

                                if ent.label_ == "DATE":
                                    chosen_date.append(ent.text)
                                if ent.label_ == "TIME":
                                    chosen_time.append(ent.text)
                            else:
                                if ent.label_ in loc_types:
                                    chosen_dest.append(ent.text)
                                if ent.label_ == "ORDINAL":
                                    chosen_date.append(ent.text)
                                if ent.label_ == "DATE":
                                    chosen_date.append(ent.text)
                                if ent.label_ == "TIME":
                                    chosen_time.append(ent.text)

                        if may_check(user_input):
                            if "May" not in chosen_date:
                                chosen_date.append("May")

                        time_pattern = r"\b\d{2}:\d{2}\b"

                        if chosen_time == []:
                            match = re.search(time_pattern, user_input)
                            if match:
                                chosen_time.append(match.group())

                        if selection(chosen_time, chosen_origin, chosen_dest, chosen_date):
                            return printout.insert(0, True)
                        else:
                            missing_info_response()
                            printout.insert(0, True)
                            return

        # If the user has not entered a verb in their sentence we assume they are asking for a one way ticket and we process the user input to find the date, time, origin and destination
        # we assume that the entities are related to booking train tickets because the chatbot is designed to book train tickets
                        
        for ent in doc.ents:
            if ent.label_ == "DATE":
                date = ent.text
                date = clean_date(date)
                date = date_conversion(date)
                data['arrive_date_str'] = date
                with open(data_path, 'w') as file:
                    json.dump(data, file, indent=4)
                printout.append("You want to travel on " + date + ".")
                missing_info_response()
                printout.insert(0, True)
                return
                
            if ent.label_ == "TIME":
                time = ent.text
                time = time_conversion(time)
                data['arrive_time_str'] = time
                with open(data_path, 'w') as file:
                    json.dump(data, file, indent=4)
                printout.append("You want to travel at " + time + ".")
                missing_info_response()
                printout.insert(0, True)
                return
                
            if ent.label_ in loc_types:
                ent_index = ent.start
                if doc[ent_index - 1].text.lower() == "from":
                    chosen_origin.append(ent.text)

                    if chosen_origin != [] and data['flag_loc'] < 5:
                        data['flag_loc'] = 5
                        data['chosen_origin_str'] = " ".join(chosen_origin)
                        with open(data_path, 'w') as file:
                            json.dump(data, file, indent=4)
                        station_selector(data['chosen_origin_str'])
                        return printout.insert(0, True)

                    if data['station_selector'] and data['flag_loc'] == 5:
                        data['chosen_origin_str'], data['origin_code'] = selected_station(data['selected'])
                        data['flag_loc'] = 0
                        with open(data_path, 'w') as file:
                            json.dump(data, file, indent=4)
                        printout.append("" + "You want to travel from " + data['chosen_origin_str'] + ".")
                        missing_info_response()
                        printout.insert(0, True)
                        return
                    
                if doc[ent_index - 1].text.lower() == "to":
                    chosen_dest.append(ent.text)
                    if chosen_dest != [] and data['flag_loc'] < 6:
                        data['flag_loc'] = 6
                        data['chosen_dest_str'] = " ".join(chosen_dest)
                        with open(data_path, 'w') as file:
                            json.dump(data, file, indent=4)
                        station_selector(data['chosen_dest_str'])
                        return printout.insert(0, True)

                    if data['station_selector'] and data['flag_loc'] == 6:
                        data['chosen_dest_str'], data['dest_code'] = selected_station(data['selected'])
                        data['flag_loc'] = 0
                        with open(data_path, 'w') as file:
                            json.dump(data, file, indent=4)
                        printout.append("" + "You want to travel to " + data['chosen_dest_str'] + ".")
                        missing_info_response()
                        printout.insert(0, True)
                        return
                else:
                    chosen_dest.append(ent.text)
                    if chosen_dest != [] and data['flag_loc'] < 7:
                        data['flag_loc'] = 7
                        data['chosen_dest_str'] = " ".join(chosen_dest)
                        with open(data_path, 'w') as file:
                            json.dump(data, file, indent=4)
                        station_selector(data['chosen_dest_str'])
                        return printout.insert(0, True)

                    if data['station_selector'] and data['flag_loc'] == 7:
                        data['chosen_dest_str'], data['dest_code'] = selected_station(data['selected'])
                        data['flag_loc'] = 0
                        with open(data_path, 'w') as file:
                            json.dump(data, file, indent=4)
                        printout.append("" + "You want to travel to " + data['chosen_dest_str'] + ".")
                        missing_info_response()
                        printout.insert(0, True)
                        return
        if chosen_time == []:
            time_pattern = r"\b\d{2}:\d{2}\b"
            match = re.search(time_pattern, user_input)
            if match:
                time = match.group()
                time = time_conversion(time)
                data['arrive_time_str'] = time
                with open(data_path, 'w') as file:
                    json.dump(data, file, indent=4)
                printout.append("You want to travel at " + time + ".")
                printout.insert(0, True)
                return
                    
    printout.insert(0, False)
    return

    # if the user has provided a ticket type we process the user input to find the date, time, origin and destination and respond with the information the user has provided
    # This function is a little redundant as the missing info response function serves the same purpose but it is kept here as it was too risky to remove it this late in the project
def ticket_response(ticket):
    global final_chatbot
    global printout

    if ticket == "one way":
        printout.append("You have selected a one way ticket.")
        if data['chosen_dest_str'] != None and data['arrive_date_str'] != None and data['arrive_time_str'] != None:
            printout.append(
                "You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " at " + data['arrive_time_str'] + " with a one way ticket.")
            if final_chatbot:
                printout.append("If you don't have any other questions you can type bye.")
        if data['arrive_time_str'] == None:
            printout.append("You have not chosen a time. please choose a time.")
        if data['chosen_dest_str'] == None:
            printout.append("You have not chosen a destination. please choose a destination.")
        if data['arrive_date_str'] == None:
            printout.append("You have not chosen a date. please choose a date.")

    if ticket == "round":
        printout.append("You have selected a round ticket.")
        if data['chosen_dest_str'] != None and data['arrive_date_str'] != None and data['arrive_time_str'] != None and data['leave_date_str'] != None and data['leave_time_str'] != None:
            printout.append(
                "You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " at " + data['arrive_time_str'] + " with a round ticket.")
            printout.append("You want to return on " + data['leave_date_str'] + " at " + data['leave_time_str'] + ".")
            if final_chatbot:
                printout.append("If you don't have any other questions you can type bye.")
        if data['chosen_dest_str'] == None:
            printout.append("You have not chosen a destination. please choose a destination.")
        if data['arrive_date_str'] == None:
            printout.append("You have not chosen a date to arrive. please choose a date.")
        if data['arrive_time_str'] == None:
            printout.append("You have not chosen a time to arrive. please choose a time.")
        if data['leave_date_str'] == None:
            printout.append("You have not chosen a date to leave. please choose a date.")
        if data['leave_time_str'] == None:
            printout.append("You have not chosen a time to leave. please choose a time.")

    if ticket=="open ticket":
        printout.append("You have selected a " + ticket + " ticket.")
        if data['chosen_dest_str'] != None and data['arrive_date_str'] != None:
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " with an open ticket.")
            if final_chatbot:
                printout.append("If you don't have any other questions you can type bye.")
        if data['chosen_dest_str'] == None:
            printout.append("You have not chosen a destination. please choose a destination.")
        if data['arrive_date_str'] == None:
            printout.append("You have not chosen a date to arrive. please choose a date.")

    if ticket=="open return":
        printout.append("You have selected a " + ticket + " ticket.")
        if data['chosen_dest_str'] != None and data['arrive_date_str'] != None and data['leave_date_str'] != None:
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " with an open return ticket.")
            printout.append("You want to return on " + data['leave_date_str'] + ".")
            if final_chatbot:
                printout.append("If you don't have any other questions you can type bye.")
        if data['chosen_dest_str'] == None:
            printout.append("You have not chosen a destination. please choose a destination.")
        if data['arrive_date_str'] == None:
            printout.append("You have not chosen a date to arrive. please choose a date.")
        if data['leave_date_str'] == None:
            printout.append("You have not chosen a date to leave. please choose a date.")

# this function is used to check if the user has entered a ticket type in their input if so the function will respond with the information the user has provided
def expert_response(user_input):
    global printout
    ticket = check_ticket(user_input, 1)
    if ticket != None:
        missing_info_response()
        printout.insert(0,True)
        return
        
    printout.insert(0,False)
    return

# This function was used for testing purposese to respond with the information the user has provided when exiting the chatbot
# we do not use this function in the final chatbot as it is not needed
def goodbye_response():
    global printout

    if data['ticket_type'] is None:

        if data['arrive_date_str'] is not None and data['chosen_dest_str'] is not None:
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + ".")

        if data['chosen_origin_str'] == "Norwich":
            printout.append("No Origin given. Defaulting to Norwich. (if you would like to change this please say 'from' and then the location)")

        if data['chosen_dest_str'] is None:
            printout.append("Please Choose a Destination.")

        if data['arrive_date_str'] is None:
            printout.append("Please Choose a Date.")

    if data['ticket_type'] == "one way" and data['leave_arrive'] is not None:
        if data['arrive_date_str'] is not None and data['chosen_dest_str'] is not None and data['arrive_time_str'] is not None:
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " at " + data['arrive_time_str'] + " with a one way ticket.")
        if data['chosen_dest_str'] is None:
            printout.append("Please Choose a Destination.")
        if data['arrive_date_str'] is None:
            printout.append("Please Choose a Date.")
        if data['arrive_time_str'] is None:
            printout.append("Please Choose a Time.")

    if data['ticket_type'] == "open ticket" and data['leave_arrive'] is not None:
        if data['chosen_dest_str'] is not None and data['arrive_date_str'] is not None:
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " with an open ticket.")
        if data['chosen_dest_str'] is None:
            printout.append("Please Choose a Destination.")
        if data['arrive_date_str'] is None:
            printout.append("Please Choose a Date.")

    if data['ticket_type'] == "round" and data['leave_arrive'] is not None:
        if data['chosen_dest_str'] is not None and data['arrive_date_str'] is not None and data['arrive_time_str'] is not None and data['leave_date_str'] is not None and data['leave_time_str'] is not None:
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " at " + data['arrive_time_str'] + " with a round ticket.")
            printout.append("You want to return on " + data['leave_date_str'] + " at " + data['leave_time_str'] + ".")
        if data['chosen_dest_str'] is None:
            printout.append("Please Choose a Destination.")
        if data['arrive_date_str'] is None:
            printout.append("Please Choose a Date. To leave your origin on")
        if data['arrive_time_str'] is None:
            printout.append("Please Choose a Time. To leave your origin on")
        if data['leave_date_str'] is None:
            printout.append("Please Choose a Date to return.")
        if data['leave_time_str'] is None:
            printout.append("Please Choose a Time to return.")

    if data['ticket_type'] == "open return" and data['leave_arrive'] is not None:
        if data['chosen_dest_str'] is not None and data['arrive_date_str'] is not None and data['leave_date_str'] is not None:
            printout.append("You want to travel from " + data['chosen_origin_str'] + " to " + data['chosen_dest_str'] + " on " + data['arrive_date_str'] + " with an open return ticket.")
            printout.append("You want to return on " + data['leave_date_str'] + ".")
        if data['chosen_dest_str'] is None:
            printout.append("Please Choose a Destination.")
        if data['arrive_date_str'] is None:
            printout.append("Please Choose a Date. To leave your origin on")
        if data['leave_date_str'] is None:
            printout.append("Please Choose a Date to return.")
        
    

