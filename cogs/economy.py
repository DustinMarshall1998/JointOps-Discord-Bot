## Economy Cog (balance, daily, work, crime, deposit, withdraw, pay)
# Imports (discord.py, commands extension, random, datetime, asyncio)
import discord
from discord.ext import commands
import random
from datetime import datetime, timedelta
import asyncio

## class Economy Cog. For user economy features.
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    ## Command to check balance.
    ## Can check own balance or another member's balance.
    ## Displays wallet, bank, and total balance in an embed.
    ## If no member is specified, defaults to the command invoker.
    @commands.cooldown(1, 5, commands.BucketType.user)  # 5 second cooldown
    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        """Check your or someone else's balance"""
        user = member or ctx.author
        balance, bank = await self.bot.db.get_user_balance(user.id, ctx.guild.id)
        
        embed = discord.Embed(
            title=f"💰 {user.display_name}'s Balance",
            color=discord.Color.green()
        )
        embed.add_field(name="💵 Wallet", value=f"${balance:,}", inline=True)
        embed.add_field(name="🏦 Bank", value=f"${bank:,}", inline=True)
        embed.add_field(name="💎 Total", value=f"${balance + bank:,}", inline=True)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        
        await ctx.send(embed=embed)
    
    ## Command to claim daily reward.
    ## Users can claim a set amount of money once every 24 hours.
    ## Displays the amount received and new balance in an embed.
    ## Implements a cooldown to enforce the 24-hour limit.
    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)  # 24 hour cooldown
    async def daily(self, ctx):
        """Claim your daily reward"""
        reward = self.bot.config['features']['economy']['daily_reward']
        balance, bank = await self.bot.db.get_user_balance(ctx.author.id, ctx.guild.id)
        
        new_balance = balance + reward
        await self.bot.db.update_user_balance(ctx.author.id, ctx.guild.id, balance=new_balance)
        
        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=f"You received **${reward:,}**!\nYour new balance is **${new_balance:,}**",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
    
    ## Command to work and earn money.
    ## Users can work once every hour to earn a random amount of money.
    ## The job type is randomly selected from a predefined list.
    ## Displays the job, amount earned, and new balance in an embed.
    ## Implements a cooldown to enforce the 1-hour limit.
    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)  # 1 hour cooldown
    async def work(self, ctx):
        """Work to earn money"""
        jobs = [
            "programming", "designing", "writing", "streaming", "gaming",
            "coding", "teaching", "cooking", "cleaning", "driving"
        ]
        
        job = random.choice(jobs)
        work_min = self.bot.config['features']['economy']['work_min']
        work_max = self.bot.config['features']['economy']['work_max']
        earnings = random.randint(work_min, work_max)
        
        balance, bank = await self.bot.db.get_user_balance(ctx.author.id, ctx.guild.id)
        new_balance = balance + earnings
        await self.bot.db.update_user_balance(ctx.author.id, ctx.guild.id, balance=new_balance)
        
        embed = discord.Embed(
            title="💼 Work Complete!",
            description=f"You worked as a **{job}** and earned **${earnings:,}**!\nYour new balance is **${new_balance:,}**",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    ## Command to attempt a crime for money.
    ## Users can attempt a crime once every 2 hours to earn a random amount of money.
    ## There is a chance of failure, resulting in a fine instead of earnings.
    ## Displays the crime outcome, amount earned or fined, and new balance in an embed.
    ## Implements a cooldown to enforce the 2-hour limit.
    @commands.command()
    @commands.cooldown(1, 7200, commands.BucketType.user)  # 2 hour cooldown
    async def crime(self, ctx):
        """Attempt a crime (risky!)"""
        crimes = [
            "robbing a bank", "hacking a computer", "stealing a car",
            "pickpocketing", "burglary", "identity theft"
        ]
        
        crime = random.choice(crimes)
        crime_min = self.bot.config['features']['economy']['crime_min']
        crime_max = self.bot.config['features']['economy']['crime_max']
        fail_rate = self.bot.config['features']['economy']['crime_fail_rate']
        
        balance, bank = await self.bot.db.get_user_balance(ctx.author.id, ctx.guild.id)
        
        if random.random() < fail_rate:  # Crime failed
            fine = random.randint(50, 200)
            new_balance = max(0, balance - fine)
            await self.bot.db.update_user_balance(ctx.author.id, ctx.guild.id, balance=new_balance)
            
            embed = discord.Embed(
                title="🚨 Crime Failed!",
                description=f"You got caught {crime} and paid a fine of **${fine:,}**!\nYour new balance is **${new_balance:,}**",
                color=discord.Color.red()
            )
        else:  # Crime succeeded
            earnings = random.randint(crime_min, crime_max)
            new_balance = balance + earnings
            await self.bot.db.update_user_balance(ctx.author.id, ctx.guild.id, balance=new_balance)
            
            embed = discord.Embed(
                title="😈 Crime Successful!",
                description=f"You successfully completed {crime} and earned **${earnings:,}**!\nYour new balance is **${new_balance:,}**",
                color=discord.Color.dark_green()
            )
        
        await ctx.send(embed=embed)
    
    ## Command to deposit money into the bank.
    ## Users can deposit a specified amount or 'all' of their wallet balance.
    ## Displays the amount deposited and new balances in an embed.
    ## Validates input to ensure positive amounts and sufficient wallet balance.
    @commands.command()
    async def deposit(self, ctx, amount: str):
        """Deposit money into your bank"""
        balance, bank = await self.bot.db.get_user_balance(ctx.author.id, ctx.guild.id)
        
        if amount.lower() == 'all':
            amount = balance
        else:
            try:
                amount = int(amount)
            except ValueError:
                await ctx.send("❌ Please enter a valid amount or 'all'!")
                return
        
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        
        if amount > balance:
            await ctx.send("❌ You don't have enough money in your wallet!")
            return
        
        new_balance = balance - amount
        new_bank = bank + amount
        
        await self.bot.db.update_user_balance(ctx.author.id, ctx.guild.id, balance=new_balance, bank=new_bank)
        
        embed = discord.Embed(
            title="🏦 Deposit Successful!",
            description=f"Deposited **${amount:,}** into your bank!\n💵 Wallet: **${new_balance:,}**\n🏦 Bank: **${new_bank:,}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    ## Command to withdraw money from the bank.
    ## Users can withdraw a specified amount or 'all' of their bank balance.
    ## Displays the amount withdrawn and new balances in an embed.
    ## Validates input to ensure positive amounts and sufficient bank balance.
    @commands.command()
    async def withdraw(self, ctx, amount: str):
        """Withdraw money from your bank"""
        balance, bank = await self.bot.db.get_user_balance(ctx.author.id, ctx.guild.id)
        
        if amount.lower() == 'all':
            amount = bank
        else:
            try:
                amount = int(amount)
            except ValueError:
                await ctx.send("❌ Please enter a valid amount or 'all'!")
                return
        
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        
        if amount > bank:
            await ctx.send("❌ You don't have enough money in your bank!")
            return
        
        new_balance = balance + amount
        new_bank = bank - amount
        
        await self.bot.db.update_user_balance(ctx.author.id, ctx.guild.id, balance=new_balance, bank=new_bank)
        
        embed = discord.Embed(
            title="🏦 Withdrawal Successful!",
            description=f"Withdrew **${amount:,}** from your bank!\n💵 Wallet: **${new_balance:,}**\n🏦 Bank: **${new_bank:,}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    ## Command to pay another user.
    ## Users can transfer a specified amount of money to another member.
    ## Validates input to ensure positive amounts, sufficient balance, and prevents paying bots or oneself.
    ## Displays the payment details in an embed.
    @commands.command()
    async def pay(self, ctx, member: discord.Member, amount: int):
        """Pay another user"""
        if member.bot:
            await ctx.send("❌ You can't pay bots!")
            return
        
        if member == ctx.author:
            await ctx.send("❌ You can't pay yourself!")
            return
        
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        
        sender_balance, sender_bank = await self.bot.db.get_user_balance(ctx.author.id, ctx.guild.id)
        
        if amount > sender_balance:
            await ctx.send("❌ You don't have enough money!")
            return
        
        receiver_balance, receiver_bank = await self.bot.db.get_user_balance(member.id, ctx.guild.id)
        
        # Update balances
        await self.bot.db.update_user_balance(ctx.author.id, ctx.guild.id, balance=sender_balance - amount)
        await self.bot.db.update_user_balance(member.id, ctx.guild.id, balance=receiver_balance + amount)
        
        embed = discord.Embed(
            title="💸 Payment Successful!",
            description=f"{ctx.author.mention} paid **${amount:,}** to {member.mention}!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

## Setup function to add the Economy cog to the bot
async def setup(bot):
    await bot.add_cog(Economy(bot))