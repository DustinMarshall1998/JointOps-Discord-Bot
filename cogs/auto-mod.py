import discord
from discord.ext import commands
import json
import os

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # Place expensive resource loading here
        pass

# Module-level setup function for adding the cog
async def setup(bot):
    await bot.add_cog(AutoMod(bot))