import discord
import os
from dotenv import load_dotenv
load_dotenv()

print("Bot is loading")
intents = discord.Intents.all()
bot = discord.Client(intents=intents)

