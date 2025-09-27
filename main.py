### Main bot file for JointOps Discord Bot Version 1.0.3
##Made By: @CodeData_, @gritherness
## Features:
# - Moderation commands (ban, kick, mute, warn)
# - Fun commands (joke, meme, 8ball)
# - Utility commands (ping, serverinfo, userinfo)
# - Economy system (balance, daily, shop)
# - Leveling system (xp, rank)
# - Music playback (play, pause, skip, queue)
# - Admin commands (setprefix, setwelcome)
# - Help command
# - Auto moderation (anti-spam, anti-link)
## - Customizable prefixes per server
## - Persistent data storage using SQLite
## - Error handling and logging
## - Environment variable management with python-dotenv

## Requirements:
# - discord.py
# - youtube-dl
# - aiosqlite
# - python-dotenv
# - logging
# - json
# - asyncio
# - os
# - sqlite3
##Importing the necessary libraries (discord.py, youtube-dl, os, asyncio, logging, dotenv, json, sqlite3)
import discord
from discord.ext import commands
import os
import asyncio
import youtube_dl
import logging
from dotenv import load_dotenv
import json
from database.db_manager import DatabaseManager

# Load environment variables
load_dotenv()

# Setup logging
# Create a logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging settings to log to a file and console simultaneously with timestamps and log levels 
# included in the log messages for better traceability of events and errors. 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/JointOps.log'),
        logging.StreamHandler()
    ]
)

# Create a logger instance for the bot module to log messages specific to bot operations. 
logger = logging.getLogger(__name__)

# Load configuration from config.json file.
config = {}
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
        logger.info("Loaded configuration from config.json")
        logger.debug(f"Configuration: {config}")
except FileNotFoundError:
    logger.error(f"config.json file not found at {config_path}. Please ensure it exists in the project directory.")
    raise
## Handle JSON decode errors gracefully and log them for debugging purposes.
except json.JSONDecodeError as e:
    logger.error(f"Error decoding config.json: {e}")
    raise

## Define the bot class and its functionalities including command handling, event listeners, and extension loading.
# The bot class inherits from commands.Bot to utilize the command framework provided by discord.py.
# It initializes with specific intents, a dynamic command prefix function, and sets up the database connection.
class JointOps(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.voice_states = True
        ## Initialize the bot with command prefix, intents, and other settings.
        # Use a dynamic prefix function to allow custom prefixes per server.
        # Disable the default help command to implement a custom one later.
        # Make commands case insensitive for user convenience.
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        ## Store configuration and initialize the database manager.
        # This allows the bot to access configuration settings and interact with the database for persistent storage.
        # The DatabaseManager class handles all database operations.
        self.config = config
        self.db = DatabaseManager()

    # Function to get the command prefix for each guild
    # If the message is in a DM, use the default prefix from environment variables or '!'
    # If the guild has a custom prefix set in the database, use that; otherwise, use the default prefix.    
    async def get_prefix(self, message):
        """Get custom prefix for each guild"""
        if message.guild is None:
            return os.getenv('BOT_PREFIX', '!')
        
        prefix = await self.db.get_guild_prefix(message.guild.id)
        return prefix or os.getenv('BOT_PREFIX', '!')
    
    async def setup_hook(self):
        """Initialize the bot"""
        await self.db.initialize()
        await self.load_extensions()
        logger.info("Bot setup completed!")
    
    # Load all extensions (cogs) for modular functionality
    # Each extension corresponds to a specific feature set of the bot, such as moderation, fun, utility, etc.
    # The extensions are loaded asynchronously to ensure non-blocking operation during bot startup.
    # Errors during loading are caught and logged for debugging purposes.
    async def load_extensions(self):
        """Load all cogs"""
        extensions = [
            'cogs.moderation',
            'cogs.fun',
            'cogs.utility',
            'cogs.economy',
            'cogs.leveling',
            'cogs.music',
            'cogs.admin',
            'cogs.help',
            'cogs.auto_mod',
        ]
        
        # Load each extension and log the status
        for extension in extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
    
    # Event listener for when the bot is ready
    # Logs the bot's connection status and sets its presence (status message) to indicate it's online and ready.
    @commands.Cog.listener()
    async def on_ready(self):
        """Bot ready event"""
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # Set bot status
        activity = discord.Game(name=f"{os.getenv('BOT_PREFIX', '/')}help | v{config['bot']['version']}")
        await self.change_presence(status=discord.Status.online, activity=activity)
    
    # Event listener for when the bot joins a new guild
    # Adds the guild to the database for tracking and logs the event.
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """When bot joins a new guild"""
        await self.db.add_guild(guild.id)
        logger.info(f"Joined guild: {guild.name} ({guild.id})")
    
    ## Global error handler for commands
    # This function handles common command errors and provides user feedback.
    # It logs unhandled errors for further investigation.
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command on cooldown. Try again in {error.retry_after:.2f} seconds.")
        else:
            logger.error(f"Unhandled error: {error}")
            await ctx.send("❌ An unexpected error occurred!")

## Main function to run the bot with proper asynchronous handling and graceful shutdown.
# It ensures that the bot starts with the token from environment variables and handles exceptions appropriately.
# The bot will log shutdown requests and errors for better maintenance and debugging.
# The asyncio.run() function is used to manage the event loop and ensure proper cleanup on exit.
async def main():
    bot = JointOps()
    
    try:
        await bot.start(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())