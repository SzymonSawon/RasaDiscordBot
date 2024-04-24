# Python 3.9.19:
https://github.com/pyenv/pyenv?tab=readme-ov-file#other-operations

# Tutorial:
1. Before training you should check for errors with:
```
rasa data validate
```
2. To train model:
```
rasa train
```
3. In another terminal in project directory run(and don't close it):
```
rasa run actions
```
4.  To chat with bot in shell:
```
rasa shell
```

# Workflow:

1.Create intent in data/nlu.yml
```
- intent: math_equation
  examples: |
    - calculate [3*1/4](equation)
    - process [90+1*80/(4*10)](equation)
    - compute [3*9+5/8](equation)
```
2.[Optional] Create custom action in actions/actions.py
```
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
```
3. Add your intents and actions to new story in data/stories.yml:
```
stories:

- story: calculate
  steps:
  - intent: greet
  - action: utter_greet
  - intent: math_equation
  - action: action_math_equation
```
4. Each change add to domain.yml file

5. [Optional] To use variables in custom actions, you need to add variable to intent:
```
compute [3*9+5/8](equation)
```
Then add your entities and slots to domain.yml:
```
entities:
 - equation
 - information

slots:
  equation:
    type: text
    mappings:
    - type: from_entity
      entity: equation
```
