## Database management module for the Discord bot
## Handles SQLite database interactions for persistent data storage
## Features:
# - Guild settings (prefix, welcome channel, mod log channel)
# - User economy (balance, bank, daily rewards)
# - User levels (xp, level)
# - Moderation logs (ban, kick, mute records)
## Requirements:
# - aiosqlite
# - sqlite3
# - logging
# - os
import os
import sqlite3
import aiosqlite
import logging

# Setup logging
# Create a logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')
logger = logging.getLogger(__name__)

## DatabaseManager class to handle all database operations
class DatabaseManager:
    def __init__(self, db_path="bot_database.db"):
        self.db_path = db_path
    
    ## Initialize the database and create necessary tables if they don't exist
    ## This method sets up tables for guild settings, user economy, user levels, and moderation logs.
    ## It ensures that the database is ready for use when the bot starts.
    async def initialize(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Guild settings
            await db.execute('''
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT DEFAULT "!",
                    welcome_channel INTEGER,
                    leave_channel INTEGER,
                    mod_log_channel INTEGER,
                    auto_mod_enabled BOOLEAN DEFAULT 1
                )
            ''')
            
            # User economy
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_economy (
                    user_id INTEGER,
                    guild_id INTEGER,
                    balance INTEGER DEFAULT 0,
                    bank INTEGER DEFAULT 0,
                    last_daily TEXT,
                    last_work TEXT,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            
            # User levels
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_levels (
                    user_id INTEGER,
                    guild_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    last_message TEXT,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            
            # Moderation logs
            await db.execute('''
                CREATE TABLE IF NOT EXISTS mod_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    action TEXT,
                    reason TEXT,
                    timestamp TEXT
                )
            ''')
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    ## Guild settings methods. For managing guild-specific configurations.
    ## Methods include getting and setting the command prefix.
    async def get_guild_prefix(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT prefix FROM guild_settings WHERE guild_id = ?",
                (guild_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else None
    
    ## Set the command prefix for a specific guild.
    async def set_guild_prefix(self, guild_id, prefix):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO guild_settings (guild_id, prefix) VALUES (?, ?)",
                (guild_id, prefix)
            )
            await db.commit()
    
    ## Add a new guild to the database when the bot joins it. 
    async def add_guild(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)",
                (guild_id,)
            )
            await db.commit()
    
    # Economy methods. For managing user economy data.
    # Methods include getting and updating user balances.
    async def get_user_balance(self, user_id, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT balance, bank FROM user_economy WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            result = await cursor.fetchone()
            return result if result else (0, 0)
    
    async def update_user_balance(self, user_id, guild_id, balance=None, bank=None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO user_economy (user_id, guild_id) VALUES (?, ?)",
                (user_id, guild_id)
            )
            
            if balance is not None:
                await db.execute(
                    "UPDATE user_economy SET balance = ? WHERE user_id = ? AND guild_id = ?",
                    (balance, user_id, guild_id)
                )
            
            if bank is not None:
                await db.execute(
                    "UPDATE user_economy SET bank = ? WHERE user_id = ? AND guild_id = ?",
                    (bank, user_id, guild_id)
                )
            
            await db.commit()
    
    # Leveling methods. For managing user leveling data.
    # Methods include getting and updating user XP and levels.
    async def get_user_level_data(self, user_id, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT xp, level FROM user_levels WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            result = await cursor.fetchone()
            return result if result else (0, 1)
    
    async def update_user_xp(self, user_id, guild_id, xp, level):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO user_levels (user_id, guild_id, xp, level) VALUES (?, ?, ?, ?)",
                (user_id, guild_id, xp, level)
            )
            await db.commit()
    
    # Moderation logs. For recording moderation actions.
    # Methods include adding a new moderation log entry.
    async def add_mod_log(self, guild_id, user_id, moderator_id, action, reason, timestamp):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO mod_logs (guild_id, user_id, moderator_id, action, reason, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (guild_id, user_id, moderator_id, action, reason, timestamp)
            )
            await db.commit()