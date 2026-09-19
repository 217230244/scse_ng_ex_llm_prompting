## Import the necessary modules
import json
import os

## Logic for loading and reading from a JSON file. 
## The function must return only the items
def load_items(filename):
    with open(filename, "r") as file:
        data = json.load(file)

    return data["items"]


## Logic for getting only those items that are not yet claimed 
## It should return only the items that are unclaimed
def get_unclaimed_items(items):
    result = []

    for item in items:
        if item["status"].strip().lower() == "unclaimed":
            result.append(item)

    return result
    

## Logic to save the result to a JSON file.
## The function should create the directory if it does not exist and save the result in a JSON format.
def save_result(result, filename):
    folder = os.path.dirname(filename)

    if folder != "":
        os.makedirs(folder, exist_ok=True)

    with open(filename, "w") as file:
        json.dump(result, file, indent=2)