from .NLP_booking import *
from .NLP_predict import *
import requests
import csv
import json


# This is the main file for the NLP chatbot. It is responsible for the main logic.
# It uses the functions from the other files to get the responses relevant to the user input.
# It also uses the LLM to get responses for inputs that the chatbot does not understand.


# This function is used for the LLM. It sends the user input to the LLM and returns the response.
llama_url = "http://localhost:11434/api/chat"

def llama3_response(user_input):
    data = {
        "model": "llama3",
        "messages": [
            {
                "role": "user",
                "content": user_input
            }
        ],
        "stream": False
    }

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(llama_url, headers=headers, json=data)

    return (response.json()['message']['content'])


# This is the main function for the chatbot. It takes the user input and returns the chatbot response.
def main(input):
    global final_chatbot
    global printout

    update()

    final_chatbot = True

    printout.clear()

    user_input = input


    # This is used to store past user inputs.
    with open(past_inputs, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_input])


    # This is used to check if the user input is "reset". If it is, the chatbot will reset the selection.
    if user_input == "reset":
        with open(reset_path, 'r') as reset:
            default = json.load(reset)

        with open(data_path, 'w') as file:
            json.dump(default, file, indent=4)

        with open(pred_reset_path, 'r') as pd_rs:
            pd_default = json.load(pd_rs)

        with open(pred_data_path, 'w') as pd_file:
            json.dump(pd_default, pd_file, indent=4)
        printout.append("I have reset the selection. start by telling me your ticket type. or type 'predict' to predict a train.")
        return printout

    # This is used to check the intention of the user input. It determines what the user wants to do.
    data['chosen_intention'] = check_intention_by_keyword(user_input)
    with open(data_path, 'w') as file:
        json.dump(data, file, indent=4)


    # This is used to branch the path of the chatbot based on the previous user input.
    if data['station_selector']:
        if data['selected'] == None:
            data['selected'] = user_input
            with open(data_path, 'w') as file:
                json.dump(data, file, indent=4)

            with open(past_inputs, 'r') as past:
                user_input = past.readlines()[-2]

        else:
            data['selected'] = int(user_input)
            with open(data_path, 'w') as file:
                json.dump(data, file, indent=4)

            with open(past_inputs, 'r') as past:
                user_input = past.readlines()[-3]

            user_input = user_input.replace('\n', '').replace('\r', '')

            if re.fullmatch(r'\d', user_input):
                with open(past_inputs, 'r') as past:
                    user_input = past.readlines()[-2]


    if pd_data['pred_station_selector']:
        if pd_data['pred_selected'] == None:
            pd_data['pred_selected'] = user_input
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)

            with open(past_inputs, 'r') as past:
                user_input = past.readlines()[-2]

        else:
            pd_data['pred_selected'] = int(user_input)
            with open(pred_data_path, 'w') as file:
                json.dump(pd_data, file, indent=4)

            with open(past_inputs, 'r') as past:
                user_input = past.readlines()[-3]

            user_input = user_input.replace('\n', '').replace('\r', '')

            if re.fullmatch(r'\d',user_input):
                with open(past_inputs, 'r') as past:
                    user_input = past.readlines()[-2]

    # This is used to remove any new line characters from the user input.
    user_input = user_input.replace('\n', '').replace('\r', '')


    printout.pop(0)

    # If the intention is "goodbye", the chatbot will say goodbye and reset the selection.
    if data['chosen_intention'] == 'goodbye':
        goodbye_response()


        with open(reset_path, 'r') as reset:
            default = json.load(reset)

        with open(data_path, 'w') as file:
                json.dump(default, file, indent=4)

        with open(pred_reset_path, 'r') as pd_rs:
            pd_default = json.load(pd_rs)

        with open(pred_data_path, 'w') as pd_file:
            json.dump(pd_default, pd_file, indent=4)

        return printout


    # This is used to branch the path of the chatbot based on the intention of the user input.
    # Depending on the intention, the chatbot will call the relevant functions to get the response.
    if data['chosen_intention'] == 'book':
        ner_response(user_input)
        if printout[0]:
            printout.pop(0)
            return printout
        else:
            printout.pop(0)
            date_time_response(user_input)
            if printout[0]:
                printout.pop(0)
                return printout
            else:
                printout.pop(0)
                expert_response(user_input)
                if printout[0]:
                    printout.pop(0)
                    return printout
                else:
                    printout.pop(0)
                    ner_response(user_input)
                    if printout[0]:
                        printout.pop(0)
                        return printout
                    else:
                        printout.pop(0)
                        if check_intention_by_keyword_nr(user_input) == "book":
                            return printout
                        else:
                            printout.append("Sorry I don't understand that. I have sent your message to a LLM and this is the response:")
                            printout.append(f"{llama3_response(user_input)}")
                            return printout
    if data['chosen_intention'] == None:
        ner_response(user_input)
        if printout[0]:
            printout.pop(0)
            return printout
        else:
            printout.pop(0)
            date_time_response(user_input)
            if printout[0]:
                printout.pop(0)
                return printout
            else:
                printout.pop(0)
                expert_response(user_input)
                if printout[0]:
                    printout.pop(0)
                    return printout
                else:
                    printout.pop(0)
                    ner_response(user_input)
                    if printout[0]:
                        printout.pop(0)
                        return printout
                    else:
                        printout.pop(0)
                        printout.append( "Sorry I don't understand that. I have sent your message to a LLM and this is the response:")
                        printout.append(f"{llama3_response(user_input)}")
                        return printout


    if data['chosen_intention'] == 'greeting':
        data['chosen_intention'] = None
        ner_response(user_input)
        if printout[0]:
            printout.pop(0)
            return printout
        else:
            printout.pop(0)
            date_time_response(user_input)
            if printout[0]:
                printout.pop(0)
                return printout
            else:
                printout.pop(0)
                expert_response(user_input)
                if printout[0]:
                    printout.pop(0)
                    return printout
                else:
                    printout.pop(0)
                    ner_response(user_input)
                    if printout[0]:
                        printout.pop(0)
                        return printout
                    else:
                        printout.pop(0)
                        if check_intention_by_keyword_nr(user_input) == "greeting":
                            return printout
                        else:
                            printout.append("Sorry I don't understand that. I have sent your message to a LLM and this is the response:")
                            printout.append(f"{llama3_response(user_input)}")
                            return printout

    if data['chosen_intention'] == 'predict':
        pred_ner_response(user_input)
        if printout[0]:
            printout.pop(0)
            return printout
        else:
            printout.pop(0)
            date_time_response(user_input)
            if printout[0]:
                printout.pop(0)
                return printout
            else:
                printout.pop(0)
                pred_ner_response(user_input)
                if printout[0]:
                    printout.pop(0)
                    return printout
                else:
                    printout.pop(0)
                    if check_intention_by_keyword_nr(user_input) == "predict":
                        return printout
                    else:
                        printout.append("Sorry I don't understand that. I have sent your message to a LLM and this is the response:")
                        printout.append(f"{llama3_response(user_input)}")
                        return printout

    # If the intention is not "goodbye", "book", "greeting" or "predict", the chatbot will assume the user wants to book a train ticket.
    if data['chosen_intention'] != 'goodbye' and data['chosen_intention'] != 'book' and data['chosen_intention'] != None and data['chosen_intention'] != 'greeting' and data['chosen_intention'] != 'predict':
        date_time_response(user_input)
        if printout[0]:
            printout.pop(0)
            return printout
        else:
            printout.pop(0)
            expert_response(user_input)
            if printout[0]:
                printout.pop(0)
                return printout
            else:
                printout.pop(0)
                ner_response(user_input)
                if printout[0]:
                    printout.pop(0)
                    return printout
                else:
                    printout.pop(0)
                    if check_intention_by_keyword_nr(user_input) == "book":
                        return printout
                    else:
                        printout.append("Sorry I don't understand that. I have sent your message to a LLM and this is the response:")
                        printout.append(f"{llama3_response(user_input)}")
                        return printout

