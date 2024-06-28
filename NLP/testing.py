import spacy.cli
from datetime import *

nlp = spacy.load("en_core_web_sm")


user_input = "May I go to London on the 1st April and I want to return on 8th April"


weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'today', 'tomorrow', 'week']
return_phrases = ['coming back', 'returning', 'return', 'departing', 'leaving']

chosen_origin = []
chosen_dest = []
chosen_date = []
chosen_time = []

def may_check(phrase):
    lower = phrase.lower()
    if "may" in lower:
        return True

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


for phrase in return_phrases:
    if phrase in user_input:


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
            if len(back_date[0]) < 4 and len(back_date) == 1:
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