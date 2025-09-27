## Leveling Cog. Provides a leveling system for users based on their activity.
## Features:
# - Users earn XP for sending messages, with a cooldown to prevent spam
# - Level up notifications in the channel where the user leveled up
# - Commands to check user levels and XP
# - Leaderboard command to show top users by level
## Requirements:
# - discord.py
# - math for level calculations
# - datetime for cooldown management
import discord
from discord.ext import commands
import random
import math
from datetime import datetime, timedelta

## class Leveling Cog. For user leveling system.
class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_message_time = {}  # Track cooldowns per user
    
    ## Calculate level based on XP using a square root formula.
    ## The level increases as the square root of the XP divided by a multiplier.
    ## This creates a progressively harder leveling curve.
    def calculate_level(self, xp):
        """Calculate level based on XP"""
        multiplier = self.bot.config['features']['leveling']['level_multiplier']
        return int(math.sqrt(xp / multiplier)) + 1

    ## Calculate XP needed for a specific level.
    def calculate_xp_for_level(self, level):
        """Calculate XP needed for a specific level"""
        multiplier = self.bot.config['features']['leveling']['level_multiplier']
        return ((level - 1) ** 2) * multiplier
    
    ## Event listener for message events to give XP.
    ## Users earn XP for each message they send, subject to a cooldown to prevent spam.
    ## When a user levels up, a notification is sent in the channel.
    @commands.Cog.listener()
    async def on_message(self, message):
        """Give XP for messages"""
        if message.author.bot or not message.guild:
            return
        
        user_id = message.author.id
        guild_id = message.guild.id
        
        # Check cooldown
        cooldown = self.bot.config['features']['leveling']['xp_cooldown']
        now = datetime.now()
        
        if user_id in self.last_message_time:
            if (now - self.last_message_time[user_id]).seconds < cooldown:
                return
        
        self.last_message_time[user_id] = now
        
        # Get current XP and level
        current_xp, current_level = await self.bot.db.get_user_level_data(user_id, guild_id)
        
        # Add XP
        xp_gain = self.bot.config['features']['leveling']['xp_per_message']
        new_xp = current_xp + xp_gain
        new_level = self.calculate_level(new_xp)
        
        # Update database
        await self.bot.db.update_user_xp(user_id, guild_id, new_xp, new_level)
        
        # Check for level up
        if new_level > current_level:
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"{message.author.mention} reached level **{new_level}**!",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
            
            await message.channel.send(embed=embed)
    
    ## Command to check a user's level and XP.
    ## If no user is specified, shows the command invoker's level.
    ## Displays current level, total XP, and progress towards the next level with a progress bar
    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        """Check your or someone else's level"""
        user = member or ctx.author
        xp, level = await self.bot.db.get_user_level_data(user.id, ctx.guild.id)
        
        # Calculate XP for current and next level
        current_level_xp = self.calculate_xp_for_level(level)
        next_level_xp = self.calculate_xp_for_level(level + 1)
        xp_progress = xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        
        # Calculate progress percentage
        progress_percent = (xp_progress / xp_needed) * 100 if xp_needed > 0 else 100
        
        # Create progress bar
        progress_bar_length = 20
        filled_length = int(progress_percent / 100 * progress_bar_length)
        progress_bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
        
        embed = discord.Embed(
            title=f"📊 {user.display_name}'s Level",
            color=discord.Color.blue()
        )
        embed.add_field(name="Level", value=f"🏆 {level}", inline=True)
        embed.add_field(name="Total XP", value=f"⭐ {xp:,}", inline=True)
        embed.add_field(name="Progress", value=f"{progress_bar}\n{xp_progress:,} / {xp_needed:,} XP ({progress_percent:.1f}%)", inline=False)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        
        await ctx.send(embed=embed)
    
    ## Command to show the server leaderboard.
    ## Displays the top 10 users by level in the server.
    ## Uses an embed for better formatting.
    @commands.command()
    async def leaderboard(self, ctx):
        """Show the server leaderboard"""
        # This would require a more complex database query
        # For now, we'll show a placeholder
        embed = discord.Embed(
            title="🏆 Server Leaderboard",
            description="Leaderboard feature coming soon!",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

### Setup function to add the Leveling cog to the bot
async def setup(bot):
    await bot.add_cog(Leveling(bot))