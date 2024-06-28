import json
import random
import spacy.cli
import requests
import csv
from datetime import datetime, timedelta
from datetime import datetime
from bs4 import BeautifulSoup
from difflib import get_close_matches, SequenceMatcher
from experta import *
import warnings
warnings.filterwarnings('ignore')



intentions_path = "../AICW2/mychatbots/ticketfinder/intentions.json"
sentences_path = "../AICW2/mychatbots/ticketfinder/sentences.txt"

weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'today', 'tomorrow', 'week']

chosen_origin_str = "Norwich"
chosen_dest_str = None
arrive_date_str = None
chosen_time_str = None
ticket_type = None

origin_code = "NRW"
dest_code = None

multiple_loc = False

chosen_intention = None

# Opening JSON file and return JSON object as a dictionary

with open(intentions_path) as f:
    intentions = json.load(f)

final_chatbot = False

def clean_date(date):
    date = nlp(date)
    out = ""
    for token in date:
        if token.pos_ == "DET":
            continue
        else:
            out += token.text + " "
    return out.rstrip()

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
    global chosen_time_str
    global ticket_type

    if chosen_date_str != None and chosen_dest_str != None and chosen_time_str != None and ticket_type != None:

        if ticket_type == "one way":
            print("BOT: You want to travel to " + chosen_dest_str + " on " + chosen_date_str + " at " + chosen_time_str + " with a one way ticket.")

        if ticket_type == "round":
            print("BOT: You want to travel to " + chosen_dest_str + " on " + chosen_date_str + " at " + chosen_time_str + " with a round ticket.")

        if ticket_type == "open ticket":
            print("BOT: You want to travel to " + chosen_dest_str + " on " + chosen_date_str + " with an open ticket.")

        if ticket_type == "open return":
            print("BOT: You want to travel to " + chosen_dest_str + " on " + chosen_date_str + " with an open return ticket.")

    if chosen_date_str != None and chosen_dest_str != None and chosen_time_str != None and ticket_type == None:
        print("BOT: You want to travel from " + chosen_origin_str + " to " + chosen_dest_str + " on " + chosen_date_str + " at " + chosen_time_str + ".")
        if final_chatbot:
            print("BOT: Could you please tell me what kind of ticket you are looking for? (You can just ask for one way, round and open return tickets.)")

    if chosen_dest_str == "Norwich":
        print("BOT: No Origin given. Defaulting to Norwich. (if you would like to change this please say 'from' and then the location)")

    if chosen_dest_str == None:
        print("BOT: Please Choose a Destination.")

    if chosen_date_str == None:
        print("BOT: Please Choose a Date.")

    if chosen_time_str == None:
        print("BOT: Please Choose a Time.")


def check_intention_by_keyword(sentence):
    global chosen_intention
    for word in sentence.split():
        for type_of_intention in intentions:
            if word.lower() in intentions[type_of_intention]["patterns"]:

                print("BOT: " + random.choice(intentions[type_of_intention]["responses"]))
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

nlp = spacy.load("en_core_web_sm")

labels = []
sentences = []

url = "https://www.4icu.org/gb/a-z/"
content = requests.get(url)
soup = BeautifulSoup(content.text, 'html.parser')

universities = {}
for tr in soup.find_all('tr')[2:]:
    tds = tr.find_all('td')
    if len(tds) == 3:
        university = {}
        university['Rank'] = tds[0].text
        university['Name'] = tds[1].text
        university['City'] = tds[2].text.replace(' ...', '')
        universities[tds[1].text] = university



def get_best_match_university(user_input):
    university_list = universities.keys()
    matches = get_close_matches(user_input, university_list, n=1, cutoff=0.6)
    if len(matches) > 0:
        best_match = matches[0]
    else:
        return None

    sm = SequenceMatcher(None, user_input, best_match)
    score = sm.ratio()
    if score >= 0.6:
        return best_match
    else:
        return None




