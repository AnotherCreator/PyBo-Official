# ---       IMPORTS          --- #
import asyncio.exceptions
import discord
import json
import os
import psycopg2

from collections.abc import Sequence
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from dotenvy import load_env, read_file
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

# ---       ENV VARIABLES       --- #

# Bot / Bot Owner related
load_env(read_file('../../.env'))
API_KEY = os.environ.get('CMC_API_KEY')
DB_DEV_PW = os.environ.get('DB_DEV_PW')
BOT_AVATAR = os.environ.get('BOT_AVATAR')
# 746153452606062652 = Dev server
# 823595529250275378 = Water sapiens
guild_ids = [746153452606062652, 823595529250275378]

# ---       LINKS        --- #
api_data = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
api_metadata = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'

# ---       LOAD API         --- #
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
}

session = Session()
session.headers.update(headers)

# ---       API PARAMS        --- #
coin_parameters = {  # Retrieves coins listed 1-100
    'start': '1',
    'limit': '100',
    'convert': 'USD',
    'aux': 'cmc_rank'
}

# ---       CONNECT TO DB       --- #
con = psycopg2.connect(
    host='localhost',
    database='pybo_official',
    user='postgres',
    password=DB_DEV_PW
)
cur = con.cursor()


# ---        DATABASE        --- #
def cache_coins():  # Run this once to init db values
    try:
        id_list = []
        coin_response = session.get(api_data, params=coin_parameters)
        coin_data = json.loads(coin_response.text)
        coins = coin_data['data']

        for x in coins:
            id_list.append(x['id'])
            ids = x['id']
            rank = x['cmc_rank']
            name = x['name']
            symbol = x['symbol']
            price = x['quote']['USD']['price']
            daily_change = x['quote']['USD']['percent_change_24h']

            cur.execute("INSERT INTO coin_info"
                        "(coin_id, coin_name, coin_symbol, coin_price, coin_rank, coin_daily_change)"
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (ids, name, symbol, price, rank, daily_change))
            con.commit()  # Commit transaction

        joined_id = ','.join(map(str, id_list))  # Creates comma-separated string

        metadata_parameters = {  # Retrieves coin_metadata listed 1-100
            'id': joined_id,
            'aux': 'logo'
        }
        metadata_response = session.get(api_metadata, params=metadata_parameters)
        metadata_data = json.loads(metadata_response.text)
        metadata = metadata_data['data']

        for unique_id in id_list:
            logo_url = metadata[str(unique_id)]['logo']

            cur.execute("UPDATE coin_info "  # Uses UPDATE instead of INSERT since first insertion init coin_logo column
                        "SET coin_logo = %s "
                        "WHERE coin_id = %s ",
                        (logo_url, unique_id))
            con.commit()  # Commit transaction
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def update_coins():
    try:
        coin_response = session.get(api_data, params=coin_parameters)
        coin_data = json.loads(coin_response.text)
        coins = coin_data['data']

        for x in coins:
            id = x['id']
            rank = x['cmc_rank']
            price = x['quote']['USD']['price']
            daily_change = x['quote']['USD']['percent_change_24h']

            cur.execute("UPDATE coin_info "
                        "SET coin_price = %s, coin_rank = %s, coin_daily_change = %s "
                        "WHERE coin_id = %s",
                        (price, rank, daily_change, id))
            con.commit()  # Commit transaction
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def get_left_coin(current_page):
    cur.execute("SELECT * FROM coin_info WHERE coin_rank = %s", (current_page,))
    rows = cur.fetchall()

    #  ID: x[0] || Name: x[1] || Symbol: x[2] || Price: x[3] || Rank: x[4] || Change: x[5] || Logo: x[6]
    for x in rows:
        embed = discord.Embed(
            title=f'${str(x[3])}',
            description=' ',
            colour=discord.Colour.blurple()
        )
        embed.set_author(
            name=f'{x[4]}. {x[1]} / {x[2]}',
            icon_url=x[6]
        )
        embed.add_field(
            name='24h %',
            value=f'{x[5]:.2f}%',
            inline=False)
        embed.set_footer(text="")
        return embed


