
# past_inputs = r"C:\Users\ryanl\Documents\Artificial Intelligence\AI project\AI-project\NLP\data\past_inputs.csv"
# data_path = r"C:\Users\ryanl\Documents\Artificial Intelligence\AI project\AI-project\NLP\data\data.json"
# reset_path = r"C:\Users\ryanl\Documents\Artificial Intelligence\AI project\AI-project\NLP\data\reset.json"
# intentions_path = r"C:\Users\ryanl\Documents\Artificial Intelligence\AI project\AI-project\NLP\data\intentions.json"
# sentences_path = r"C:\Users\ryanl\Documents\Artificial Intelligence\AI project\AI-project\NLP\data\sentences.txt"
# stations_path = r"C:\Users\ryanl\Documents\Artificial Intelligence\AI project\AI-project\NLP\data\stations.csv"
# pred_data_path = r"C:\Users\ryanl\Documents\Artificial Intelligence\AI project\AI-project\NLP\data\pred_data.json"
# pred_reset_path = r"C:\Users\ryanl\Documents\Artificial Intelligence\AI project\AI-project\NLP\data\pred_reset.json"
# pred_stations_path = r"C:\Users\ryanl\Documents\Artificial Intelligence\AI project\AI-project\NLP\data\pred_stations.csv"

past_inputs = r"C:\Users\Ryan\Documents\AI project\AI-project\NLP\data\past_inputs.csv"
data_path = r"C:\Users\Ryan\Documents\AI project\AI-project\NLP\data\data.json"
reset_path = r"C:\Users\Ryan\Documents\AI project\AI-project\NLP\data\reset.json"
intentions_path = r"C:\Users\Ryan\Documents\AI project\AI-project\NLP\data\intentions.json"
sentences_path = r"C:\Users\Ryan\Documents\AI project\AI-project\NLP\data\sentences.txt"
stations_path = r"C:\Users\Ryan\Documents\AI project\AI-project\NLP\data\stations.csv"
pred_data_path = r"C:\Users\Ryan\Documents\AI project\AI-project\NLP\data\pred_data.json"
pred_reset_path = r"C:\Users\Ryan\Documents\AI project\AI-project\NLP\data\pred_reset.json"
pred_stations_path = r"C:\Users\Ryan\Documents\AI project\AI-project\NLP\data\pred_stations.csv"


import json
import random
import spacy.cli
from datetime import datetime, timedelta
import warnings
import re
warnings.filterwarnings('ignore')

nlp = spacy.load("en_core_web_sm")

labels = []
sentences = []



# this has not been put into a seperate file as implementation would be more complex
weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'today', 'tomorrow', 'week']
verbs = ['going', 'visit', 'travel', 'go', 'choose', 'get', 'goes']
loc_types = ['GPE', 'ORG', 'LOC', 'NORP', 'PERSON']

data = json.loads(open(data_path).read())
pd_data = json.loads(open(pred_data_path).read())

printout = []


# Opening JSON file and return JSON object as a dictionary

with open(intentions_path) as f:
    intentions = json.load(f)

final_chatbot = True

def print_out():
    global printout
    for message in printout:
        print(message)

# this function checks to see if the word may is in the text supplied as in some cases may can be used to indicate a date
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
    if ":" in str(time):
        if "am" in str(time).lower() or "pm" in str(time).lower():
            time = time[:-2]
            return datetime.strptime(time, "%H:%M").strftime("%H:%M")
        return datetime.strptime(time, "%H:%M").strftime("%H:%M")
    if "am" in str(time).lower() or "pm" in str(time).lower():
        return datetime.strptime(time, "%I%p").strftime("%H:%M")

def pred_time_conversion(time):

    split = time.split()
    total = 0
    if "and" in split:
        for word in split:
            if word == "minutes" or word == "minute":
                index = split.index(word)
                match = re.search(r'\d+', split[index - 1])
                if match:
                    total = total + int(match.group())
            if word == "hours" or word == "hour":
                index = split.index(word)
                match = re.search(r'\d+', split[index - 1])
                if match:
                    total = total + (int(match.group()) * 60)
        return total

    for word in split:
        if word == "minutes" or word == "minute":
            match = re.search(r'\d+', time)
            if match:
                return int(match.group())
        if word == "hours" or word == "hour":
            match = re.search(r'\d+', time)
            if match:
                return (int(match.group()) * 60)





def check_intention_by_keyword(sentence):
    global final_chatbot

    global printout
    for word in sentence.split():
        for type_of_intention in intentions:
            if word.lower() in intentions[type_of_intention]["patterns"]:

                printout.append("" + random.choice(intentions[type_of_intention]["responses"]))
                if type_of_intention == 'book':
                    printout.append("note, if you would like to start over, just type 'reset' and I will start selection again.")
                if type_of_intention == 'predict':
                    printout.append("(for a train that you are actively on type 'Active Train')\n"
                                    "(for a train that you are going to take type 'Future Train')\n"
                                    "(prediction cannot be made for current selection as it may not be on the route)"
                                    "you can type 'reset' to start over.")
                # Do not change these lines
                if type_of_intention == 'greeting' and final_chatbot:
                    printout.append("I am built for helping you with your travel plans. You can ask me about the time, date, and train tickets.\n(Hint: What time is it?)")
                printout.insert(0, True)
                return type_of_intention
    printout.insert(0, False)
    return data['chosen_intention']

def check_intention_by_keyword_nr(sentence):
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
    global final_chatbot
    global printout
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
            printout.append("" + "It’s " + str(datetime.now().strftime('%H:%M:%S')))
            if final_chatbot:
                printout.append("You can also ask me what the date is today. (Hint: What is the date today?)")
        elif labels[max_similarity_idx] == 'date':
            printout.append("" + "It’s " + str(datetime.now().strftime('%Y-%m-%d')))
            if final_chatbot:
                printout.append(
                    "I can help you book a train if you want, firstly let me know what type of ticket you want. (one way, round, open ticket, open return)")
        printout.insert(0, True)
        

    printout.insert(0, False)
