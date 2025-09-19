import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def help(self, ctx, *, command: str = None):
        """Show help information"""
        if command:
            # Show help for specific command
            cmd = self.bot.get_command(command)
            if cmd:
                embed = discord.Embed(
                    title=f"📖 Help: {cmd.name}",
                    description=cmd.help or "A list of commands that can be use to help you understand each command.",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Usage", value=f"`{ctx.prefix}{cmd.name} {cmd.signature}`", inline=False)
                
                if cmd.aliases:
                    embed.add_field(name="Aliases", value=", ".join(f"`{alias}`" for alias in cmd.aliases), inline=False)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Command not found!")
            return
        
        # Show general help
        embed = discord.Embed(
            title="🤖 JointOps Bot - Help",
            description=f"Prefix: `{ctx.prefix}` | Use `{ctx.prefix}help <command>` for detailed info",
            color=discord.Color.blue()
        )
        
        # Moderation commands
        embed.add_field(
            name="🛡️ Moderation",
            value="`kick` `ban` `mute` `unmute` `clear`",
            inline=False
        )
        
        # Fun commands
        embed.add_field(
            name="🎮 Fun",
            value="`ping` `roll` `coinflip` `joke` `quote` `rps` `magic8ball` `meme`",
            inline=False
        )
        
        # Economy commands
        embed.add_field(
            name="💰 Economy",
            value="`balance` `daily` `work` `crime` `deposit` `withdraw` `pay`",
            inline=False
        )
        
        # Leveling commands
        embed.add_field(
            name="📊 Leveling",
            value="`level` `leaderboard`",
            inline=False
        )
        
        # Utility commands
        embed.add_field(
            name="🔧 Utility",
            value="`userinfo` `serverinfo` `avatar` `weather` `calculate` `poll` `remind`",
            inline=False
        )
        
        # Music commands
        embed.add_field(
            name="🎵 Music",
            value="`join` `leave` `play` `queue` `skip` `volume`",
            inline=False
        )
        
        # Admin commands
        embed.add_field(
            name="⚙️ Admin",
            value="`setprefix` `settings` `reload` `load` `unload` `shutdown`",
            inline=False
        )
        
        embed.set_footer(text=f"Bot Version: {self.bot.config['bot']['version']} | Made with ❤️")
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def commands(self, ctx, command: str = None):
        """List all available commands"""
        all_commands = []
        
        for cog_name, cog in self.bot.cogs.items():
            if cog_name == "Help":
                continue
            
            cog_commands = [cmd.name for cmd in cog.get_commands() if not cmd.hidden]
            if cog_commands:
                all_commands.extend(cog_commands)
        
        embed = discord.Embed(
            title="📜 All Commands",
            description=f"Total commands: {len(all_commands)}",
            color=discord.Color.blue()
        )
        
        # Split commands into chunks of 10 for better formatting
        command_chunks = [all_commands[i:i+10] for i in range(0, len(all_commands), 10)]
        
        for i, chunk in enumerate(command_chunks):
            embed.add_field(
                name=f"Commands {i*10+1}-{min((i+1)*10, len(all_commands))}",
                value="`" + "` `".join(chunk) + "`",
                inline=False
            )
        
        await ctx.send(embed=embed)

@commands.command()
async def info(self, ctx):
    """Show bot information"""
    embed = discord.Embed(
        title="🤖 Bot Information",
        color=discord.Color.blue()
    )
        
    embed.add_field(name="Name", value=self.bot.config['bot']['name'], inline=True)
    embed.add_field(name="Version", value=self.bot.config['bot']['version'], inline=True)
    embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        
    embed.add_field(name="Language", value="Python 3.7+", inline=True)
    embed.add_field(name="Library", value="discord.py", inline=True)
    embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
    embed.add_field(
        name="Features",
        value="• Moderation System\n• Economy & Leveling\n• Fun Commands\n• Music Player\n• Utility Tools",
        inline=False
    )
        
    embed.set_footer(text="Made with ❤️ for Discord communities")
        
    await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))