def ner_response(user_input):

    check_ticket(user_input, 0)

    doc = nlp(user_input)
    chosen_origin = []
    chosen_dest = []
    chosen_date = []
    chosen_time = []
    global chosen_origin_str
    global chosen_dest_str
    global arrive_date_str
    global chosen_time_str
    global multiple_loc
    multiple_loc = False

    for key in doc:
        if key.text.lower() == "from":
            multiple_loc = True

    for token in doc:
        if token.pos_ == "VERB":
            choose = False
            if token.text.lower() == "going":
                choose = True
            if token.text.lower() == "visit":
                choose = True
            if token.text.lower() == "travel":
                choose = True
            if token.text.lower() == "go":
                choose = True
            if token.text.lower() == "choose":
                choose = True
            if token.text.lower() == "get":
                choose = True
            if token.text.lower() == "goes":
                choose = True
            if choose:
                if any(doc.ents):
                    for ent in doc.ents:
                        if multiple_loc:
                            ent_index = ent.start
                            if doc[ent_index - 1].text.lower() == "from":
                                if ent.label_ == "GPE":
                                    chosen_origin.append(ent.text)
                                if ent.label_ == "ORG":
                                    chosen_origin.append(ent.text)
                                if ent.label_ == "LOC":
                                    chosen_origin.append(ent.text)
                                if ent.label_ == "NORP":
                                    chosen_origin.append(ent.text)
                                if ent.label_ == "PERSON":
                                    chosen_origin.append(ent.text)
                            if doc[ent_index - 1].text.lower() == "to":
                                if ent.label_ == "GPE":
                                    chosen_dest.append(ent.text)
                                if ent.label_ == "ORG":
                                    chosen_dest.append(ent.text)
                                if ent.label_ == "LOC":
                                    chosen_dest.append(ent.text)
                                if ent.label_ == "NORP":
                                    chosen_dest.append(ent.text)
                                if ent.label_ == "PERSON":
                                    chosen_dest.append(ent.text)

                            if ent.label_ == "DATE":
                                chosen_date.append(ent.text)
                            if ent.label_ == "TIME":
                                chosen_time.append(ent.text)
                        else:
                            if ent.label_ == "GPE":
                                chosen_dest.append(ent.text)
                            if ent.label_ == "ORG":
                                chosen_dest.append(ent.text)
                            if ent.label_ == "LOC":
                                chosen_dest.append(ent.text)
                            if ent.label_ == "NORP":
                                chosen_dest.append(ent.text)
                            if ent.label_ == "PERSON":
                                chosen_dest.append(ent.text)
                            if ent.label_ == "DATE":
                                chosen_date.append(ent.text)
                            if ent.label_ == "TIME":
                                chosen_time.append(ent.text)



                    if chosen_time != []:
                        chosen_time_beforecon = " ".join(chosen_time)
                        chosen_time_str = time_conversion(chosen_time_beforecon)
                        print("BOT: " + "You want to travel at " + chosen_time_str + ".")

                    if chosen_origin != []:
                        chosen_origin_str = " ".join(chosen_origin)
                        print("BOT: " + "You want to travel from " + chosen_origin_str + ".")

                    if chosen_dest != []:
                        chosen_dest_str = " ".join(chosen_dest)
                        print("BOT: " + "You want to go to " + chosen_dest_str + ".")

                    if chosen_date != []:
                        chosen_date_before = " ".join(chosen_date)
                        cleaned_date = clean_date(chosen_date_before)
                        chosen_date_date = date_conversion(cleaned_date)
                        chosen_date_str = "".join(chosen_date_date)
                        print("BOT: " + "You want to travel on " + chosen_date_str + ".")

                    if chosen_origin == []:
                        print("BOT: As no origin was given, I am assuming you want to travel from Norwich. (If you would like to change this please say 'from' and then the location)")


                    if chosen_date_str != None and chosen_dest_str != None and chosen_time_str != None and ticket_type != None:
                        print("BOT: You want to travel from " + chosen_origin_str + " to " + chosen_dest_str + " on " + chosen_date_str + " at " + chosen_time_str + " with ticket type " + ticket_type + ".")
                        if final_chatbot:
                            print("BOT: If you don't have any other questions you can type bye.)")
                        return True
                    missing_info_response()
                    return True
    for ent in doc.ents:
        if ent.label_ == "DATE":
            date = ent.text
            date = clean_date(date)
            date = date_conversion(date)
            chosen_date_str = date
            print("BOT: You want to travel on " + date + ".")
            missing_info_response()
            return True
        if ent.label_ == "TIME":
            time = ent.text
            time = time_conversion(time)
            chosen_time_str = time
            print("BOT: You want to travel at " + time + ".")
            missing_info_response()
            return True
        if ent.label_ == "GPE" or ent.label_ == "ORG" or ent.label_ == "LOC" or ent.label_ == "NORP" or ent.label_ == "PERSON":
            ent_index = ent.start
            if doc[ent_index - 1].text.lower() == "from":
                chosen_origin.append(ent.text)
                chosen_origin_str = " ".join(chosen_origin)
                print("BOT: You want to travel from " + chosen_origin_str + ".")
                missing_info_response()
                return True
            if doc[ent_index - 1].text.lower() == "to":
                chosen_dest.append(ent.text)
                chosen_dest_str = " ".join(chosen_dest)
                print("BOT: You want to travel to " + chosen_dest_str + ".")
                missing_info_response()
                return True
            else:
                chosen_dest.append(ent.text)
                chosen_dest_str = " ".join(chosen_dest)
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


