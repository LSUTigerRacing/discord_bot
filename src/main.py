import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import sys

###
### (FOR INITIATING GOOGLE CLOUD ONLY) (DON'T WORRY ABOUT THIS BASICALLY) To create a docker container: docker build -t discord-bot .
### TO RUN THE CODE/BOT, RUN THIS COMMAND: python run_docker.py
###

load_dotenv()
test_token = os.getenv('TEST_TOKEN')
prod_token = os.getenv('PRODUCTION_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ask if to push bot update to prod or keep in test
target = os.getenv('TARGET', 'D').upper()  # Default to Dev if not set, TARGET set in .env

@bot.event
async def on_ready():
    print(f"Loaded cogs: {', '.join(bot.cogs.keys())}")
    if (target == 'P'):
        print("TigerRacing Bot is Live! (Prod)")
    elif (target == 'D'):
        print("TigerRacing Bot is Live! (Dev)")

"""load all .py files in cogs folder as extensions"""
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            print(f"Loading Cog: {filename[:-3]}")
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_connect():
    await load_extensions()

"""look main here"""
if __name__ == '__main__':
    try:
        if (target == 'P'):
            bot.run(prod_token, log_handler=handler, log_level=logging.DEBUG)
        elif (target == 'D'):
            bot.run(test_token, log_handler=handler, log_level=logging.DEBUG)
        else:
            print("No Valid Token Found (this means big oops)")
    except discord.LoginFailure:
        logging.critical("Invalid Discord Token")
        
# @bot.command()
# async def assign(ctx):
#     role = discord.utils.get(ctx.guild.roles, name="powertrain")
#     if role:
#         await ctx.author.add_roles(role)
#         await ctx.send(f"Assigned role to {ctx.author.mention}")
#     else:
#         await ctx.send("Role Doesn't Exist")