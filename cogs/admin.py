## Admin Cog for managing bot settings and extensions. 
## Commands include setting server prefix, viewing settings, loading/unloading/reloading cogs, and shutting down the bot.
## Permissions checks ensure only authorized users can execute sensitive commands.
## Uses embeds for better message formatting and user feedback.
## Requires discord.py library and a database manager for persistent storage.
## Environment variables used:
# - OWNER_ID: Discord user ID of the bot owner for permission checks.
# - BOT_PREFIX: Default command prefix for the bot. Defaults to '!' if not set.

# Recent edits to this file: Added setstatus command to change bot's playing status.

# Imports (discord.py, commands extension, json, os)
import discord
from discord.ext import commands
import json
import os

## class Admin Cog. For managing bot settings and extensions.
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    #check if user is bot owner. Used for permission checks on sensitive commands.
    def is_owner():
        """Check if user is bot owner"""
        def predicate(ctx):
            return ctx.author.id == int(os.getenv('OWNER_ID', 0))
        return commands.check(predicate)
    
    # Command to set the server prefix. Only the bot owner can use this command.
    # Validates the prefix length and updates it in the database.
    # Sends a confirmation embed message upon success.  
    @commands.command()
    @is_owner()
    async def setprefix(self, ctx, *, prefix):
        """Set custom prefix for this server"""
        if len(prefix) > 5:
            await ctx.send("❌ Prefix cannot be longer than 5 characters!")
            return
        
        await self.bot.db.set_guild_prefix(ctx.guild.id, prefix)
        
        embed = discord.Embed(
            title="⚙️ Prefix Updated",
            description=f"Server prefix changed to: `{prefix}`",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    ## Command to show current server settings.
    ## Displays settings like prefix, auto moderation status, leveling system status, and economy system status.
    ## Uses an embed for better formatting.
    ## Requires administrator permissions to use.
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        """Show server settings"""
        prefix = await self.bot.db.get_guild_prefix(ctx.guild.id) or os.getenv('BOT_PREFIX', '!')
        
        embed = discord.Embed(
            title="⚙️ Server Settings",
            color=discord.Color.blue()
        )
        embed.add_field(name="Prefix", value=f"`{prefix}`", inline=True)
        embed.add_field(name="Auto Moderation", value="✅ Enabled", inline=True)
        embed.add_field(name="Leveling System", value="✅ Enabled", inline=True)
        embed.add_field(name="Economy System", value="✅ Enabled", inline=True)
        
        await ctx.send(embed=embed)
    
    ## Command to reload a cog (extension).
    ## Only the bot owner can use this command.
    ## Attempts to reload the specified cog and sends a success or failure embed message.
    ## Cogs are located in the 'cogs' directory.
    @commands.command()
    @is_owner()
    async def reload(self, ctx, *, extension):
        """Reload a cog"""
        try:
            await self.bot.reload_extension(f"cogs.{extension}")
            embed = discord.Embed(
                title="🔄 Extension Reloaded",
                description=f"Successfully reloaded `{extension}`",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Reload Failed",
                description=f"Failed to reload `{extension}`: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    ## Command to load a cog (extension).
    ## Only the bot owner can use this command.
    ## Attempts to load the specified cog and sends a success or failure embed message.
    ## Cogs are located in the 'cogs' directory.
    @commands.command()
    @is_owner()
    async def load(self, ctx, *, extension):
        """Load a cog"""
        try:
            await self.bot.load_extension(f"cogs.{extension}")
            embed = discord.Embed(
                title="📥 Extension Loaded",
                description=f"Successfully loaded `{extension}`",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Load Failed",
                description=f"Failed to load `{extension}`: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    ## Command to unload a cog (extension).
    ## Only the bot owner can use this command.
    ## Attempts to unload the specified cog and sends a success or failure embed message.
    ## Cogs are located in the 'cogs' directory.
    @commands.command()
    @is_owner()
    async def unload(self, ctx, *, extension):
        """Unload a cog"""
        try:
            await self.bot.unload_extension(f"cogs.{extension}")
            embed = discord.Embed(
                title="📤 Extension Unloaded",
                description=f"Successfully unloaded `{extension}`",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Unload Failed",
                description=f"Failed to unload `{extension}`: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    ## Command to shut down the bot.
    ## Only the bot owner can use this command.
    ## Sends a shutdown confirmation embed message before closing the bot.
    @commands.command()
    @is_owner()
    async def shutdown(self, ctx):
        """Shutdown the bot"""
        embed = discord.Embed(
            title="🔄 Shutting Down",
            description="Bot is shutting down...",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        await self.bot.close()

    ## Command to change the bot's playing status.
    ## Requires administrator permissions to use.
    ## Updates the bot's presence to show the specified status message.
    ## Sends a confirmation embed message upon success.
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setstatus(self, ctx, *, status: str):
        """Change the bot's playing status"""
        activity = discord.Game(name=status)
        await self.bot.change_presence(activity=activity)
        embed = discord.Embed(
            title="✅ Status Updated",
            description=f"Bot status changed to: **Playing {status}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

## Setup function to add the Admin cog to the bot
async def setup(bot):
    await bot.add_cog(Admin(bot))