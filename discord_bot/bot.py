import discord
import requests
from dotenv import load_dotenv
from os import environ, getenv

load_dotenv()


async def send_message(message):
    username = str(message.author)
    url = getenv("RASA_ENDPOINT") or "http://localhost:5005/webhooks/rest/webhook"
    data = {
        "sender": username,
        "message": message.content,
    }

    response = requests.post(url, json=data)

    print(response.json())

    for resp in response.json():
        if resp["recipient_id"] != username:
            continue
        await message.reply(resp["text"])


class RasaBot(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return
        print(f"Got message from {message.author}: {message.content}")
        await send_message(message)


intents = discord.Intents.default()
intents.message_content = True

client = RasaBot(intents=intents)
client.run(environ["DISCORD_TOKEN"])
