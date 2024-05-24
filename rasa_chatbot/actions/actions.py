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
            with open(path, "w") as file:
                json.dump({}, file)

        with open(path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

        task = tracker.latest_message['text']
        if user_name not in data:
            data[user_name] = {"tasks": [{"task": task}]}
        else:
            data[user_name]["tasks"].append({"task": task})

        with open(path, "w") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

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
            return []

        with open(path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                dispatcher.utter_message(text="Przepraszam, ale mam błąd w danych, czy mógłbyś mnie zrestartować?")
                return []

        if user_name not in data:
            dispatcher.utter_message(text="Nie masz jeszcze zadań")
            return []

        task = tracker.latest_message['text']
        tasks = data[user_name]["tasks"]
        task_found = False
        for i in tasks:
            if i["task"] == task:
                tasks.remove(i)
                task_found = True
                break

        if not task_found:
            dispatcher.utter_message(text=f"Zadanie '{task}' nie zostało znalezione.")
        else:
            with open(path, "w") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            dispatcher.utter_message(text=f"Usunięto zadanie: {task}")

        return []




class ActionListTasks(Action):
    def name(self) -> str:
        return "action_list_tasks"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        path = Path("./data/tasks.json")

        metadata = tracker.latest_message.get("metadata", {})
        user_name = metadata.get("user_name", "nieznany użytkownik")

        if not path.exists():
            dispatcher.utter_message(text="Nie masz jeszcze zadań")
            return []

        with open(path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                dispatcher.utter_message(text="Przepraszam, ale mam błąd w danych, czy mógłbyś mnie zrestartować?")
                return []

        if user_name not in data or not data[user_name]["tasks"]:
            dispatcher.utter_message(text="Nie masz jeszcze zadań")
            return []

        task_names = [task["task"] for task in data[user_name]["tasks"]]
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
