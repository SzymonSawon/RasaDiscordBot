import discord
import requests
from dotenv import load_dotenv
from os import environ, getenv

load_dotenv()

#timer for pomodoro
import asyncio
import datetime
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
async def send_message(message):
    username = str(message.author)
    url = getenv("RASA_ENDPOINT") or "http://localhost:5005/webhooks/rest/webhook"
    user_name = str(message.author.name)
    data = {
        "sender": username,
        "message": message.content,
        "metadata": { 
            "user_name": user_name
        }
    }

    response = requests.post(url, json=data)

    print(response.json())

    for resp in response.json():
        if resp["recipient_id"] != username:
            continue
        await message.reply(resp["text"])

async def start_pomodoro_timer(channel):
    duration = 10      
    message = await channel.send(f"Pomodoro będzie trwało {str(datetime.timedelta(seconds=duration))}")

    for i in range(duration - 1, -1, -1):
        await asyncio.sleep(1) 
        await message.edit(content=f"Praca: {str(datetime.timedelta(seconds=i))}")

    duration = 3     
    message = await channel.send(f"Zaraz przerwa! {str(datetime.timedelta(seconds=duration))}")

    for i in range(duration - 1, -1, -1):
        await asyncio.sleep(1) 
        await message.edit(content=f"Odliczanie: {str(datetime.timedelta(seconds=i))}")


    duration = 5      
    message = await channel.send(f"Zaczynamy przerwę! {str(datetime.timedelta(seconds=duration))}")

    for i in range(duration - 1, -1, -1):
        await asyncio.sleep(1) 
        await message.edit(content=f"Przerwa: {str(datetime.timedelta(seconds=i))}")

    await channel.send("Koniec pomodoro!")

class RasaBot(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return 
        if message.content.lower() == "!timer":
            print(f"Got message from {message.author}: {message.content}")
            await start_pomodoro_timer(message.channel)
        else:
            print(f"Got message from {message.author}: {message.content}")
            await send_message(message)


intents.message_content = True

client = RasaBot(intents=intents)
client.run(environ["DISCORD_TOKEN"])
