### Main bot file for JointOps Discord Bot Version 1.0.2
##Made by: @CodeData_




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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load configuration
config = {}
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    logger.error(f"config.json file not found at {config_path}. Please ensure it exists in the project directory.")
    raise
except json.JSONDecodeError as e:
    logger.error(f"Error decoding config.json: {e}")
    raise

class JointOps(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        self.config = config
        self.db = DatabaseManager()
        
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
        
        for extension in extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
    
    async def on_ready(self):
        """Bot ready event"""
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # Set bot status
        activity = discord.Game(name=f"{os.getenv('BOT_PREFIX', '/')}help | v{config['bot']['version']}")
        await self.change_presence(status=discord.Status.online, activity=activity)
    
    async def on_guild_join(self, guild):
        """When bot joins a new guild"""
        await self.db.add_guild(guild.id)
        logger.info(f"Joined guild: {guild.name} ({guild.id})")
    
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

# Initialize and run bot
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