def get_right_coin(current_page):
    cur.execute("SELECT * FROM coin_info WHERE coin_rank = %s", (current_page,))
    rows = cur.fetchall()

    #  ID: x[0] || Name: x[1] || Symbol: x[2] || Price: x[3] || Rank: x[4] || Change: x[5] || Logo: x[6]
    for x in rows:
        embed = discord.Embed(
            title=f'${str(x[3])}',
            description=' ',
            colour=discord.Colour.blurple()
        )
        embed.set_author(
            name=f'{x[4]}. {x[1]} / {x[2]}',
            icon_url=x[6]
        )
        embed.add_field(
            name='24h %',
            value=f'{x[5]:.2f}%',
            inline=False)
        embed.set_footer(text="")
    return embed


def get_left_10_coins(current_rank):
    cur.execute("SELECT * FROM coin_info ORDER BY coin_rank asc")
    rows = cur.fetchall()

    if current_rank < 11:
        max = 10
        min = 1
    else:
        max = current_rank
        min = max - 10
        if max > 100:
            max = 100
            min = 90

    embed = discord.Embed(
        title=' ',
        description=' ',
        colour=discord.Colour.blurple()
    )
    #  ID: x[0] || Name: x[1] || Symbol: x[2] || Price: x[3] || Rank: x[4] || Change: x[5] || Logo: x[6]
    for x in rows:
        if min <= x[4] <= max:
            embed.set_author(name=f'Top {max} Crypto Coins',
                             icon_url=BOT_AVATAR)
            embed.add_field(
                name=f'{x[4]}. {x[1]} / {x[2]}',
                value=f'${x[3]}',
                inline=False)
    return embed


def get_right_10_coins(current_rank):
    cur.execute("SELECT * FROM coin_info ORDER BY coin_rank asc")
    rows = cur.fetchall()

    if current_rank > 100:
        max = 100
        min = 90
    else:
        max = current_rank
        min = current_rank - 10
        if max > 100:
            max = 100
            min = 90

    embed = discord.Embed(
        title=' ',
        description=' ',
        colour=discord.Colour.blurple()
    )
    # ID: x[0] || Name: x[1] || Symbol: x[2] || Price: x[3] || Logo: x[4] || Rank: x[5]
    for x in rows:
        if min <= x[4] <= max:
            embed.set_author(name=f'Top {max} Crypto Coins',
                             icon_url=BOT_AVATAR)
            embed.add_field(
                name=f'{x[4]}. {x[1]} / {x[2]}',
                value=f'${x[3]}',
                inline=False)
    return embed


# ---     CHECKS / FUNCTIONS    --- #
def bot_channel_check(ctx):
    botspam_channels = ['bot-spam', 'bot-commands']
    if str(ctx.message.channel) in botspam_channels or ctx.author.id == 291005201840734218:
        return True


def make_sequence(seq):
    if seq is None:
        return ()
    if isinstance(seq, Sequence) and not isinstance(seq, str):
        return seq
    else:
        return seq,


def reaction_check(message=None, emoji=None, author=None, ignore_bot=True):
    message = make_sequence(message)
    message = tuple(m.id for m in message)
    emoji = make_sequence(emoji)
    author = make_sequence(author)

    def check(reaction, user):
        if ignore_bot and user.bot:
            return False
        if message and reaction.message.id not in message:
            return False
        if emoji and reaction.emoji not in emoji:
            return False
        if author and user not in author:
            return False
        return True
    return check


