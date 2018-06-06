# install python 3.6
# python3.6 -m pip install -U https://github.com/Rapptz/discord.py/archive/rewrite.zip
# python3.6 -m pip install -U "yarl<1.2"

import discord
import requests
import datetime
from discord.ext import commands
import asyncio

client = discord.Client()
bot = commands.Bot(command_prefix='$')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    bot.loop.create_task(update_bot_btc_price())


bot.remove_command('help')


@bot.command()
async def help(ctx):
    # check the command has been issued from a valid channel.
    valid_channel = check_valid_channels(ctx)
    if valid_channel is False:
        return

    await ctx.send(f"Hi {ctx.author.mention}. I have sent you a direct message with help info")
    await ctx.author.send(f"Hi {ctx.author.mention}. Here are the commands for Safe.TradeBot")

    embed = discord.Embed(title="Bot commands for Safe.TradeBot", url="http://safe.trade", color=0x131afe)
    embed.set_author(name="Safe.TradeBot", url="http://www.safecoin.org",
                     icon_url="https://safe.trade/assets/logo2-f90245b6bdcfa4f7582e36d0bc7c69d513934aa8c5a1c6cbc884ef91768bda00.png")
    embed.add_field(name="$markets", value="List all available markets on Safe.Trade", inline=False)
    embed.add_field(name="$safebtcz", value="Trade stats for SAFE/BTCZ", inline=False)
    embed.add_field(name="$safebtc", value="Trade stats for SAFE/BTC", inline=False)
    embed.add_field(name="$safeltc", value="Trade stats for SAFE/LTC", inline=False)
    embed.add_field(name="$zensafe", value="Trade stats for ZEN/SAFE", inline=False)
    embed.add_field(name="$xsgsafe", value="Trade stats for XSG/SAFE", inline=False)
    await ctx.author.send(embed=embed)


@bot.command()
async def markets(ctx):
    # check the command has been issued from a valid channel.
    valid_channel = check_valid_channels(ctx)
    if valid_channel is False:
        return

    data = get_markets()

    # check we have result. Exit if we don't
    if data is None:
        await ctx.send(f"{ctx.author.mention} Market data is unavailable at this time")
        return

    marketdata = []
    for item in data:
        marketdata.append(item.get('name'))
    output = '\n'.join(marketdata)

    await ctx.send(f"{ctx.author.mention} Here are the available markets for safe.trade")

    # https://cog-creators.github.io/discord-embed-sandbox/
    embed = discord.Embed(title="Markets available on Safe.Trade", url="http://safe.trade", color=0x131afe)
    embed.set_author(name="Safe.TradeBot", url="http://www.safecoin.org",
                     icon_url="https://safe.trade/assets/logo2-f90245b6bdcfa4f7582e36d0bc7c69d513934aa8c5a1c6cbc884ef91768bda00.png")
    embed.add_field(name='Markets', value=output, inline=True)
    await ctx.send(embed=embed)


@bot.command()
async def safebtcz(ctx):
    # check the command has been issued from a valid channel.
    valid_channel = check_valid_channels(ctx)
    if valid_channel is False:
        return

    data = get_pair(str(ctx.command))
    pair = str(ctx.command).upper().replace('SAFE', 'SAFE/')

    # check we have result. Exit if we don't
    if data is None:
        await ctx.send(f"{ctx.author.mention} Trade data is unavailable at this time")
        return

    at = data.get('at')
    ticker = data.get('ticker')

    buy = ticker.get('buy')
    sell = ticker.get('sell')
    high = ticker.get('high')
    low = ticker.get('low')
    last = ticker.get('last')
    vol = ticker.get('vol')

    await ctx.send(f"{ctx.author.mention} Here are the stats for " + pair)

    embed = add_embeds(pair, buy, sell, high, low, last, vol, at)
    await ctx.send(embed=embed)


@bot.command()
async def safebtc(ctx):
    # check the command has been issued from a valid channel.
    valid_channel = check_valid_channels(ctx)
    if valid_channel is False:
        return

    data = get_pair(str(ctx.command))
    pair = str(ctx.command).upper().replace('SAFE', 'SAFE/')

    # check we have result. Exit if we don't
    if data is None:
        await ctx.send(f"{ctx.author.mention} Trade data is unavailable at this time")
        return

    at = data.get('at')
    ticker = data.get('ticker')

    buy = ticker.get('buy')
    sell = ticker.get('sell')
    high = ticker.get('high')
    low = ticker.get('low')
    last = ticker.get('last')
    vol = ticker.get('vol')

    await ctx.send(f"{ctx.author.mention} Here are the stats for " + pair)

    embed = add_embeds(pair, buy, sell, high, low, last, vol, at)
    await ctx.send(embed=embed)


