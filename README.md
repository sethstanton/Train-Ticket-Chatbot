# AI Chatbot Project

Welcome to the GitHub page for our AI Chatbot project. This repository contains the necessary files and instructions to set up and run our chatbot.

## Project Structure

The main chatbot files are located in the following directory:

AICW2/mychatbots/ticketfinder/


## Setting Up the Environment

To use our chatbot, we provide a Conda environment file called `Final_env.yml`. However, please keep in mind that this file does not install all the dependencies required for the project.

### Prerequisite: Installing Llama3

First, you'll need to install Llama3. Follow the instructions provided in the link below to install Llama3:
[Llama3 Installation Guide](https://github.com/meta-llama/llama-recipes/blob/main/recipes/quickstart/Running_Llama3_Anywhere/Running_Llama_on_Mac_Windows_Linux.ipynb)

We used the 7B model for our project as it was the fastest and most space-efficient.

### Setting Up SpaCy

To use SpaCy, you will need to download the model used by the chatbot. This can be done in the terminal window for the Conda environment using the following command:

python -m spacy download en_core_web_sm


## Handling Dependencies

The provided environment file might not contain all the necessary dependencies due to limitations with exporting environments using Conda. To resolve any missing dependencies, we recommend installing them based on the error messages shown in the console. Unfortunately, we cannot provide a complete list of dependencies.

Thank you for using our AI Chatbot project.