if __name__ == "__main__":

    # This is used to test the chatbot. The user input is hardcoded and the chatbot response is printed.
    # It is done in this way for reproducibility.

    # output = main("hello")
    # print(output)
    # output1 = main("I want to book a ticket")
    # print(output1)
    # output2 = main("round")
    # print(output2)
    # output3 = main("I would like to go to from Cambridge to Norwich on sunday at 5pm returning on monday at 5pm")
    # print(output3)
    # output4 = main("1")
    # print(output4)
    # output5 = main("1")
    # print(output5)
    # output6 = main("leave")
    # print(output6)
    # output7 = main("bye")
    # print(output7)

    # output = main("hello")
    # print(output)
    # output1 = main("I want to predict a ticket")
    # print(output1)
    # output2 = main("future train")
    # print(output2)
    # output3 = main("I would like to go to from Norwich to Colchester on sunday at 5pm")
    # print(output3)
    # output4 = main("1")
    # print(output4)
    # output5 = main("1")
    # print(output5)
    # output6 = main("bye")
    # print(output6)

    output = main("hello")
    print(output)
    output1 = main("I want to predict a ticket")
    print(output1)
    output2 = main("active train")
    print(output2)
    output3 = main("I am currently at Colchester and I am going to Norwich and I am delayed by 30 minutes")
    print(output3)
    output4 = main("1")
    print(output4)
    output5 = main("1")
    print(output5)
    output6 = main("bye")
    print(output6)





    exit()


