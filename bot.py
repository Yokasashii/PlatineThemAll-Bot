import discord
import os
from dotenv import load_dotenv
load_dotenv()

print("Loading bot...")

intents = discord.Intents.all()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

bot.run(os.getenv('DISCORD_TOKEN'))
