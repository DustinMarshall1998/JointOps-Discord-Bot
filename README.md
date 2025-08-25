# JointOps Discord Bot

A comprehensive, highly customizable Discord bot with multiple features including moderation, economy, leveling, music, and more!

## 🌟 Features

### 🛡️ Moderation
- Kick, ban, mute/unmute members
- Clear messages
- Auto-moderation (invite links, spam detection)
- Moderation logging

### 💰 Economy System
- Virtual currency system
- Daily rewards, work, and crime commands
- Bank system with deposit/withdraw
- User-to-user payments

### 📊 Leveling System
- XP and level tracking
- Level-up announcements
- Progress tracking with visual progress bars

### 🎮 Fun Commands
- Games (rock-paper-scissors, dice roll, coin flip)
- Jokes, quotes, and memes
- Magic 8-ball
- Random number generation

### 🔧 Utility Tools
- User and server information
- Avatar display
- Weather information
- Calculator
- Polls and reminders

### 🎵 Music Player
- Voice channel integration
- Queue system
- Basic playback controls
- Volume adjustment

### ⚙️ Admin Features
- Custom prefix per server
- Cog management (load/unload/reload)
- Server settings
- Bot owner commands

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/allinone-discord-bot.git
   cd allinone-discord-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your Discord bot token and other API keys:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   WEATHER_API_KEY=your_openweathermap_api_key
   YOUTUBE_API_KEY=your_youtube_api_key
   BOT_PREFIX=!
   OWNER_ID=your_discord_user_id
   ```

4. **Configure the bot:**
   - Edit `config.json` to customize bot settings
   - Adjust economy values, XP rates, and other features

5. **Run the bot:**
   ```bash
   python main.py
   ```

## 🔧 Configuration

### Bot Settings (`config.json`)
```json
{
  "bot": {
    "name": "AllInOne Bot",
    "description": "A comprehensive Discord bot",
    "version": "1.0.0",
    "color": "#7289DA"
  },
  "features": {
    "economy": {
      "daily_reward": 100,
      "work_min": 50,
      "work_max": 200
    },
    "leveling": {
      "xp_per_message": 15,
      "xp_cooldown": 60
    }
  }
}
```

### Environment Variables
- `DISCORD_TOKEN`: Your Discord bot token
- `WEATHER_API_KEY`: OpenWeatherMap API key (optional)
- `YOUTUBE_API_KEY`: YouTube API key for music features (optional)
- `BOT_PREFIX`: Default command prefix
- `OWNER_ID`: Your Discord user ID for owner commands

## 📚 Commands

### Moderation Commands
- `!kick @user [reason]` - Kick a member
- `!ban @user [reason]` - Ban a member
- `!mute @user [duration] [reason]` - Mute a member
- `!unmute @user` - Unmute a member
- `!clear [amount]` - Clear messages

### Economy Commands
- `!balance [@user]` - Check balance
- `!daily` - Claim daily reward
- `!work` - Work for money
- `!crime` - Attempt a crime (risky)
- `!deposit <amount>` - Deposit money to bank
- `!withdraw <amount>` - Withdraw money from bank
- `!pay @user <amount>` - Pay another user

### Fun Commands
- `!ping` - Check bot latency
- `!roll [sides]` - Roll a dice
- `!coinflip` - Flip a coin
- `!joke` - Get a random joke
- `!quote` - Get an inspirational quote
- `!rps <choice>` - Play rock paper scissors
- `!magic8ball <question>` - Ask the magic 8-ball
- `!meme` - Get a random meme

### Utility Commands
- `!userinfo [@user]` - Get user information
- `!serverinfo` - Get server information
- `!avatar [@user]` - Get user's avatar
- `!weather <city>` - Get weather information
- `!calculate <expression>` - Calculate math expressions
- `!poll <question> [options]` - Create a poll
- `!remind <minutes> <reminder>` - Set a reminder

### Admin Commands
- `!setprefix <prefix>` - Set custom server prefix
- `!settings` - View server settings
- `!reload <cog>` - Reload a cog
- `!load <cog>` - Load a cog
- `!unload <cog>` - Unload a cog
- `!shutdown` - Shutdown the bot (owner only)

## 🏗️ Project Structure

```
allinone-discord-bot/
├── main.py                 # Main bot file
├── config.json            # Bot configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── database/
│   └── db_manager.py     # Database management
└── cogs/
    ├── admin.py          # Admin commands
    ├── economy.py        # Economy system
    ├── fun.py            # Fun commands
    ├── help.py           # Help system
    ├── leveling.py       # Level system
    ├── moderation.py     # Moderation commands
    ├── music.py          # Music player
    └── utility.py        # Utility commands
```

## 🔐 Permissions

The bot requires the following permissions:
- Read Messages
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Add Reactions
- Connect (for music)
- Speak (for music)
- Manage Messages (for moderation)
- Kick Members (for moderation)
- Ban Members (for moderation)
- Manage Roles (for muting)

## 📝 Database

The bot uses SQLite for data persistence with the following tables:
- `guild_settings` - Server configurations
- `user_economy` - Economy data per user/guild
- `user_levels` - Leveling data per user/guild
- `mod_logs` - Moderation action logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you need help or have questions:
1. Check the documentation
2. Look through existing issues
3. Create a new issue with details

## 🔄 Updates

The bot is actively maintained with regular updates including:
- New features and commands
- Bug fixes and improvements
- Security updates
- Performance optimizations

---

**Made with ❤️ for Discord communities**