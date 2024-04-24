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
from bs4 import BeautifulSoup


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
                f"https://en.wikipedia.org/wiki/{user_input}")
            url = f"https://en.wikipedia.org/wiki/{user_input}"
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = soup.select('div.mw-parser-output > p')
                for paragraph in paragraphs:
                    text = paragraph.get_text().strip()
                    if text:
                        dispatcher.utter_message(
                            text=f"Result: {text} and {user_input} and {url}")
            else:
                dispatcher.utter_message(text="Site error")

        except Exception as e:
            dispatcher.utter_message(text=f"Error: {e}")

        return []
