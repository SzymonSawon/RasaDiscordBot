# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

import json
from rasa_sdk.events import SlotSet

# Tests
from pathlib import Path


class ActionMathEqation(Action):

    def name(self) -> Text:
        return "action_math_equation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            user_input = tracker.get_slot('equation')
            output = eval(user_input)
            dispatcher.utter_message(text=f"Result: {output}")

        except Exception as e:
            dispatcher.utter_message(text=f"Error: {e}")

        return []


class ActionGetWikipedia(Action):

    def name(self) -> Text:
        return "action_get_wikipedia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            user_input = tracker.get_slot('information')
            response = requests.get(
                f"https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exchars=300&explaintext=1&redirects=1&titles={user_input}")
            if response.status_code == 200:
                data = response.json()
                for page_id, page in data["query"]["pages"].items():
                    dispatcher.utter_message(
                        text=f"{page['extract']}\n---\nSee more: https://en.wikipedia.org/wiki/{page['title']}")
            else:
                dispatcher.utter_message(text="Site error")

        except Exception as e:
            dispatcher.utter_message(text=f"Error: {e}")

        return []


class ActionAddTask(Action):
    def name(self) -> Text:
        return "action_add_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        path = Path("./data/tasks.json")

        if not path.exists():  # Jeśli plik nie istnieje, utwórz go
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as file:
                json.dump({"tasks": []}, file, indent=2)

        with open("./tasks.json", "r") as file:
            data = json.load(file)

        task = tracker.latest_message['text']
        data["tasks"].append({"task": task, "state": "wip"})

        with open("./tasks.json", "w") as file:
            data = json.dump(data, file)

        dispatcher.utter_message(text=f"Dodano zadanie: {task}")

        return []


class ActionListTasks(Action):
    def name(self) -> str:
        return "action_list_tasks"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        path = Path("./data/tasks.json")

        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as file:
                json.dump({"tasks": []}, file, indent=2)

        with open("./tasks.json", "r") as file:
            data = json.load(file)

        task_names = [task["task"] for task in data["tasks"]]

        task_list_text = ", ".join(task_names)

        dispatcher.utter_message(text=f"Twoje zadania to: {task_list_text}")
        return [SlotSet("task_list", task_list_text)]


class ActionGetPokemon(Action):
    def name(self) -> str:
        return "action_get_pokemon"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        user_input = tracker.get_slot('pokemon')
        url = f"https://pokeapi.co/api/v2/pokemon/{user_input.lower()}"
        response = requests.get(url)
        if response.status_code == 200:
            pokemon_api = response.json()
            pokemon_info = {
                "name": pokemon_api["name"],
                "height": pokemon_api["height"],
                "weight": pokemon_api["weight"],
                "abilities": [ability["ability"]["name"] for ability in pokemon_api["abilities"]],
                "types": [type_data["type"]["name"] for type_data in pokemon_api["types"]]
            }
            dispatcher.utter_message(
                text=f"""\nNazwa: {pokemon_info["name"]}
                         \nWzrost: {pokemon_info["height"]}
                         \nWaga: {pokemon_info["weight"]}
                         \nTyp: {', '.join(pokemon_info["types"])}
                         """)
        else:
            dispatcher.utter_message(text=f"Nie udało się dotrzeć do informacji")
