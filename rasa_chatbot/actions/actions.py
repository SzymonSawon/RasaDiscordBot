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
import time

# Tests
from pathlib import Path

class ActionAddTask(Action):
    def name(self) -> Text:
        return "action_add_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        path = Path("./data/tasks.json")
        metadata = tracker.latest_message.get("metadata", {})
        user_name = metadata.get("user_name", "nieznany użytkownik")
        if not path.exists():
            dispatcher.utter_message(text="Nie masz jeszcze zadań")


        with open("./data/tasks.json", "r") as file:
            data = json.load(file)

        task = tracker.latest_message['text']
        if str(user_name)[1:] not in data:
            data.update({str(user_name)[1:]:{"tasks": [{"task": task}]}})
        else:
            data[str(user_name)[1:]]["tasks"].append({"task": task})

        with open("./data/tasks.json", "w") as file:
            data = json.dump(data, file)

        dispatcher.utter_message(text=f"Dodano zadanie: {task}")

        return []


class ActionRemoveTask(Action):
    def name(self) -> Text:
        return "action_remove_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        path = Path("./data/tasks.json")
        metadata = tracker.latest_message.get("metadata", {})
        user_name = metadata.get("user_name", "nieznany użytkownik")
        if not path.exists():
            dispatcher.utter_message(text="Nie masz jeszcze zadań")


        with open("./data/tasks.json", "r") as file:
            data = json.load(file)

        if str(user_name)[1:] not in data:
            dispatcher.utter_message(text="Nie masz jeszcze zadań")
            return []
        else:
            task = tracker.latest_message['text']
            for i in data[str(user_name)[1:]]["tasks"]:
                if (i["task"] == task):
                    data[str(user_name)[1:]]["tasks"].remove(i)

        with open("./data/tasks.json", "w") as file:
            data = json.dump(data, file)

        dispatcher.utter_message(text=f"Usunięto zadanie: {task}")

        return []


class ActionListTasks(Action):
    def name(self) -> str:
        return "action_list_tasks"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        path = Path("./data/tasks.json")

        metadata = tracker.latest_message.get("metadata", {})
        user_name = metadata.get("user_name", "nieznany użytkownik")

        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as file:
                json.dump({"tasks": []}, file, indent=2)

        with open("./data/tasks.json", "r") as file:
            data = json.load(file)

        if str(user_name)[1:] not in data:
            dispatcher.utter_message(text="Nie masz jeszcze zadań")
            return []
        else:
            task_names = [task["task"] for task in data[str(user_name)[1:]]["tasks"]]

        task_list_text = "\n \u2022 " + " \n \u2022 ".join(task_names)

        dispatcher.utter_message(text=f"Twoje zadania to: {task_list_text}")
        return [SlotSet("task_list", task_list_text)]


class ActionGetPokemon(Action):
    def name(self) -> str:
        return "action_get_pokemon"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        user_input = tracker.get_slot('pokemon')
        if (user_input is None):
            dispatcher.utter_message(
                text="Nie ma takiego pokemona")
            return []
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
                    text=f"""Twój pokemon:
    \u2022 Nazwa: {pokemon_info["name"]}
    \u2022 Wzrost: {pokemon_info["height"]}
    \u2022 Waga: {pokemon_info["weight"]}
    \u2022 Typ: {', '.join(pokemon_info["types"])}
                         """)
        else:
            dispatcher.utter_message(
                text="Nie udało się dotrzeć do informacji")


class ActionGetQuote(Action):
    def name(self) -> str:
        return "action_get_quote"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        url = "https://api.quotable.io/quotes/random"
        response = requests.get(url)
        if response.status_code == 200:
            quote_api = response.json()

            dispatcher.utter_message(
                text=f"Cytat specjalnie dla ciebie: {quote_api[0]['content']} \nAutor: {quote_api[0]['author']}")
        else:
            dispatcher.utter_message(
                text="Nie udało się dotrzeć do informacji")
