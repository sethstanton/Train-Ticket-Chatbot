import json

with open('reset.json', 'r') as reset:
    default = json.load(reset)

with open('data.json', 'w') as file:
    json.dump(default, file, indent=4)

with open('pred_reset.json', 'r') as pd_rs:
    pd_default = json.load(pd_rs)

with open('pred_data.json', 'w') as pd_file:
    json.dump(pd_default, pd_file, indent=4)
