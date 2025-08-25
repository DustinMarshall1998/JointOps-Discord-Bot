import discord
from discord.ext import commands
import aiohttp
import asyncio
from datetime import datetime
import os

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        if self.session:
            asyncio.create_task(self.session.close())
    
    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        """Get information about a user"""
        user = member or ctx.author
        
        embed = discord.Embed(
            title=f"👤 {user.display_name}",
            color=user.color if user.color.value != 0 else discord.Color.blue()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        
        embed.add_field(name="Username", value=str(user), inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Status", value=str(user.status).title(), inline=True)
        
        embed.add_field(name="Account Created", value=user.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%B %d, %Y") if user.joined_at else "N/A", inline=True)
        embed.add_field(name="Roles", value=f"{len(user.roles) - 1}", inline=True)
        
        if user.premium_since:
            embed.add_field(name="Boosting Since", value=user.premium_since.strftime("%B %d, %Y"), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def serverinfo(self, ctx):
        """Get information about the server"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"🏰 {guild.name}",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        
        embed.add_field(name="Verification Level", value=str(guild.verification_level).title(), inline=True)
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
        
        if guild.description:
            embed.add_field(name="Description", value=guild.description, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        """Get a user's avatar"""
        user = member or ctx.author
        
        embed = discord.Embed(
            title=f"🖼️ {user.display_name}'s Avatar",
            color=discord.Color.blue()
        )
        
        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        embed.set_image(url=avatar_url)
        embed.add_field(name="Direct Link", value=f"[Click Here]({avatar_url})", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def weather(self, ctx, *, city=None):
        """Get weather information for a city"""
        if not city:
            await ctx.send("❌ Please specify a city!")
            return
        
        api_key = os.getenv('WEATHER_API_KEY')
        if not api_key:
            await ctx.send("❌ Weather service is not configured!")
            return
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    embed = discord.Embed(
                        title=f"🌤️ Weather in {data['name']}, {data['sys']['country']}",
                        color=discord.Color.blue()
                    )
                    
                    embed.add_field(name="Temperature", value=f"{data['main']['temp']:.1f}°C", inline=True)
                    embed.add_field(name="Feels Like", value=f"{data['main']['feels_like']:.1f}°C", inline=True)
                    embed.add_field(name="Humidity", value=f"{data['main']['humidity']}%", inline=True)
                    
                    embed.add_field(name="Description", value=data['weather'][0]['description'].title(), inline=True)
                    embed.add_field(name="Wind Speed", value=f"{data['wind']['speed']} m/s", inline=True)
                    embed.add_field(name="Pressure", value=f"{data['main']['pressure']} hPa", inline=True)
                    
                    await ctx.send(embed=embed)
                elif resp.status == 404:
                    await ctx.send("❌ City not found!")
                else:
                    await ctx.send("❌ Weather service is currently unavailable!")
        except Exception as e:
            await ctx.send("❌ An error occurred while fetching weather data!")
    
    @commands.command()
    async def calculate(self, ctx, *, expression):
        """Calculate a mathematical expression"""
        try:
            # Safe evaluation - only allow basic math
            allowed_chars = set('0123456789+-*/(). ')
            if not all(c in allowed_chars for c in expression):
                await ctx.send("❌ Invalid characters in expression!")
                return
            
            # Replace some common math terms
            expression = expression.replace('^', '**')
            expression = expression.replace('x', '*')
            
            result = eval(expression)
            
            embed = discord.Embed(
                title="🧮 Calculator",
                color=discord.Color.green()
            )
            embed.add_field(name="Expression", value=f"```{expression}```", inline=False)
            embed.add_field(name="Result", value=f"```{result}```", inline=False)
            
            await ctx.send(embed=embed)
            
        except ZeroDivisionError:
            await ctx.send("❌ Division by zero!")
        except Exception as e:
            await ctx.send("❌ Invalid mathematical expression!")
    
    @commands.command()
    async def poll(self, ctx, question, *options):
        """Create a poll with reactions"""
        if len(options) < 2:
            await ctx.send("❌ Please provide at least 2 options!")
            return
        
        if len(options) > 10:
            await ctx.send("❌ Maximum 10 options allowed!")
            return
        
        # Number emojis for reactions
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        embed = discord.Embed(
            title="📊 Poll",
            description=f"**{question}**",
            color=discord.Color.blue()
        )
        
        for i, option in enumerate(options):
            embed.add_field(name=f"{emojis[i]} Option {i+1}", value=option, inline=False)
        
        embed.set_footer(text=f"Poll created by {ctx.author.display_name}")
        
        poll_msg = await ctx.send(embed=embed)
        
        # Add reactions
        for i in range(len(options)):
            await poll_msg.add_reaction(emojis[i])
    
    @commands.command()
    async def remind(self, ctx, time: int, *, reminder):
        """Set a reminder (time in minutes)"""
        if time <= 0 or time > 1440:  # Max 24 hours
            await ctx.send("❌ Time must be between 1 and 1440 minutes (24 hours)!")
            return
        
        embed = discord.Embed(
            title="⏰ Reminder Set!",
            description=f"I'll remind you about: **{reminder}**\nIn {time} minute(s)",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
        # Wait for the specified time
        await asyncio.sleep(time * 60)
        
        # Send reminder
        remind_embed = discord.Embed(
            title="🔔 Reminder!",
            description=f"You asked me to remind you about: **{reminder}**",
            color=discord.Color.orange()
        )
        await ctx.send(f"{ctx.author.mention}", embed=remind_embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))