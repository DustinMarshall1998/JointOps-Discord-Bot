## Auto-Mod Cog (anti-spam, anti-link)
# Imports (discord.py, commands extension, json, os, asyncio)
import discord
from discord.ext import commands
import json
import os
import asyncio

## class AutoMod Cog. For automatic moderation features.
class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_threshold = 5  # Number of messages in short time to consider as spam
        self.user_message_times = {}  # Track user message timestamps
        self.link_keywords = ["http://", "https://", "www.", ".com", ".net", ".org"]  # Simple link detection

    # Event listener for message events to implement anti-spam and anti-link features.
    # Deletes messages that are considered spam or contain links if auto-mod is enabled for the guild.
    # Sends a warning message to the user when their message is deleted.
    # Logs moderation actions to the mod_logs table in the database.
    # Requires the bot to have the necessary permissions to manage messages.
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        guild_id = message.guild.id
        auto_mod_enabled = await self.bot.db.is_auto_mod_enabled(guild_id)
        if not auto_mod_enabled:
            return
        
        # Anti-spam check
        now = message.created_at.timestamp()
        user_id = message.author.id
        if user_id not in self.user_message_times:
            self.user_message_times[user_id] = []
        self.user_message_times[user_id].append(now)
        
        # Remove timestamps older than 10 seconds
        self.user_message_times[user_id] = [t for t in self.user_message_times[user_id] if now - t < 10]
        
        if len(self.user_message_times[user_id]) > self.spam_threshold:
            try:
                await message.delete()
                warning = await message.channel.send(f"⚠️ {message.author.mention}, please stop spamming!")
                await asyncio.sleep(5)
                await warning.delete()
                
                # Log the action
                await self.bot.db.log_mod_action(
                    guild_id=guild_id,
                    user_id=user_id,
                    moderator_id=self.bot.user.id,
                    action="Auto-Moderation: Spam",
                    reason="User sent too many messages in a short time."
                )
            except discord.Forbidden:
                pass  # Bot lacks permissions to delete messages
        
        # Anti-link check
        if any(keyword in message.content.lower() for keyword in self.link_keywords):
            try:
                await message.delete()
                warning = await message.channel.send(f"⚠️ {message.author.mention}, posting links is not allowed!")
                await asyncio.sleep(5)
                await warning.delete()
                
                # Log the action
                await self.bot.db.log_mod_action(
                    guild_id=guild_id,
                    user_id=user_id,
                    moderator_id=self.bot.user.id,
                    action="Auto-Moderation: Link",
                    reason="User posted a link."
                )
            except discord.Forbidden:
                pass  # Bot lacks permissions to delete messages    
    async def cog_load(self):
        # Place expensive resource loading here
        pass

# Module-level setup function for adding the cog
async def setup(bot):
    await bot.add_cog(AutoMod(bot))