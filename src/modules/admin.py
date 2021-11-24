# ---       IMPORTS          ---#
import discord
from discord.ext import commands


# ---       MAIN LINE       ---#
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    # '*' allow admins to send full length messages, ignoring the spaces
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        await user.kick(reason=reason)
        embed = discord.Embed(
            title=f'Kicked {user}',
            description=' ',
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed, delete_after=10)

        audit_channel = self.bot.get_channel(772860738796650537)
        embed2 = discord.Embed(
            title=f'Kicked {user}',
            description=' ',
            colour=discord.Colour.red()
        )
        embed2.set_footer(text=f'Reason: {reason}')
        embed2.set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar_url
        )
        await audit_channel.send(embed=embed2)

    # Allow banning via @User
    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        await user.ban(reason=reason)
        embed = discord.Embed(
            title=f'Banned {user}',
            description=' ',
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed, delete_after=10)

        audit_channel = self.bot.get_channel(772860738796650537)
        embed2 = discord.Embed(
            title=f'Banned {user}',
            description=' ',
            colour=discord.Colour.red()
        )
        embed2.set_footer(text=f'Reason: {reason}')
        embed2.set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar_url
        )
        await audit_channel.send(embed=embed2)

    # Allow banning via UserID
    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def idban(self, ctx, userid, *, reason=None):
        user = discord.Object(id=userid)
        username = ctx.get_user(userid)
        await ctx.guild.ban(user, reason=reason)
        embed = discord.Embed(
            title=f'Banned {userid}, {username}',
            description=' ',
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed, delete_after=10)

        audit_channel = self.bot.get_channel(772860738796650537)
        embed2 = discord.Embed(
            title=f'Banned {user}',
            description=' ',
            colour=discord.Colour.blurple()
        )
        embed2.set_footer(text=f'Reason: {reason}')
        embed2.set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar_url
        )
        await audit_channel.send(embed=embed2)

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, userid, *, reason=None):
        user = discord.Object(id=userid)
        await ctx.guild.unban(user, reason=reason)
        embed = discord.Embed(
            title=f'Unbanned {userid}',
            description=' ',
            colour=discord.Colour.green()
        )
        await ctx.send(embed=embed, delete_after=10)

        audit_channel = self.bot.get_channel(772860738796650537)
        embed2 = discord.Embed(
            title=f'Unbanned {user}',
            description=' ',
            colour=discord.Colour.green()
        )
        embed2.set_footer(text=f'Reason: {reason}')
        embed2.set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar_url
        )
        await audit_channel.send(embed=embed2)

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def prune(self, ctx, amount=5):
        if int(amount) > 0:
            audit_channel = self.bot.get_channel(772860738796650537)
            if int(amount) == 1:
                # Send embed in channel where command was called
                await ctx.channel.purge(limit=int(amount) + 1) # Shifted +1 to account for command call
                embed = discord.Embed(
                    title=f'Successfully removed {amount} message',
                    description=' ',
                    colour=discord.Colour.blurple()
                )
                await ctx.send(embed=embed, delete_after=2)
                # Send embed to audit channel
                embed2 = discord.Embed(
                    title=f'Successfully removed {amount} message in #{ctx.channel}',
                    description=' ',
                    colour=discord.Colour.red()
                )
                embed2.set_author(
                    name=ctx.author,
                    icon_url=ctx.author.avatar_url
                )
                await audit_channel.send(embed=embed2)
            else:
                # Send embed in channel where command was called
                await ctx.channel.purge(limit=int(amount) + 1) # Shifted +1 to account for command call
                embed = discord.Embed(
                    title=f'Successfully removed {amount} messages',
                    description=' ',
                    colour=discord.Colour.blurple()
                )
                await ctx.send(embed=embed, delete_after=2)
                # Send embed to audit channel
                embed2 = discord.Embed(
                    title=f'Successfully removed {amount} messages in #{ctx.channel}',
                    description=' ',
                    colour=discord.Colour.red()
                )
                embed2.set_author(
                    name=ctx.author,
                    icon_url=ctx.author.avatar_url
                )
                await audit_channel.send(embed=embed2)
        elif int(amount) <= 0:
            embed = discord.Embed(
                title='Error: The amount must be greater than 0',
                description=' ',
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed, delete_after=5)

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    async def mute(self, ctx, user: discord.Member, *, reason=None):
        mute_role = discord.utils.get(ctx.guild.roles, name='Mute')
        await user.add_roles(mute_role, reason=reason)
        embed = discord.Embed(
            title=f'Muted {user}',
            description=' ',
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed, delete_after=5)

        audit_channel = self.bot.get_channel(772860738796650537)
        embed2 = discord.Embed(
            title=f'Muted {user}',
            description=' ',
            colour=discord.Colour.red()
        )
        embed2.set_footer(text=f'Reason: {reason}')
        embed2.set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar_url
        )
        await audit_channel.send(embed=embed2)

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    async def unmute(self, ctx, user: discord.Member):
        mute_role = discord.utils.get(ctx.guild.roles, name='Mute')
        await user.remove_roles(mute_role)
        embed = discord.Embed(
            title=f'Unmuted {user}',
            description=' ',
            colour=discord.Colour.green()
        )
        await ctx.send(embed=embed, delete_after=5)

        audit_channel = self.bot.get_channel(772860738796650537)
        embed2 = discord.Embed(
            title=f'Unmuted {user}',
            description=' ',
            colour=discord.Colour.green()
        )
        embed2.set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar_url
        )
        await audit_channel.send(embed=embed2)

    # ---       ERROR HANDLING       ---#
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title='Error: Specify user to kick',
                description=' ',
                colour=discord.Colour.red()
            )
            embed.set_footer(text='ex => ;kick UserID / @User')
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title='Error: You are not allowed to manage users',
                description=' ',
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed, delete_after=5)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title='Error: Specify user ID to ban',
                description=' ',
                colour=discord.Colour.red()
            )
            embed.set_footer(text='ex => ;ban UserID / @User')
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title='Error: You are not allowed to manage users',
                description=' ',
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed, delete_after=5)

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title='Error: Specify user ID to unban',
                description=' ',
                colour=discord.Colour.red()
            )
            embed.set_footer(text='ex => ;unban UserID / @User')
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title='Error: You are not allowed to manage users',
                description=' ',
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed, delete_after=5)

    @prune.error
    async def prune_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title='Error: Specify amount of messages to be deleted',
                description=' ',
                colour=discord.Colour.red()
            )
            embed.set_footer(text='ex => ;prune 10')
            await ctx.send(embed=embed, delete_after=5)

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title='Error: You are not able to manage roles',
                description=' ',
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title='Error: Specify user',
                description=' ',
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed, delete_after=5)

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title='Error: You are not able to manage roles',
                description=' ',
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title='Error: Specify user',
                description=' ',
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed, delete_after=5)


# ---       END MAIN        ---#
def setup(bot):
    bot.add_cog(Admin(bot))
