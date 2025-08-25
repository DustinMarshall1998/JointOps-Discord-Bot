import discord
from discord.ext import commands
import random
import aiohttp
import json

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        if self.session:
            asyncio.create_task(self.session.close())
    
    @commands.command()
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: {latency}ms",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def roll(self, ctx, sides: int = 6):
        """Roll a dice with specified sides"""
        if sides < 2:
            await ctx.send("❌ Dice must have at least 2 sides!")
            return
        
        if sides > 100:
            await ctx.send("❌ Maximum 100 sides allowed!")
            return
        
        result = random.randint(1, sides)
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"You rolled a **{result}** on a {sides}-sided dice!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def coinflip(self, ctx):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])
        emoji = "🪙" if result == "Heads" else "🥇"
        
        embed = discord.Embed(
            title=f"{emoji} Coin Flip",
            description=f"The coin landed on **{result}**!",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def joke(self, ctx):
        """Get a random joke"""
        try:
            async with self.session.get('https://official-joke-api.appspot.com/random_joke') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(
                        title="😂 Random Joke",
                        description=f"**{data['setup']}**\n\n{data['punchline']}",
                        color=discord.Color.purple()
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Couldn't fetch a joke right now!")
        except:
            # Fallback jokes
            jokes = [
                ("Why don't scientists trust atoms?", "Because they make up everything!"),
                ("What do you call a fake noodle?", "An impasta!"),
                ("Why did the scarecrow win an award?", "He was outstanding in his field!"),
                ("What do you call a bear with no teeth?", "A gummy bear!"),
                ("Why don't eggs tell jokes?", "They'd crack each other up!")
            ]
            setup, punchline = random.choice(jokes)
            embed = discord.Embed(
                title="😂 Random Joke",
                description=f"**{setup}**\n\n{punchline}",
                color=discord.Color.purple()
            )
            await ctx.send(embed=embed)
    
    @commands.command()
    async def quote(self, ctx):
        """Get an inspirational quote"""
        try:
            async with self.session.get('https://api.quotable.io/random') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(
                        title="💭 Inspirational Quote",
                        description=f'"{data["content"]}"',
                        color=discord.Color.teal()
                    )
                    embed.set_footer(text=f"— {data['author']}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Couldn't fetch a quote right now!")
        except:
            quotes = [
                ("The only way to do great work is to love what you do.", "Steve Jobs"),
                ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
                ("Life is what happens to you while you're busy making other plans.", "John Lennon"),
                ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt")
            ]
            quote, author = random.choice(quotes)
            embed = discord.Embed(
                title="💭 Inspirational Quote",
                description=f'"{quote}"',
                color=discord.Color.teal()
            )
            embed.set_footer(text=f"— {author}")
            await ctx.send(embed=embed)
    
    @commands.command()
    async def rps(self, ctx, choice: str = None):
        """Play Rock Paper Scissors"""
        if not choice:
            await ctx.send("❌ Please choose rock, paper, or scissors!")
            return
        
        choice = choice.lower()
        if choice not in ['rock', 'paper', 'scissors']:
            await ctx.send("❌ Invalid choice! Choose rock, paper, or scissors.")
            return
        
        bot_choice = random.choice(['rock', 'paper', 'scissors'])
        
        # Determine winner
        if choice == bot_choice:
            result = "It's a tie!"
            color = discord.Color.yellow()
        elif (choice == 'rock' and bot_choice == 'scissors') or \
             (choice == 'paper' and bot_choice == 'rock') or \
             (choice == 'scissors' and bot_choice == 'paper'):
            result = "You win!"
            color = discord.Color.green()
        else:
            result = "I win!"
            color = discord.Color.red()
        
        # Emojis
        emojis = {'rock': '🪨', 'paper': '📄', 'scissors': '✂️'}
        
        embed = discord.Embed(
            title="🎮 Rock Paper Scissors",
            description=f"You chose {emojis[choice]} **{choice.title()}**\nI chose {emojis[bot_choice]} **{bot_choice.title()}**\n\n**{result}**",
            color=color
        )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def magic8ball(self, ctx, *, question=None):
        """Ask the magic 8-ball a question"""
        if not question:
            await ctx.send("❌ Please ask a question!")
            return
        
        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
        
        answer = random.choice(responses)
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            description=f"**Question:** {question}\n**Answer:** {answer}",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def meme(self, ctx):
        """Get a random meme"""
        try:
            async with self.session.get('https://meme-api.herokuapp.com/gimme') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(
                        title="😂 Random Meme",
                        color=discord.Color.orange()
                    )
                    embed.set_image(url=data['url'])
                    embed.set_footer(text=f"From r/{data['subreddit']} • 👍 {data['ups']}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Couldn't fetch a meme right now!")
        except:
            await ctx.send("❌ Meme service is currently unavailable!")

async def setup(bot):
    await bot.add_cog(Fun(bot))