import discord
from discord.ext import commands
import json
import os
import logging

class FormulaSAE(commands.Cog, name="fsae"):
    def __init__(self, bot):
        self.bot = bot