@bot.command()
async def safeltc(ctx):
    # check the command has been issued from a valid channel.
    valid_channel = check_valid_channels(ctx)
    if valid_channel is False:
        return

    data = get_pair(str(ctx.command))
    pair = str(ctx.command).upper().replace('SAFE', 'SAFE/')

    # check we have result. Exit if we don't
    if data is None:
        await ctx.send(f"{ctx.author.mention} Trade data is unavailable at this time")
        return

    at = data.get('at')
    ticker = data.get('ticker')

    buy = ticker.get('buy')
    sell = ticker.get('sell')
    high = ticker.get('high')
    low = ticker.get('low')
    last = ticker.get('last')
    vol = ticker.get('vol')

    await ctx.send(f"{ctx.author.mention} Here are the stats for " + pair)

    embed = add_embeds(pair, buy, sell, high, low, last, vol, at)
    await ctx.send(embed=embed)


@bot.command()
async def zensafe(ctx):
    # check the command has been issued from a valid channel.
    valid_channel = check_valid_channels(ctx)
    if valid_channel is False:
        return

    data = get_pair(str(ctx.command))
    pair = str(ctx.command).upper().replace('ZEN', 'ZEN/')

    # check we have result. Exit if we don't
    if data is None:
        await ctx.send(f"{ctx.author.mention} Trade data is unavailable at this time")
        return

    at = data.get('at')
    ticker = data.get('ticker')

    buy = ticker.get('buy')
    sell = ticker.get('sell')
    high = ticker.get('high')
    low = ticker.get('low')
    last = ticker.get('last')
    vol = ticker.get('vol')

    await ctx.send(f"{ctx.author.mention} Here are the stats for " + pair)

    embed = add_embeds(pair, buy, sell, high, low, last, vol, at)
    await ctx.send(embed=embed)


@bot.command()
async def xsgsafe(ctx):
    # check the command has been issued from a valid channel.
    valid_channel = check_valid_channels(ctx)
    if valid_channel is False:
        return

    data = get_pair(str(ctx.command))
    pair = str(ctx.command).upper().replace('XSG', 'XSG/')

    # check we have result. Exit if we don't
    if data is None:
        await ctx.send(f"{ctx.author.mention} Trade data is unavailable at this time")
        return

    at = data.get('at')
    ticker = data.get('ticker')

    buy = ticker.get('buy')
    sell = ticker.get('sell')
    high = ticker.get('high')
    low = ticker.get('low')
    last = ticker.get('last')
    vol = ticker.get('vol')

    await ctx.send(f"{ctx.author.mention} Here are the stats for " + pair)

    embed = add_embeds(pair, buy, sell, high, low, last, vol, at)
    await ctx.send(embed=embed)


# get available markets
def get_markets():
    data = None

    try:
        response = requests.get('https://safe.trade/api/v2/markets')
        data = response.json()
        return data
    except Exception as e:
        print('Error retrieving data for markets')
        return data


# get the trading pair based on the bot command name
def get_pair(pair):
    data = None

    try:
        response = requests.get('https://safe.trade/api/v2/tickers/' + pair)
        data = response.json()
        return data
    except Exception as e:
        print('Error retrieving data for ' + pair)
        return data


# add formatting for all pairs in one convenient location
def add_embeds(pair, buy, sell, high, low, last, vol, at):
    # convert time
    time = datetime.datetime.fromtimestamp(at).strftime('%Y-%m-%d %H:%M:%S')

    # https://cog-creators.github.io/discord-embed-sandbox/
    embed = discord.Embed(title="Trade stats for " + pair, url="http://safe.trade", color=0x131afe)
    embed.set_author(name="Safe.TradeBot", url="http://www.safecoin.org",
                     icon_url="https://safe.trade/assets/logo2-f90245b6bdcfa4f7582e36d0bc7c69d513934aa8c5a1c6cbc884ef91768bda00.png")
    embed.add_field(name='Buy', value=buy, inline=True)
    embed.add_field(name='Sell', value=sell, inline=True)
    embed.add_field(name='Last', value=last, inline=True)
    embed.add_field(name='High', value=high, inline=True)
    embed.add_field(name='Low', value=low, inline=True)
    embed.add_field(name='24h Vol', value=vol, inline=True)
    embed.set_footer(text="data correct as of " + str(time))
    return embed


# only allow bot to speak in these channels or through a direct message
def check_valid_channels(ctx):
    validity = False
    if str(ctx.message.channel) in ('test', 'safetrade', 'bot-commands') or 'Direct Message' in str(
            ctx.message.channel):
        validity = True
    return validity


# get btc price for status
def get_btc_price():
    try:
        response = requests.get('https://safe.trade/api/v2/tickers/safebtc')
        data = response.json()
        ticker = data.get('ticker')
        last = ticker.get('last')
        return last
    except Exception as e:
        data = 'no data'
        return data


# task to update btc price
async def update_bot_btc_price():
    while True:
        await bot.change_presence(status=discord.Status.online,
                                  activity=discord.Game(name='SAFE/BTC: ' + get_btc_price()))
        await asyncio.sleep(120)


# test bot id
bot.run('id goes here')