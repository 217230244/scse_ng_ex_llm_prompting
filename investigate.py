## Import the necessary modules
import json

from ollama import chat

## Import the function from the module parse_data
from parse_data import (
    load_items,
    get_unclaimed_items,
    save_result
)

## Build your prompt based on the description the user provides 
## and the items that are available in the lost-and-found database.
## The model must follow the rules listed in the README file
## The function should return the system prompt and the user prompt.
## You may need to use json.dumps() to convert the available_items list into a JSON string.

def build_prompt(description, available_items):
    items_json = json.dumps(available_items, indent=2)

    system_prompt = (
        "You are a campus lost-and-found assistant.\n"
        "Use only the JSON data provided in the user prompt. "
        "Do not use any outside information.\n"
        "Not every detail of an item has to match for it to be a possible match.\n"
        "Return ONLY valid JSON. Do not include explanations, markdown or extra text.\n"
        "The JSON must have exactly this structure:\n"
        "{\n"
        '    "matches": ["ITEM_ID"],\n'
        '    "confidence": "LOW"\n'
        "}\n"
        "Rules:\n"
        '- "matches" must contain all possible matching item IDs. '
        "If there are no matches, use an empty list.\n"
        '- "confidence" shows how confident you are about the matches. '
        "It must be exactly one of: LOW, MEDIUM, HIGH.\n"
    )

    user_prompt = (
        "Available items (JSON):\n"
        + items_json
        + "\n\nLost item description:\n"
        + description
    )

    return system_prompt, user_prompt
    

## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
## The function should return the response from Qwen.
def ask_qwen(system_prompt, user_prompt):
    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.message.content


## Logic to parse the response from Qwen and return the result. 
## You may need to use json.loads() to convert the response string into a suitable Python data structure.
def parse_response(response_text):
    text = response_text.strip()

    # Remove markdown code fences if the model added them anyway
    if text.startswith("```"):
        first_newline = text.find("\n")

        if first_newline != -1:
            text = text[first_newline + 1:]
        else:
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
    


## Logic to validate the result returned by Qwen.
## It should check if the result is a dictionary, contains the keys "matches" and "confidence", and that the values are of the correct type.
## If everything is correct, then it should check if the item IDs in the "matches" list are valid IDs .
def validate_result(result, available_items):
    if type(result) != dict:
        return False

    if "matches" not in result or "confidence" not in result:
        return False

    if len(result) != 2:
        return False

    if type(result["matches"]) != list:
        return False

    if type(result["confidence"]) != str:
        return False

    if result["confidence"] not in ["LOW", "MEDIUM", "HIGH"]:
        return False

    valid_ids = []
    for item in available_items:
        valid_ids.append(item["id"])

    for item_id in result["matches"]:
        if type(item_id) != str:
            return False

        if item_id not in valid_ids:
            return False

    return True


## Logic to display the matches found by Qwen in a user-friendly format.
## It should look something like this:
""" 
CAMPUS LOST-AND-FOUND ASSISTANT
==================================================

Describe the item you lost: I lost a black bag somewhere

Searching for possible matches...

MATCH RESULT
--------------------------------------------------
Confidence: MEDIUM

Possible matches:

ID: F101
Item: backpack
Color: black
Location: Library 2nd floor
Date found: 2026-09-15

Result saved to output/match_result.json
 """
## If no matches are found, it should display a message indicating that no matches were found, along with the empty list
def display_matches(result, available_items):
    print("\nMATCH RESULT")
    print("-" * 50)
    print(f"Confidence: {result['confidence']}")
    print()

    if len(result["matches"]) == 0:
        print("No matches found.")
        print("Possible matches: []")
        return

    print("Possible matches:")

    for match_id in result["matches"]:
        for item in available_items:
            if item["id"] == match_id:
                print()
                print(f"ID: {item['id']}")
                print(f"Item: {item['item']}")
                print(f"Color: {item['color']}")
                print(f"Location: {item['location']}")
                print(f"Date found: {item['date']}")
    

## Control center for the entire program.
def main():
    items = load_items("found_items.json")
    available_items = get_unclaimed_items(items)

    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)
    print()

    description = input("Describe the item you lost: ").strip()
    print()
    print("Searching for possible matches...")

    system_prompt, user_prompt = build_prompt(description, available_items)
    response_text = ask_qwen(system_prompt, user_prompt)
    result = parse_response(response_text)

    if validate_result(result, available_items):
        display_matches(result, available_items)
        save_result(result, "output/match_result.json")
        print()
        print("Result saved to output/match_result.json")
    else:
        print("The model returned an invalid result.")


if __name__ == "__main__":
    main()