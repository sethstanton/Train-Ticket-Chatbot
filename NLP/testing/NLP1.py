import json
import random
import pandas as pd
from fuzzywuzzy import process
import spacy.cli
import requests
import csv
from datetime import datetime, timedelta
from datetime import datetime
from difflib import get_close_matches, SequenceMatcher
import warnings
warnings.filterwarnings('ignore')

nlp = spacy.load("en_core_web_sm")

labels = []
sentences = []

url = "https://www.4icu.org/gb/a-z/"

intentions_path = "data/intentions.json"
sentences_path = "data/sentences.txt"

# this has not been put into a seperate file as implementation would be more complex
weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'today', 'tomorrow', 'week']
verbs = ['going', 'visit', 'travel', 'go', 'choose', 'get', 'goes']
loc_types = ['GPE', 'ORG', 'LOC', 'NORP', 'PERSON']
return_phrases = ['coming back', 'returning', 'return', 'departing', 'leaving', 'leave']

df = pd.read_csv('data/stations.csv')
df['combined'] = df['name'] + ' ' + df['longname.name_alias']


chosen_origin_str = "Norwich"
chosen_dest_str = None
arrive_date_str = None
arrive_time_str = None

leave_date_str = None
leave_time_str = None
ticket_type = None
leave_arrive = None

origin_code = "NRW"
dest_code = None

multiple_loc = False

chosen_intention = None

# Opening JSON file and return JSON object as a dictionary

with open(intentions_path) as f:
    intentions = json.load(f)

final_chatbot = False

# this function checks to see if may appears in the text supplied as in some cases may can be used to indicate a date
def may_check(phrase):
    lower = phrase.lower()
    if "may" in lower:
        return True
def clean_date(date):
    date = nlp(date)
    out = ""
    for token in date:
        if token.pos_ == "DET":
            continue
        else:
            out += token.text + " "
    return out.rstrip()

def clean_ord(ord):
    if "st" in ord:
        ord = ord.replace("st", "")
        return ord
    if "nd" in ord:
        ord = ord.replace("nd", "")
        return ord
    if "rd" in ord:
        ord = ord.replace("rd", "")
        return ord
    if "th" in ord:
        ord = ord.replace("th", "")
        return ord

def date_conversion(date):
    if date.lower() in weekdays:

        date = date.lower()

        todayindex = datetime.today().weekday()

        if date == "today":
            return datetime.today().strftime("%Y-%m-%d")
        if date == "tomorrow":
            date_out = datetime.today() + timedelta(days=1)
            return date_out.strftime("%Y-%m-%d")
        if date == "a week":
            date_out = datetime.today() + timedelta(days=7)
            return date_out.strftime("%Y-%m-%d")

        index = weekdays.index(date)
        today = datetime.today()
        if todayindex == index:
            date_out = datetime.today() + timedelta(days=7)
            return date_out.strftime("%Y-%m-%d")
        else:
            if today.weekday() < index:
                date_out = datetime.today() + timedelta(days=(index - todayindex))
                return date_out.strftime("%Y-%m-%d")
            else:
                date_out = datetime.today() + timedelta(days=7 - today.weekday() + index)
                return date_out.strftime("%Y-%m-%d")
    else:
        words = date.split()
        if "st" in words[0]:
            words[0] = words[0].replace("st", "")
        if "nd" in words[0]:
            words[0] = words[0].replace("nd", "")
        if "rd" in words[0]:
            words[0] = words[0].replace("rd", "")
        if "th" in words[0]:
            words[0] = words[0].replace("th", "")

        month = words[0] + " " + words[1] + " " + str(datetime.today().year)
        date = datetime.strptime(month, "%d %B %Y").strftime("%Y-%m-%d")

        if date < datetime.today().strftime("%Y-%m-%d"):
            return datetime.strptime(month, "%d %B %Y").replace(year=datetime.today().year + 1).strftime("%Y-%m-%d")
        else:
            return date

