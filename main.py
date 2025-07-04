import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print("TigerRacing Bot is Live!")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name="powertrain")
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"Assigned role to {ctx.author.mention}")
    else:
        await ctx.send("Role Doesn't Exist")
bot.run(token, log_handler=handler, log_level=logging.DEBUG)