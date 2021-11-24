# ---       IMPORTS         --- #
import discord

from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from pybo import BOT_AVATAR, guild_ids


# ---     CUSTOM CHECKS     --- #
def bot_channel_check(ctx):
    botspam_channels = ['bot-spam', 'bot-commands']
    if str(ctx.message.channel) in botspam_channels or ctx.author.id == 291005201840734218:
        return True


# ---       MAIN LINE       --- #
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---       SLASH COMMANDS       --- #
    @cog_ext.cog_slash(
        name='help',
        description='Detailed list of bot commands!',
        guild_ids=guild_ids,
        options=[
            create_option(
                name='module',
                description='Choose category!',
                required=True,
                option_type=3,
                choices=[
                    create_choice(
                        name='Administration',
                        value='admin'
                    ),
                    create_choice(
                        name='Info',
                        value='info'
                    ),
                    create_choice(
                        name='Market',
                        value='market'
                    )
                ]
            )
        ]
    )
    async def _help(self, ctx: SlashContext, module: str):
        if module == 'admin':
            embed = discord.Embed(
                title='Administration',
                description=' ',
                colour=discord.Colour.blurple()
            )
            embed.set_author(name='Commands List', icon_url=BOT_AVATAR)
            embed.add_field(name=';prune __Amount__',
                            value='Removes the amount of messages specified',
                            inline=False)
            embed.add_field(name=';mute __@user / user ID__',
                            value='Mutes the specified user',
                            inline=False)
            embed.add_field(name=';unmute __@user / user ID__',
                            value='Unmutes the specified user',
                            inline=False)
            embed.set_footer(text='User IDs can be found by turning on "Developer Mode"')
        elif module == 'info':
            embed = discord.Embed(
                title='Info',
                description=' ',
                colour=discord.Colour.blurple()
            )
            embed.set_author(name='Commands List', icon_url=BOT_AVATAR)
            embed.add_field(name=';ping', value='pong!',
                            inline=False)
        elif module == 'market':
            embed = discord.Embed(
                title='Market',
                description=' ',
                colour=discord.Colour.blurple()
            )
            embed.set_author(name='Commands List', icon_url=BOT_AVATAR)
            embed.add_field(name=';coin __1-100__ or ;coin __name__',
                            value='Displays Name / Current Price',
                            inline=False)
            embed.add_field(name=';top __1-100__',
                            value='Displays the top # coins',
                            inline=False)
        await ctx.send(embeds=[embed])

    # ---       PREFIX COMMANDS       --- #
    # @commands.command()
    # @commands.check(bot_channel_check)
    # async def help(self, ctx, module=None):
    #     if module is None:
    #         embed = discord.Embed(
    #             title='Use *;help* __*Module Name*__ to get more info',
    #             description='• Administration\n'
    #                         '• Info\n'
    #                         '• Market\n',
    #             colour=discord.Colour.blurple()
    #         )
    #         embed.set_author(name='Commands List',
    #                          icon_url=BOT_AVATAR)
    #         await ctx.send(embed=embed)
    #     elif module == 'Administration' or module == 'administration' or module == 'Admin' or module == 'admin':
    #         embed = discord.Embed(
    #             title='Administration',
    #             description=' ',
    #             colour=discord.Colour.blurple()
    #         )
    #         embed.set_author(name='Commands List', icon_url=BOT_AVATAR)
    #         embed.add_field(name=';prune __Amount__',
    #                         value='Removes the amount of messages specified',
    #                         inline=False)
    #         embed.add_field(name=';mute __@user / user ID__',
    #                         value='Mutes the specified user',
    #                         inline=False)
    #         embed.add_field(name=';unmute __@user / user ID__',
    #                         value='Unmutes the specified user',
    #                         inline=False)
    #         embed.set_footer(text='User IDs can be found by turning on "Developer Mode"')
    #
    #         await ctx.send(embed=embed)
    #     elif module == 'Info' or module == 'info':
    #         embed = discord.Embed(
    #             title='Info',
    #             description=' ',
    #             colour=discord.Colour.blurple()
    #         )
    #         embed.set_author(name='Commands List', icon_url=BOT_AVATAR)
    #         embed.add_field(name=';ping', value='pong!',
    #                         inline=False)
    #         await ctx.send(embed=embed)
    #     elif module == 'Market' or module == 'market':
    #         embed = discord.Embed(
    #             title='Market',
    #             description=' ',
    #             colour=discord.Colour.blurple()
    #         )
    #         embed.set_author(name='Commands List', icon_url=BOT_AVATAR)
    #         embed.add_field(name=';coin __1-100__ or ;coin __name__',
    #                         value='Displays Name / Current Price',
    #                         inline=False)
    #         embed.add_field(name=';top __1-100__',
    #                         value='Displays the top # coins',
    #                         inline=False)
    #
    #         await ctx.send(embed=embed)
    #     else:
    #         embed = discord.Embed(
    #             title='Invalid Command',
    #             description=' ',
    #             colour=discord.Colour.red()
    #         )
    #         await ctx.send(embed=embed)


# ---       END MAIN            ---#
def setup(bot):
    bot.add_cog(Help(bot))