class Book(Fact):
    """Info about the booking ticket."""
    pass

class TrainBot(KnowledgeEngine):
  @Rule(Book(ticket='one way'))
  def one_way(self):
    print("BOT: You have selected a one way ticket. Have a good trip.")
    if final_chatbot:
      print("BOT: If you don't have any other questions you can type bye.")

  @Rule(Book(ticket='round'))
  def round_way(self):
    print("BOT: You have selected a round ticket. Have a good trip.")
    if final_chatbot:
      print("BOT: If you don't have any other questions you can type bye.")

  @Rule(AS.ticket << Book(ticket=L('open ticket') | L('open return')))
  def open_ticket(self, ticket):
    print("BOT: You have selected a " + ticket["ticket"] +".  Have a good trip.")
    if final_chatbot:
      print("BOT: If you don't have any other questions you can type bye.")


# engine = TrainBot()
# engine.reset()
# engine.declare(Book(ticket=choice(['one way', 'round', 'open ticket', 'open return'])))
# engine.run()

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
def expert_response(user_input):
    engine = TrainBot()
    engine.reset()
    ticket = check_ticket(user_input , 1)
    if ticket != None:
        engine.declare(Book(ticket=ticket))
        engine.run()
        return True

    return False

def goodbye_response():

    if ticket_type == None:
        print("BOT: You have not chosen a ticket type.")


    if arrive_date_str != None and chosen_dest_str != None and chosen_time_str != None and ticket_type != None:

        if ticket_type == "one way":
            print("BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " at " + chosen_time_str + " with a one way ticket.")

        if ticket_type == "round":
            print("BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " at " + chosen_time_str + " with a round ticket.")

        if ticket_type == "open ticket":
            print("BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " with an open ticket.")

        if ticket_type == "open return":
            print("BOT: You want to travel to " + chosen_dest_str + " on " + arrive_date_str + " with an open return ticket.")

    if chosen_dest_str == None:
        print("BOT: You have not chosen a destination.")

    if arrive_date_str == None:
        print("BOT: You have not chosen a date.")

    if chosen_time_str == None:
        print("BOT: You have not chosen a time.")






final_chatbot = True

flag=True

print("BOT: Hi there! How can I help you?.\n (If you want to exit, just type bye!)")


while(flag==True):


    user_input = input()
    with open('../AICW2/mychatbots/ticketfinder/past_inputs.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_input])


    chosen_intention = check_intention_by_keyword(user_input)


    if chosen_intention == 'goodbye':

        goodbye_response()
        flag=False
        #change intention for different responses (prediction etc)

        # if one way ticket I only need destination, date and time
        # if round ticket I need destination, date and time arriving and date and time leaving
        # if open ticket I need destination and date no extra info is needed
        # if open return ticket I need destination and date arriving and date leaving no extra info is needed

    if chosen_intention == 'book':
        if not ner_response(user_input):
            if not date_time_response(user_input):
                if not expert_response(user_input):
                    if not ner_response(user_input):
                        if check_intention_by_keyword_nr(user_input) != "book":
                            print("BOT: Sorry I don't understand that. Please rephrase your statement.")
    if chosen_intention == None:
        if not ner_response(user_input):
            if not date_time_response(user_input):
                if not expert_response(user_input):
                    if not ner_response(user_input):
                        print("BOT: Sorry I don't understand that. Please rephrase your statement.")

    if chosen_intention == 'greeting':
        chosen_intention = None
        if not ner_response(user_input):
            if not date_time_response(user_input):
                if not expert_response(user_input):
                    if not ner_response(user_input):
                        continue

    if chosen_intention != 'goodbye' and chosen_intention != 'book' and chosen_intention != None and chosen_intention != 'greeting':
        if not date_time_response(user_input):
            if not expert_response(user_input):
                if not ner_response(user_input):
                    print("BOT: Sorry I don't understand that. Please rephrase your statement.")

