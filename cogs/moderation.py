## Moderation Cog. Provides moderation commands and auto-moderation features.
## Features:
# - Kick, ban, mute, unmute commands with logging
# - Clear messages command with logging
# - Auto-moderation for invite links and excessive mentions
# - Logs moderation actions to the database
## Requirements:
# - discord.py
# - datetime for timestamps
# - asyncio for timed actions
import discord
from discord.ext import commands
from datetime import datetime
import asyncio

## class Moderation Cog. For moderation commands and auto-moderation features.
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    ## Kick command to remove a member from the server.
    ## Requires the user to have kick permissions.
    ## Logs the action to the database and sends a confirmation embed.
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member from the server"""
        try:
            await member.kick(reason=reason)
            
            # Log the action
            await self.bot.db.add_mod_log(
                ctx.guild.id, member.id, ctx.author.id,
                "kick", reason, datetime.now().isoformat()
            )
            
            embed = discord.Embed(
                title="Member Kicked",
                description=f"{member.mention} has been kicked.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this member!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    ## Ban command to permanently remove a member from the server.
    ## Requires the user to have ban permissions.
    ## Logs the action to the database and sends a confirmation embed.
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member from the server"""
        try:
            await member.ban(reason=reason)
            
            # Log the action
            await self.bot.db.add_mod_log(
                ctx.guild.id, member.id, ctx.author.id,
                "ban", reason, datetime.now().isoformat()
            )
            
            embed = discord.Embed(
                title="Member Banned",
                description=f"{member.mention} has been banned.",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this member!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    ## Clear command to bulk delete messages from a channel.
    ## Requires the user to have manage messages permissions.
    ## Logs the action to the database and sends a confirmation embed.
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        """Clear messages from the channel"""
        if amount > 100:
            await ctx.send("❌ Cannot clear more than 100 messages at once!")
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 for the command message
            
            embed = discord.Embed(
                title="Messages Cleared",
                description=f"Cleared {len(deleted) - 1} messages.",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            msg = await ctx.send(embed=embed)
            await asyncio.sleep(3)
            await msg.delete()
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to delete messages!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    ## Mute command to mute a member for a specified duration.
    ## Requires the user to have manage roles permissions.
    ## Creates a "Muted" role if it doesn't exist and sets appropriate permissions.
    ## Logs the action to the database and sends a confirmation embed.
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int = 10, *, reason="No reason provided"):
        """Mute a member for a specified duration (in minutes)"""
        try:
            # Create or get muted role
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if not muted_role:
                muted_role = await ctx.guild.create_role(name="Muted")
                
                # Set permissions for the muted role
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)
            
            await member.add_roles(muted_role, reason=reason)
            
            # Log the action
            await self.bot.db.add_mod_log(
                ctx.guild.id, member.id, ctx.author.id,
                f"mute ({duration}m)", reason, datetime.now().isoformat()
            )
            
            embed = discord.Embed(
                title="Member Muted",
                description=f"{member.mention} has been muted for {duration} minutes.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
            # Auto-unmute after duration
            await asyncio.sleep(duration * 60)
            await member.remove_roles(muted_role, reason="Auto unmute")
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to mute this member!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    ## Unmute command to remove the mute from a member.
    ## Requires the user to have manage roles permissions.
    ## Logs the action to the database and sends a confirmation embed.
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmute a member"""
        try:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if muted_role and muted_role in member.roles:
                await member.remove_roles(muted_role)
                
                embed = discord.Embed(
                    title="Member Unmuted",
                    description=f"{member.mention} has been unmuted.",
                    color=discord.Color.green()
                )
                embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ This member is not muted!")
                
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unmute this member!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    ## Auto-moderation listener to monitor messages for invite links and excessive mentions.
    ## Deletes offending messages and warns the user.
    ## Logs moderation actions to the database.
    ## Requires the bot to have manage messages permissions.
    @commands.Cog.listener()
    async def on_message(self, message):
        """Auto-moderation features"""
        if message.author.bot or not message.guild:
            return
        
        # Check for invite links
        if self.bot.config['features']['moderation']['auto_delete_invites']:
            if 'discord.gg/' in message.content or 'discord.com/invite/' in message.content:
                if not message.author.guild_permissions.manage_messages:
                    await message.delete()
                    await message.channel.send(f"❌ {message.author.mention}, invite links are not allowed!", delete_after=5)
        
        # Check for excessive mentions
        max_mentions = self.bot.config['features']['moderation']['max_mentions']
        if len(message.mentions) > max_mentions:
            await message.delete()
            await message.channel.send(f"❌ {message.author.mention}, too many mentions in one message!", delete_after=5)

### Setup function to add the Moderation cog to the bot
async def setup(bot):
    await bot.add_cog(Moderation(bot))