def time_conversion(time):

    time = time.replace(" ", "")

    if "afternoon" in str(time).lower():
        return datetime.strptime("15:00", "%H:%M").strftime("%H:%M")
    if "midnight" in str(time).lower():
        return datetime.strptime("00:00", "%H:%M").strftime("%H:%M")
    if "noon" in str(time).lower():
        return datetime.strptime("12:00", "%H:%M").strftime("%H:%M")
    if "morning" in str(time).lower():
        return datetime.strptime("09:00", "%H:%M").strftime("%H:%M")
    if "evening" in str(time).lower():
        return datetime.strptime("18:00", "%H:%M").strftime("%H:%M")
    if "am" in str(time).lower() or "pm" in str(time).lower():
        return datetime.strptime(time, "%I%p").strftime("%H:%M")
    if str(time).isdigit():
        return datetime.strptime(time, "%H%M").strftime("%H:%M")
    if ":" in str(time):
        return datetime.strptime(time, "%H:%M").strftime("%H:%M")

def missing_info_response():
    global chosen_dest_str
    global arrive_date_str
    global arrive_time_str
    global chosen_origin_str
    global leave_date_str
    global leave_time_str
    global leave_arrive
    global ticket_type

    if ticket_type is None:

        if arrive_date_str is not None and chosen_dest_str is not None:
            print("BOT: You want to travel from " + chosen_origin_str + " to " + chosen_dest_str + " on " + arrive_date_str + ".")
            if final_chatbot:
                print("BOT: Could you please tell me what kind of ticket you are looking for? (You can just ask for one way, round and open return tickets.)")

        if chosen_origin_str == "Norwich":
            print("BOT: No Origin given. Defaulting to Norwich. (if you would like to change this please say 'from' and then the location)")

        if chosen_dest_str is None:
            print("BOT: Please Choose a Destination.")

        if arrive_date_str is None:
            print("BOT: Please Choose a Date.")

    if leave_arrive is None:
        print("BOT: Please Choose if you want to depart or arrive at the time given.")
        print("BOT: Just type 'leave' or 'arrive'.")

    if ticket_type == "one way" and leave_arrive is not None:
        if arrive_date_str is not None and chosen_dest_str is not None and arrive_time_str is not None:
            print("BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " at " + arrive_time_str + " with a one way ticket.")
            if final_chatbot:
                print("BOT: If you don't have any other questions you can type bye.")
        if chosen_dest_str is None:
            print("BOT: Please Choose a Destination.")
        if arrive_date_str is None:
            print("BOT: Please Choose a Date.")
        if arrive_time_str is None:
            print("BOT: Please Choose a Time.")

    if ticket_type == "open ticket" and leave_arrive is not None:
        if arrive_date_str is not None and chosen_dest_str is not None:
            print("BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " with an open ticket.")
            if final_chatbot:
                print("BOT: If you don't have any other questions you can type bye.")
        if chosen_dest_str is None:
            print("BOT: Please Choose a Destination.")
        if arrive_date_str is None:
            print("BOT: Please Choose a Date.")

    if ticket_type == "round" and leave_arrive is not None:
        if chosen_dest_str is not None and arrive_date_str is not None and arrive_time_str is not None and leave_date_str is not None and leave_time_str is not None:
            print("BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " at " + arrive_time_str + " with a round ticket.")
            print("BOT: You want to return on " + leave_date_str + " at " + leave_time_str + ".")
            if final_chatbot:
                print("BOT: If you don't have any other questions you can type bye.")
        if chosen_dest_str is None:
            print("BOT: Please Choose a Destination.")
        if arrive_date_str is None:
            print("BOT: Please Choose a Date. To leave your origin on")
        if arrive_time_str is None:
            print("BOT: Please Choose a Time. To leave your origin on")
        if leave_date_str is None:
            print("BOT: Please Choose a Date to return.")
        if leave_time_str is None:
            print("BOT: Please Choose a Time to return.")

    if ticket_type == "open return" and leave_arrive is not None:

        if chosen_dest_str is not None and arrive_date_str is not None and leave_date_str is not None:
            print("BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " with an open return ticket.")
            print("BOT: You want to return on " + leave_date_str + ".")
            if final_chatbot:
                print("BOT: If you don't have any other questions you can type bye.")

        if chosen_dest_str is None:
            print("BOT: Please Choose a Destination.")
        if arrive_date_str is None:
            print("BOT: Please Choose a Date. To leave your origin on")
        if leave_date_str is None:
            print("BOT: Please Choose a Date to return.")

def selection(chosen_time, chosen_origin, chosen_dest, chosen_date, ticket_type):
    global chosen_origin_str
    global chosen_dest_str
    global arrive_date_str
    global arrive_time_str

    if chosen_time:
        chosen_time_beforecon = " ".join(chosen_time)
        arrive_time_str = time_conversion(chosen_time_beforecon)
        print("BOT: " + "You want to travel at " + arrive_time_str + ".")

    if chosen_origin:
        chosen_origin_str = " ".join(chosen_origin)
        chosen_origin_str, origin_code = station_selector(chosen_origin_str)
        print("BOT: " + "You want to travel from " + chosen_origin_str + ".")

    if chosen_dest:
        chosen_dest_str = " ".join(chosen_dest)
        chosen_dest_str, dest_code = station_selector(chosen_dest_str)
        print("BOT: " + "You want to go to " + chosen_dest_str + ".")

    if chosen_date:
        chosen_date_before = " ".join(chosen_date)
        cleaned_date = clean_date(chosen_date_before)
        chosen_date_date = date_conversion(cleaned_date)
        arrive_date_str = "".join(chosen_date_date)
        print("BOT: " + "You want to travel on " + arrive_date_str + ".")

    if ticket_type is not None:
        print("BOT: " + "You want to travel with a " + ticket_type + " ticket.")

def check_intention_by_keyword(sentence):
    global chosen_intention
    for word in sentence.split():
        for type_of_intention in intentions:
            if word.lower() in intentions[type_of_intention]["patterns"]:

                print("BOT: " + random.choice(intentions[type_of_intention]["responses"]))
                if type_of_intention == 'book':
                    print("BOT: note, if you would like to start over, just type 'reset' and I will start selection again.")
                # Do not change these lines
                if type_of_intention == 'greeting' and final_chatbot:
                    print("BOT: I am built for helping you with your travel plans. You can ask me about the time, date, and train tickets.\n(Hint: What time is it?)")
                return type_of_intention
    return chosen_intention

def check_intention_by_keyword_nr(sentence):
    global chosen_intention
    for word in sentence.split():
        for type_of_intention in intentions:
            if word.lower() in intentions[type_of_intention]["patterns"]:
                return type_of_intention
    return None

def lemmatize_and_clean(text):
    doc = nlp(text.lower())
    out = ""
    for token in doc:
        if not token.is_stop and not token.is_punct:
            out = out + token.lemma_ + " "
    return out.strip()

def check_ticket(user_input , loc):
    global ticket_type
    user_input = user_input.lower()
    ticket_list = ['one way', 'round', 'open ticket', 'open return']

    for ticket in ticket_list:
        if ticket in user_input:
            ticket_type = ticket_list[ticket_list.index(ticket)]
            if loc == 1:
                return ticket_list[ticket_list.index(ticket)]

    if loc == 1:
        return None

def find_similar_stations(target):
    global df
    station_names = [(name,idx) for idx, name in enumerate(df['combined'])]
    top_matches = process.extract(target, station_names, limit=5)

    results = [{'matched station': match[0][0], 'similarity score': match[1],
                'index': i+1, 'original index': match[0][1]} for i, match in enumerate(top_matches)]
    return results

def station_selector(target_station):
    global df
    # Replace 'your_spreadsheet.xlsx' with the path to your spreadsheet
    similar_stations = find_similar_stations(target_station)
    print("BOT: Here are the top 5 matching stations, please select the one you want to use:")

    for station in similar_stations:
        print(f"{station['index']} Station: {station['matched station']}, Similarity Score: {station['similarity score']}")

    selected_station = int(input("Enter the index of the station you want to select: "))

    station_df_index = similar_stations[selected_station-1]['original index']
    station_name = df.iloc[station_df_index]['name']
    station_tiploc = df.iloc[station_df_index]['tiploc']

    return station_name, station_tiploc




def ner_response(user_input):

    doc = nlp(user_input)
    chosen_origin = []
    chosen_dest = []
    chosen_date = []
    chosen_time = []
    global chosen_origin_str
    global chosen_dest_str
    global arrive_date_str
    global arrive_time_str
    global multiple_loc
    global leave_arrive
    global leave_date_str
    global leave_time_str
    global return_phrases
    global ticket_type
    multiple_loc = False

    # this checks the user input to see if they have entered a ticket type anywhere in the sentence allowing the user to phrase their sentence in any way
    check_ticket(user_input, 0)

    # this check the user input for the word 'from' as this word will always be present if the user is giving 2 locations in one input
    for key in doc:
        if key.text.lower() == "from":
            multiple_loc = True

    # this checks the user input for the specific words 'leave' and 'arrive' to determine if the user wants to leave or arrive at the time given
    if user_input == "leave":
        leave_arrive = "leave"
        print("BOT: You have chosen to leave at the time you given.")
        missing_info_response()
        return True
    if user_input == "arrive":
        leave_arrive = "arrive"
        print("BOT: You have chosen to arrive at your destination.")
        missing_info_response()
        return True

    # this segment is specific for the ticket types 'round' and 'open return' as they require a return date and time which requires extra processing to separate the two dates and times
    if ticket_type == "round" or ticket_type == "open return":
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

                if chosen_origin != []:
                    chosen_origin_str = " ".join(chosen_origin)
                    chosen_origin_str, origin_code = find_similar_stations(chosen_origin_str)
                    print("BOT: " + "You want to travel from " + chosen_origin_str + ".")

                if chosen_dest != []:
                    chosen_dest_str = " ".join(chosen_dest)
                    chosen_dest_str, dest_code = find_similar_stations(chosen_dest_str)
                    print("BOT: " + "You want to go to " + chosen_dest_str + ".")


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

                if may_check(go_to):
                    if "May" not in go_date:
                        go_date.append("May")

                if may_check(come_back):
                    if "May" not in back_date:
                        back_date.append("May")

                if go_time != []:
                    ar_time_beforecon = " ".join(go_time)
                    arrive_time_str = time_conversion(ar_time_beforecon)
                    print("BOT: " + "You want to travel at " + arrive_time_str + ".")

                if go_date != []:
                    chosen_date_before = " ".join(go_date)
                    cleaned_date = clean_date(chosen_date_before)
                    chosen_date_date = date_conversion(cleaned_date)
                    arrive_date_str = "".join(chosen_date_date)
                    print("BOT: " + "You want to travel on " + arrive_date_str + ".")

                if back_time != []:
                    back_time_beforecon = " ".join(back_time)
                    leave_time_str = time_conversion(back_time_beforecon)
                    print("BOT: " + "You want to return at " + leave_time_str + ".")

                if back_date != []:
                    if len(back_date[0]) < 4:
                        if back_date[0].lower() not in weekdays:

                            ord = clean_ord(back_date[0])
                            ord = int(ord)

                            fixed_date = chosen_date_date[:-2] + str(ord)

                            leave_date_date = datetime.strptime(fixed_date, "%Y-%m-%d").strftime("%Y-%m-%d")

                            leave_date_str = "".join(leave_date_date)

                            print("BOT: " + "You want to return on " + leave_date_str + ".")

                    else:
                        back_date_before = " ".join(back_date)
                        cleaned_date = clean_date(back_date_before)
                        back_date_date = date_conversion(cleaned_date)
                        leave_date_str = "".join(back_date_date)
                        print("BOT: " + "You want to return on " + leave_date_str + ".")

                missing_info_response()
                return True
    else:
        for token in doc:
            if token.pos_ == "VERB":
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

                        selection(chosen_time, chosen_origin, chosen_dest, chosen_date, ticket_type)
                        missing_info_response()
                        return True
        for ent in doc.ents:
            if ent.label_ == "DATE":
                date = ent.text
                date = clean_date(date)
                date = date_conversion(date)
                arrive_date_str = date
                print("BOT: You want to travel on " + date + ".")
                missing_info_response()
                return True
            if ent.label_ == "TIME":
                time = ent.text
                time = time_conversion(time)
                arrive_time_str = time
                print("BOT: You want to travel at " + time + ".")
                missing_info_response()
                return True
            if ent.label_ in loc_types:
                ent_index = ent.start
                if doc[ent_index - 1].text.lower() == "from":
                    chosen_origin.append(ent.text)
                    chosen_origin_str = " ".join(chosen_origin)
                    chosen_origin_str, origin_code = find_similar_stations(chosen_origin_str)
                    print("BOT: You want to travel from " + chosen_origin_str + ".")
                    missing_info_response()
                    return True
                if doc[ent_index - 1].text.lower() == "to":
                    chosen_dest.append(ent.text)
                    chosen_dest_str = " ".join(chosen_dest)
                    chosen_dest_str, dest_code = find_similar_stations(chosen_dest_str)
                    print("BOT: You want to travel to " + chosen_dest_str + ".")
                    missing_info_response()
                    return True
                else:
                    chosen_dest.append(ent.text)
                    chosen_dest_str = " ".join(chosen_dest)
                    chosen_dest_str, dest_code = find_similar_stations(chosen_dest_str)
                    print("I am assuming you want to travel to " + chosen_dest_str + ".")
                    missing_info_response()
                    return True
    return False

time_sentences = ''
date_sentences = ''
with open(sentences_path) as file:
    for line in file:
        parts = line.split(' | ')
        if parts[0] == 'time':
            time_sentences = time_sentences + ' ' + parts[1].strip()
        elif parts[0] == 'date':
            date_sentences = date_sentences + ' ' + parts[1].strip()

labels = []
sentences = []

doc = nlp(time_sentences)
for sentence in doc.sents:
    labels.append("time")
    sentences.append(sentence.text.lower().strip())

doc = nlp(date_sentences)
for sentence in doc.sents:
    labels.append("date")
    sentences.append(sentence.text.lower().strip())

def date_time_response(user_input):
    cleaned_user_input = lemmatize_and_clean(user_input)
    doc_1 = nlp(cleaned_user_input)
    similarities = {}
    for idx, sentence in enumerate(sentences):
        cleaned_sentence = lemmatize_and_clean(sentence)
        doc_2 = nlp(cleaned_sentence)
        similarity = doc_1.similarity(doc_2)
        similarities[idx] = similarity

    max_similarity_idx = max(similarities, key=similarities.get)

    # Minimum acceptable similarity between user's input and our Chatbot data
    # This number can be changed
    min_similarity = 0.75

    # Do not change these lines
    if similarities[max_similarity_idx] > min_similarity:
        if labels[max_similarity_idx] == 'time':
            print("BOT: " + "It’s " + str(datetime.now().strftime('%H:%M:%S')))
            if final_chatbot:
                print("BOT: You can also ask me what the date is today. (Hint: What is the date today?)")
        elif labels[max_similarity_idx] == 'date':
            print("BOT: " + "It’s " + str(datetime.now().strftime('%Y-%m-%d')))
            if final_chatbot:
                print(
                    "BOT: Now can you tell me where you want to go? (Hints: you can type in a city's name, or an organisation. I am going to London or I want to visit the University of East Anglia.)")
        return True

    return False


def ticket_type_response(ticket):

    if ticket == "one way":
        print("BOT: You have selected a one way ticket.")
        if chosen_dest_str != None and arrive_date_str != None and arrive_time_str != None:
            print(
                "BOT: You want to travel from " + chosen_origin_str + " to " + chosen_dest_str + " on " + arrive_date_str + " at " + arrive_time_str + " with a one way ticket.")
            if final_chatbot:
                print("BOT: If you don't have any other questions you can type bye.")
        if arrive_time_str == None:
            print("BOT: You have not chosen a time. please choose a time.")
        if chosen_dest_str == None:
            print("BOT: You have not chosen a destination. please choose a destination.")
        if arrive_date_str == None:
            print("BOT: You have not chosen a date. please choose a date.")

        if ticket == "round":
            print("BOT: You have selected a round ticket.")
            if chosen_dest_str != None and arrive_date_str != None and arrive_time_str != None and leave_date_str != None and leave_time_str != None:
                print(
                    "BOT: You want to travel from " + chosen_origin_str + " to " + chosen_dest_str + " on " + arrive_date_str + " at " + arrive_time_str + " with a round ticket.")
                print("BOT: You want to return on " + leave_date_str + " at " + leave_time_str + ".")
                if final_chatbot:
                    print("BOT: If you don't have any other questions you can type bye.")
            if chosen_dest_str == None:
                print("BOT: You have not chosen a destination. please choose a destination.")
            if arrive_date_str == None:
                print("BOT: You have not chosen a date to arrive. please choose a date.")
            if arrive_time_str == None:
                print("BOT: You have not chosen a time to arrive. please choose a time.")
            if leave_date_str == None:
                print("BOT: You have not chosen a date to leave. please choose a date.")
            if leave_time_str == None:
                print("BOT: You have not chosen a time to leave. please choose a time.")

        if ticket=="open ticket":
            print("BOT: You have selected a " + ticket + " ticket.")
            if chosen_dest_str != None and arrive_date_str != None:
                print("BOT: You want to travel from " + chosen_origin_str + " to " + chosen_dest_str + " on " + arrive_date_str + " with an open ticket.")
                if final_chatbot:
                    print("BOT: If you don't have any other questions you can type bye.")
            if chosen_dest_str == None:
                print("BOT: You have not chosen a destination. please choose a destination.")
            if arrive_date_str == None:
                print("BOT: You have not chosen a date to arrive. please choose a date.")

        if ticket=="open return":
            print("BOT: You have selected a " + ticket + " ticket.")
            if chosen_dest_str != None and arrive_date_str != None and leave_date_str != None:
                print("BOT: You want to travel from " + chosen_origin_str + " to " + chosen_dest_str + " on " + arrive_date_str + " with an open return ticket.")
                print("BOT: You want to return on " + leave_date_str + ".")
                if final_chatbot:
                    print("BOT: If you don't have any other questions you can type bye.")
            if chosen_dest_str == None:
                print("BOT: You have not chosen a destination. please choose a destination.")
            if arrive_date_str == None:
                print("BOT: You have not chosen a date to arrive. please choose a date.")
            if leave_date_str == None:
                print("BOT: You have not chosen a date to leave. please choose a date.")
def check_ticket(user_input, loc):
    global ticket_type
    user_input = user_input.lower()
    ticket_list = ['one way', 'round', 'open ticket', 'open return']

    for ticket in ticket_list:
        if ticket in user_input:
            ticket_type = ticket_list[ticket_list.index(ticket)]
            if loc == 1:
                return ticket_list[ticket_list.index(ticket)]

    if loc == 1:
        return None

def expert_response(user_input):
    ticket = check_ticket(user_input, 1)
    if ticket != None:
        ticket_type_response(ticket)
        return True
    return False


def goodbye_response():
    if ticket_type == None:
        print("BOT: You have not chosen a ticket type.")

    if arrive_date_str != None and chosen_dest_str != None and arrive_time_str != None and ticket_type != None:

        if ticket_type == "one way":
            print(
                "BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " at " + arrive_time_str + " with a one way ticket.")

        if ticket_type == "round":
            print(
                "BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " at " + arrive_time_str + " with a round ticket.")

        if ticket_type == "open ticket":
            print("BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " with an open ticket.")

        if ticket_type == "open return":
            print(
                "BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " with an open return ticket.")

    if chosen_dest_str == None:
        print("BOT: You have not chosen a destination.")

    if arrive_date_str == None:
        print("BOT: You have not chosen a date.")

    if arrive_time_str == None:
        print("BOT: You have not chosen a time.")

