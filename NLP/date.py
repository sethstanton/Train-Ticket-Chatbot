from datetime import *
import spacy.cli
import csv

nlp = spacy.load('en_core_web_sm')

weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def clean_date(date):
    out = ""
    for token in date:
        if token.pos_ == "DET":
            continue
        else:
            out += token.text + " "
    return out
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



def date_conversion_month(month):
    words = month.split()
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
        return datetime.strptime(month, "%d %B %Y").replace(year = datetime.today().year + 1).strftime("%Y-%m-%d")
    else:
        return date

def time_conversion(time):

    if "noon" in str(time).lower():
        return datetime.strptime("12:00", "%H:%M").strftime("%H:%M")
    if "midnight" in str(time).lower():
        return datetime.strptime("00:00", "%H:%M").strftime("%H:%M")
    if "afternoon" in str(time).lower():
        return datetime.strptime("15:00", "%H:%M").strftime("%H:%M")
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

print(date_conversion("sunday"))
print(date_conversion("15th January"))


print(time_conversion("midnight"))

print(date_conversion_month("15th January"))

doc = nlp("the 5th December 2024")

print(clean_date(doc))

with open('../AICW2/mychatbots/ticketfinder/past_inputs.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Past User Inputs"])

user_input = input()

reader = csv.reader(open('../AICW2/mychatbots/ticketfinder/stations.csv', 'r'))

indatabase = False
for row in reader:
    if user_input.upper() in row:
        indatabase = True
        break
if indatabase:
    print("Station found")
if not indatabase:
    print("Station not found")
