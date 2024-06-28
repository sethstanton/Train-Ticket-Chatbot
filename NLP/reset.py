import json

with open('data/reset.json', 'r') as reset:
    default = json.load(reset)

with open('data/data.json', 'w') as file:
    json.dump(default, file, indent=4)