# ---       MAIN LINE       ---#
class Market(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---       SLASH COMMANDS       --- #
    @cog_ext.cog_subcommand(
        base='market',
        name='coin',
        description='Displays cryptocoin info from CoinMarketCap',
        guild_ids=guild_ids,
        options=[
            create_option(
                name='module',
                description=' ',
                required=True,
                option_type=3,
                choices=[
                    create_choice(
                        name='rank',
                        value='rank'
                    ),
                    create_choice(
                        name='name',
                        value='name'
                    )
                ]
            )
        ]
    )
    async def _market_coin(self, ctx: SlashContext, module: str):
        # Variables
        emoji_list = ['◀', '▶']

        # Database
        cur.execute('SELECT * FROM coin_info ORDER BY coin_rank asc')
        rows = cur.fetchall()

        if module == 'rank':
            embed = discord.Embed(
                title='Please enter a rank from 1-100',
                description=' ',
                colour=discord.Colour.blurple()
            )
            await ctx.send(embeds=[embed], delete_after=5.0)

            try:
                msg = await self.bot.wait_for('message', timeout=5.0)
            except asyncio.exceptions.TimeoutError:
                embed = discord.Embed(
                    title=f'{ctx.author} failed to send a message within the allotted time',
                    description=' ',
                    colour=discord.Colour.red()
                )
                await ctx.send(embeds=[embed], delete_after=5.0)

            try:
                coin_number = int(msg.content)
                await msg.delete()  # Deletes message sent by user
                for x in rows:
                    #  ID: x[0] || Name: x[1] || Symbol: x[2] || Price: x[3] || Rank: x[4] || Change: x[5] || Logo: x[6]
                    if x[4] == coin_number:
                        current_page = x[4]
                        embed = discord.Embed(
                            title=f'${str(x[3])}',
                            description=' ',
                            colour=discord.Colour.blurple()
                        )
                        embed.set_author(
                            name=f'{x[4]}. {x[1]} / {x[2]}',
                            icon_url=x[6]
                        )
                        embed.add_field(
                            name='24h %',
                            value=f'{x[5]:.2f}%',
                            inline=False)
                        embed.set_footer(text="")
                message = await ctx.send(embed=embed)

                if current_page <= 1:  # Adds / Removes emoji if it passes threshold
                    await message.add_reaction(emoji_list[1])
                elif current_page >= 100:
                    await message.add_reaction(emoji_list[0])
                else:
                    for emoji in emoji_list:
                        await message.add_reaction(emoji)

                check = reaction_check(message=message, author=ctx.author, emoji=(emoji_list[0], emoji_list[1]))
                while True:  # Continues to run for 10 seconds until user does not click the emojis
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
                        if reaction.emoji == emoji_list[0]:  # Left page
                            await message.delete()  # Deletes embed before sending a new one
                            current_page = current_page - 1
                            if current_page <= 0:
                                current_page = 1
                                embed = get_left_coin(1)
                            else:
                                embed = get_left_coin(current_page)

                            message = await ctx.send(embed=embed)
                            if current_page <= 1:  # Adds / Removes emoji if it passes threshold
                                await message.add_reaction(emoji_list[1])
                            elif current_page >= 100:
                                await message.add_reaction(emoji_list[0])
                            else:
                                for emoji in emoji_list:
                                    await message.add_reaction(emoji)
                            check = reaction_check(message=message, author=ctx.author,
                                                   emoji=(emoji_list[0], emoji_list[1]))

                        elif reaction.emoji == emoji_list[1]:  # Right page
                            await message.delete()  # Deletes embed before sending a new one
                            current_page = current_page + 1
                            if current_page >= 100:
                                current_page = 100
                                embed = get_right_coin(100)
                            else:
                                embed = get_right_coin(current_page)

                            message = await ctx.send(embed=embed)
                            if current_page <= 1:  # Adds / Removes emoji if it passes threshold
                                await message.add_reaction(emoji_list[1])
                            elif current_page >= 100:
                                await message.add_reaction(emoji_list[0])
                            else:
                                for emoji in emoji_list:
                                    await message.add_reaction(emoji)

                            check = reaction_check(message=message, author=ctx.author,
                                                   emoji=(emoji_list[0], emoji_list[1]))
                    except TimeoutError:
                        print('Timeout')
            except ValueError:
                await msg.delete()  # Deletes message sent by user
                embed = discord.Embed(
                    title=f'Input is not a rank: {msg.content}',
                    description=' ',
                    colour=discord.Colour.red()
                )
                await ctx.send(embeds=[embed], delete_after=5.0)

        elif module == 'name':
            embed = discord.Embed(
                title='Please enter a name',
                description=' ',
                colour=discord.Colour.blurple()
            )
            await ctx.send(embeds=[embed], delete_after=5.0)

            try:
                msg = await self.bot.wait_for('message', timeout=5.0)
            except asyncio.exceptions.TimeoutError:
                embed = discord.Embed(
                    title=f'{ctx.author} failed to send a message within the allotted time',
                    description=' ',
                    colour=discord.Colour.red()
                )
                await ctx.send(embeds=[embed], delete_after=5.0)

            try:
                coin_name = msg.content.lower()
                await msg.delete()  # Deletes message sent by user
                for x in rows:
                    #  ID: x[0] || Name: x[1] || Symbol: x[2] || Price: x[3] || Rank: x[4] || Change: x[5] || Logo: x[6]
                    if x[1].lower() == coin_name:
                        current_page = x[4]
                        embed = discord.Embed(
                            title=f'${str(x[3])}',
                            description=' ',
                            colour=discord.Colour.blurple()
                        )
                        embed.set_author(
                            name=f'{x[4]}. {x[1]} / {x[2]}',
                            icon_url=x[6]
                        )
                        embed.add_field(
                            name='24h %',
                            value=f'{x[5]:.2f}%',
                            inline=False)
                        embed.set_footer(text="")
                message = await ctx.send(embed=embed)

                if current_page <= 1:  # Adds / Removes emoji if it passes threshold
                    await message.add_reaction(emoji_list[1])
                elif current_page >= 100:
                    await message.add_reaction(emoji_list[0])
                else:
                    for emoji in emoji_list:
                        await message.add_reaction(emoji)

                check = reaction_check(message=message, author=ctx.author, emoji=(emoji_list[0], emoji_list[1]))
                while True:  # Continues to run for 10 seconds until user does not click the emojis
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
                        if reaction.emoji == emoji_list[0]:  # Left page
                            await message.delete()  # Deletes embed before sending a new one
                            current_page = current_page - 1
                            if current_page <= 0:
                                current_page = 1
                                embed = get_left_coin(1)
                            else:
                                embed = get_left_coin(current_page)

                            message = await ctx.send(embed=embed)
                            if current_page <= 1:  # Adds / Removes emoji if it passes threshold
                                await message.add_reaction(emoji_list[1])
                            elif current_page >= 100:
                                await message.add_reaction(emoji_list[0])
                            else:
                                for emoji in emoji_list:
                                    await message.add_reaction(emoji)
                            check = reaction_check(message=message, author=ctx.author,
                                                   emoji=(emoji_list[0], emoji_list[1]))

                        elif reaction.emoji == emoji_list[1]:  # Right page
                            await message.delete()  # Deletes embed before sending a new one
                            current_page = current_page + 1
                            if current_page >= 100:
                                current_page = 100
                                embed = get_right_coin(100)
                            else:
                                embed = get_right_coin(current_page)

                            message = await ctx.send(embed=embed)
                            if current_page <= 1:  # Adds / Removes emoji if it passes threshold
                                await message.add_reaction(emoji_list[1])
                            elif current_page >= 100:
                                await message.add_reaction(emoji_list[0])
                            else:
                                for emoji in emoji_list:
                                    await message.add_reaction(emoji)

                            check = reaction_check(message=message, author=ctx.author,
                                                   emoji=(emoji_list[0], emoji_list[1]))
                    except TimeoutError:
                        print('Timeout')
            except ValueError:
                await msg.delete()  # Deletes message sent by user
                embed = discord.Embed(
                    title=f'Input is not a name: {msg.content}',
                    description=' ',
                    colour=discord.Colour.red()
                )
                await ctx.send(embeds=[embed], delete_after= 5.0)

    @cog_ext.cog_subcommand(
        base='market',
        name='top',
        description='Displays the top # coins from 1-100',
        guild_ids=guild_ids
    )
    async def _market_top(self, ctx: SlashContext, *, rank):
        # Variables
        emoji_list = ['◀', '▶']

        # Database
        cur.execute('SELECT * FROM coin_info ORDER BY coin_rank asc')  # 1,2,3...,100
        rows = cur.fetchall()

        try:
            rank = int(rank)

            if rank < 11:
                min = 1
                max = 10
            else:
                min = rank - 10
                max = rank
                if max > 100:
                    max = 100

            embed = discord.Embed(
                title=' ',
                description=' ',
                colour=discord.Colour.blurple()
            )
            #  ID: x[0] || Name: x[1] || Symbol: x[2] || Price: x[3] || Rank: x[4] || Change: x[5] || Logo: x[6]
            for x in rows:
                if min <= x[4] <= max:
                    embed.set_author(name=f'Top {max} Crypto Coins',
                                     icon_url=BOT_AVATAR)
                    embed.add_field(
                        name=f'{x[4]}. {x[1]} / {x[2]}',
                        value=f'${x[3]}',
                        inline=False)
                    embed.set_footer(text="")

            message = await ctx.send(embed=embed)
            if rank <= 10:  # Adds / Removes emoji if it passes threshold
                await message.add_reaction(emoji_list[1])
            elif rank >= 100:
                await message.add_reaction(emoji_list[0])
            else:
                for emoji in emoji_list:
                    await message.add_reaction(emoji)

            check = reaction_check(message=message, author=ctx.author, emoji=(emoji_list[0], emoji_list[1]))
            current_page = max
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
                    if reaction.emoji == emoji_list[0]:  # Left page
                        await message.delete()  # Deletes embed before sending a new one
                        current_page = current_page - 10
                        if current_page <= 0:
                            current_page = 10
                            embed = get_left_10_coins(10)
                        else:
                            embed = get_left_10_coins(current_page)

                        message = await ctx.send(embed=embed)
                        if current_page <= 10:  # Adds / Removes emoji if it passes threshold
                            await message.add_reaction(emoji_list[1])
                        elif current_page >= 100:
                            await message.add_reaction(emoji_list[0])
                        else:
                            for emoji in emoji_list:
                                await message.add_reaction(emoji)

                        check = reaction_check(message=message, author=ctx.author,
                                               emoji=(emoji_list[0], emoji_list[1]))

                    elif reaction.emoji == emoji_list[1]:  # Right page
                        await message.delete()  # Deletes embed before sending a new one
                        current_page = current_page + 10
                        if current_page >= 100:
                            current_page = 100
                            embed = get_right_10_coins(100)
                        else:
                            embed = get_right_10_coins(current_page)
                        message = await ctx.send(embed=embed)

                        if current_page <= 1:  # Adds / Removes emoji if it passes threshold
                            await message.add_reaction(emoji_list[1])
                        elif current_page >= 100:
                            await message.add_reaction(emoji_list[0])
                        else:
                            for emoji in emoji_list:
                                await message.add_reaction(emoji)

                        check = reaction_check(message=message, author=ctx.author,
                                               emoji=(emoji_list[0], emoji_list[1]))
                except TimeoutError:
                    print('Timeout')
        except ValueError:
            embed = discord.Embed(
                title=f'Input is not a rank: {rank}',
                description=' ',
                colour=discord.Colour.red()
            )
            await ctx.send(embeds=[embed], delete_after=5.0)

    # ---       PREFIX COMMANDS       --- #
    # @commands.command()
    # @commands.check(bot_channel_check)
    # async def coin(self, ctx, *, name):  # Accepts current rank or coin name
    #     # Variables
    #     emoji_list = ['◀', '▶']
    #
    #     # Database
    #     cur.execute('SELECT * FROM coin_info ORDER BY coin_rank asc')
    #     rows = cur.fetchall()
    #
    #     await ctx.message.delete()  # Deletes command call
    #     try:  # Checks to see if user input 'name' is a rank
    #         coin_number = int(name)
    #         for x in rows:
    #             #  ID: x[0] || Name: x[1] || Symbol: x[2] || Price: x[3] || Rank: x[4] || Change: x[5] || Logo: x[6]
    #             if x[4] == coin_number:
    #                 current_page = x[4]
    #                 embed = discord.Embed(
    #                     title=f'${str(x[3])}',
    #                     description=' ',
    #                     colour=discord.Colour.blurple()
    #                 )
    #                 embed.set_author(
    #                     name=f'{x[4]}. {x[1]} / {x[2]}',
    #                     icon_url=x[6]
    #                 )
    #                 embed.add_field(
    #                     name='24h %',
    #                     value=f'{x[5]:.2f}%',
    #                     inline=False)
    #                 embed.set_footer(text="")
    #         message = await ctx.send(embed=embed)
    #
    #         if current_page <= 1:  # Adds / Removes emoji if it passes threshold
    #             await message.add_reaction(emoji_list[1])
    #         elif current_page >= 100:
    #             await message.add_reaction(emoji_list[0])
    #         else:
    #             for emoji in emoji_list:
    #                 await message.add_reaction(emoji)
    #
    #         check = reaction_check(message=message, author=ctx.author, emoji=(emoji_list[0], emoji_list[1]))
    #         while True:  # Continues to run for 10 seconds until user does not click the emojis
    #             try:
    #                 reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
    #                 if reaction.emoji == emoji_list[0]:  # Left page
    #                     await message.delete()  # Deletes embed before sending a new one
    #                     current_page = current_page - 1
    #                     if current_page <= 0:
    #                         current_page = 1
    #                         embed = get_left_coin(1)
    #                     else:
    #                         embed = get_left_coin(current_page)
    #
    #                     message = await ctx.send(embed=embed)
    #                     if current_page <= 1:  # Adds / Removes emoji if it passes threshold
    #                         await message.add_reaction(emoji_list[1])
    #                     elif current_page >= 100:
    #                         await message.add_reaction(emoji_list[0])
    #                     else:
    #                         for emoji in emoji_list:
    #                             await message.add_reaction(emoji)
    #                     check = reaction_check(message=message, author=ctx.author,
    #                                            emoji=(emoji_list[0], emoji_list[1]))
    #
    #                 elif reaction.emoji == emoji_list[1]:  # Right page
    #                     await message.delete()  # Deletes embed before sending a new one
    #                     current_page = current_page + 1
    #                     if current_page >= 100:
    #                         current_page = 100
    #                         embed = get_right_coin(100)
    #                     else:
    #                         embed = get_right_coin(current_page)
    #
    #                     message = await ctx.send(embed=embed)
    #                     if current_page <= 1:  # Adds / Removes emoji if it passes threshold
    #                         await message.add_reaction(emoji_list[1])
    #                     elif current_page >= 100:
    #                         await message.add_reaction(emoji_list[0])
    #                     else:
    #                         for emoji in emoji_list:
    #                             await message.add_reaction(emoji)
    #
    #                     check = reaction_check(message=message, author=ctx.author,
    #                                            emoji=(emoji_list[0], emoji_list[1]))
    #             except TimeoutError:
    #                 print('Timeout')
    #     except ValueError:
    #         coin_name = name  # User input is confirmed to be a name
    #         for x in rows:
    #             #  ID: x[0] || Name: x[1] || Symbol: x[2] || Price: x[3] || Rank: x[4] || Change: x[5] || Logo: x[6]
    #             if x[1] == coin_name:
    #                 current_page = x[4]
    #                 embed = discord.Embed(
    #                     title=f'${str(x[3])}',
    #                     description=' ',
    #                     colour=discord.Colour.blurple()
    #                 )
    #                 embed.set_author(
    #                     name=f'{x[4]}. {x[1]} / {x[2]}',
    #                     icon_url=x[6]
    #                 )
    #                 embed.add_field(
    #                     name='24h %',
    #                     value=f'{x[5]:.2f}%',
    #                     inline=False)
    #                 embed.set_footer(text="")
    #         message = await ctx.send(embed=embed)
    #
    #         if current_page <= 1:  # Adds / Removes emoji if it passes threshold
    #             await message.add_reaction(emoji_list[1])
    #         elif current_page >= 100:
    #             await message.add_reaction(emoji_list[0])
    #         else:
    #             for emoji in emoji_list:
    #                 await message.add_reaction(emoji)
    #
    #         check = reaction_check(message=message, author=ctx.author, emoji=(emoji_list[0], emoji_list[1]))
    #         while True:  # Continues to run for 10 seconds until user does not click the emojis
    #             try:
    #                 reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
    #                 if reaction.emoji == emoji_list[0]:  # Left page
    #                     await message.delete()  # Deletes embed before sending a new one
    #                     current_page = current_page - 1
    #                     if current_page <= 0:
    #                         current_page = 1
    #                         embed = get_left_coin(1)
    #                     else:
    #                         embed = get_left_coin(current_page)
    #
    #                     message = await ctx.send(embed=embed)
    #                     if current_page <= 1:  # Adds / Removes emoji if it passes threshold
    #                         await message.add_reaction(emoji_list[1])
    #                     elif current_page >= 100:
    #                         await message.add_reaction(emoji_list[0])
    #                     else:
    #                         for emoji in emoji_list:
    #                             await message.add_reaction(emoji)
    #                     check = reaction_check(message=message, author=ctx.author,
    #                                            emoji=(emoji_list[0], emoji_list[1]))
    #
    #                 elif reaction.emoji == emoji_list[1]:  # Right page
    #                     await message.delete()  # Deletes embed before sending a new one
    #                     current_page = current_page + 1
    #                     if current_page >= 100:
    #                         current_page = 100
    #                         embed = get_right_coin(100)
    #                     else:
    #                         embed = get_right_coin(current_page)
    #
    #                     message = await ctx.send(embed=embed)
    #                     if current_page <= 1:  # Adds / Removes emoji if it passes threshold
    #                         await message.add_reaction(emoji_list[1])
    #                     elif current_page >= 100:
    #                         await message.add_reaction(emoji_list[0])
    #                     else:
    #                         for emoji in emoji_list:
    #                             await message.add_reaction(emoji)
    #
    #                     check = reaction_check(message=message, author=ctx.author,
    #                                            emoji=(emoji_list[0], emoji_list[1]))
    #             except TimeoutError:
    #                 print('Timeout')
    #
    # @commands.command()
    # @commands.check(bot_channel_check)
    # async def top(self, ctx, rank):
    #     # Variables
    #     emoji_list = ['◀', '▶']
    #     rank = int(rank)
    #
    #     # Database
    #     cur.execute('SELECT * FROM coin_info ORDER BY coin_rank asc')  # 1,2,3...,100
    #     rows = cur.fetchall()
    #
    #     if rank < 11:
    #         min = 1
    #         max = 10
    #     else:
    #         min = rank - 10
    #         max = rank
    #         if max > 100:
    #             max = 100
    #
    #     embed = discord.Embed(
    #         title=' ',
    #         description=' ',
    #         colour=discord.Colour.blurple()
    #     )
    #     #  ID: x[0] || Name: x[1] || Symbol: x[2] || Price: x[3] || Rank: x[4] || Change: x[5] || Logo: x[6]
    #     for x in rows:
    #         if min <= x[4] <= max:
    #             embed.set_author(name=f'Top {max} Crypto Coins',
    #                              icon_url=BOT_AVATAR)
    #             embed.add_field(
    #                 name=f'{x[4]}. {x[1]} / {x[2]}',
    #                 value=f'${x[3]}',
    #                 inline=False)
    #             embed.set_footer(text="")
    #
    #     message = await ctx.send(embed=embed)
    #     if rank <= 10:  # Adds / Removes emoji if it passes threshold
    #         await message.add_reaction(emoji_list[1])
    #     elif rank >= 100:
    #         await message.add_reaction(emoji_list[0])
    #     else:
    #         for emoji in emoji_list:
    #             await message.add_reaction(emoji)
    #
    #     check = reaction_check(message=message, author=ctx.author, emoji=(emoji_list[0], emoji_list[1]))
    #     current_page = max
    #     while True:
    #         try:
    #             reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
    #             if reaction.emoji == emoji_list[0]:  # Left page
    #                 await message.delete()  # Deletes embed before sending a new one
    #                 current_page = current_page - 10
    #                 if current_page <= 0:
    #                     current_page = 10
    #                     embed = get_left_10_coins(10)
    #                 else:
    #                     embed = get_left_10_coins(current_page)
    #
    #                 message = await ctx.send(embed=embed)
    #                 if current_page <= 10:  # Adds / Removes emoji if it passes threshold
    #                     await message.add_reaction(emoji_list[1])
    #                 elif current_page >= 100:
    #                     await message.add_reaction(emoji_list[0])
    #                 else:
    #                     for emoji in emoji_list:
    #                         await message.add_reaction(emoji)
    #
    #                 check = reaction_check(message=message, author=ctx.author,
    #                                        emoji=(emoji_list[0], emoji_list[1]))
    #
    #             elif reaction.emoji == emoji_list[1]:  # Right page
    #                 await message.delete()  # Deletes embed before sending a new one
    #                 current_page = current_page + 10
    #                 if current_page >= 100:
    #                     current_page = 100
    #                     embed = get_right_10_coins(100)
    #                 else:
    #                     embed = get_right_10_coins(current_page)
    #                 message = await ctx.send(embed=embed)
    #
    #                 if current_page <= 1:  # Adds / Removes emoji if it passes threshold
    #                     await message.add_reaction(emoji_list[1])
    #                 elif current_page >= 100:
    #                     await message.add_reaction(emoji_list[0])
    #                 else:
    #                     for emoji in emoji_list:
    #                         await message.add_reaction(emoji)
    #
    #                 check = reaction_check(message=message, author=ctx.author,
    #                                        emoji=(emoji_list[0], emoji_list[1]))
    #         except TimeoutError:
    #             print('Timeout')
    #
    # @coin.error
    # async def coin_error(self, ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         embed = discord.Embed(
    #             title='Error: Specify coin rank or name',
    #             description=' ',
    #             colour=discord.Colour.red()
    #         )
    #         embed.set_footer(text='ex => ;coin 4\nex => ;coin Bitcoin')
    #
    #         await ctx.send(embed=embed, delete_after=5)
    #
    # @top.error
    # async def top_error(self, ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         embed = discord.Embed(
    #             title='Error: Specify top #',
    #             description=' ',
    #             colour=discord.Colour.red()
    #         )
    #         embed.set_footer(text='ex => ;top 45')
    #
    #         await ctx.send(embed=embed, delete_after=5)


# ---       END MAIN        ---#
def setup(bot):
    bot.add_cog(Market(bot))
