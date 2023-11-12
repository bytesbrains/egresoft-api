import json
import os

# Specify the absolute path to db.json
json_file_path = os.path.join(os.path.dirname(__file__), "db.json")

# Open and read the JSON file
with open(json_file_path, "r") as json_file:
    users_db = json.load(json_file)
