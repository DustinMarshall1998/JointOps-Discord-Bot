import sqlite3
import aiosqlite
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path="bot_database.db"):
        self.db_path = db_path
    
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
    
    # Guild settings methods
    async def get_guild_prefix(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT prefix FROM guild_settings WHERE guild_id = ?",
                (guild_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else None
    
    async def set_guild_prefix(self, guild_id, prefix):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO guild_settings (guild_id, prefix) VALUES (?, ?)",
                (guild_id, prefix)
            )
            await db.commit()
    
    async def add_guild(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)",
                (guild_id,)
            )
            await db.commit()
    
    # Economy methods
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
    
    # Leveling methods
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
    
    # Moderation logs
    async def add_mod_log(self, guild_id, user_id, moderator_id, action, reason, timestamp):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO mod_logs (guild_id, user_id, moderator_id, action, reason, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (guild_id, user_id, moderator_id, action, reason, timestamp)
            )
            await db.commit()