import discord
import requests
import datetime
import asyncio
import re

class Bot(discord.Client):
    markets = {}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.price_update())
        self.bg_task2 = self.loop.create_task(self.markets_update())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel) or message.channel.name in ('test', 'safetrade', 'bot-commands'):
            if message.content:
                command = message.content.split()[0].lower()
                if command == "$help":
                    if not isinstance(message.channel, discord.DMChannel):
                        await message.channel.send(f"Hi {message.author.mention}. I have sent you a direct message with help info")

                    embed = discord.Embed(title="Bot commands for Safe.TradeBot", url="https://safe.trade", color=0x131afe)
                    embed.set_author(name="Safe.TradeBot", url="http://www.safecoin.org",
                                    icon_url="https://safe.trade/assets/logo2-f90245b6bdcfa4f7582e36d0bc7c69d513934aa8c5a1c6cbc884ef91768bda00.png")
                    embed.add_field(name="$markets", value="List all available markets on Safe.Trade", inline=False)
                    embed.add_field(name="$<market>", value="Trade stats for the market you choose ($safebtc for SAFE/BTC market, $xsgsafe for XSG/SAFE market and so on)", inline=False)
                    await message.author.send(f"Hi {message.author.mention}. Here are the commands for Safe.TradeBot", embed=embed)
                elif command == "$markets":
                    if not isinstance(message.channel, discord.DMChannel):
                        await message.channel.send(f"Hi {message.author.mention}. I have sent you a direct message with market list")

                    embed = discord.Embed(title="Markets available on Safe.Trade", url="https://safe.trade", color=0x131afe)
                    embed.set_author(name="Safe.TradeBot", url="http://www.safecoin.org",
                                    icon_url="https://safe.trade/assets/logo2-f90245b6bdcfa4f7582e36d0bc7c69d513934aa8c5a1c6cbc884ef91768bda00.png")
                    embed.add_field(name='Markets', value="\n".join(market.get("name") for market in self.markets), inline=True)
                    await message.author.send(f"{message.author.mention} Here are the available markets for safe.trade", embed=embed)

                elif command.startswith('$'):
                    pair = message.content[1:]
                    for market in self.markets:
                        if pair in (market.get("id"), market.get("name").lower()):
                            break
                    else:
                        await message.channel.send(f"{message.author.mention} Market pair does not exist")
                        return
                    try:
                        response = requests.get('https://safe.trade/api/v2/tickers/{}'.format(market.get("id")))
                    except:
                        await message.channel.send(f"{message.author.mention} Trade data is unavailable at this time")
                        return
                    data = response.json()
                    ticker = data.get("ticker")
                    try:
                        response = requests.get('https://safe.trade/api/v2/k?market={}&period=15&limit=97'.format(market.get("id")))
                    except:
                        percentage = 0
                    else:
                        percentage = 100-100*response.json()[0][3]/float(ticker.get('last'))

                    time = datetime.datetime.fromtimestamp(data.get('at')).strftime('%Y-%m-%d %H:%M:%S')

                    embed = discord.Embed(title="{}\t{:+.2f}%".format(market.get("name"), percentage), url="https://safe.trade", color=0x131afe)
                    embed.set_author(name="Safe.TradeBot", url="http://www.safecoin.org",
                                    icon_url="https://safe.trade/assets/logo2-f90245b6bdcfa4f7582e36d0bc7c69d513934aa8c5a1c6cbc884ef91768bda00.png")
                    embed.add_field(name='Buy', value=ticker.get('buy'), inline=True)
                    embed.add_field(name='Sell', value=ticker.get('sell'), inline=True)
                    embed.add_field(name='Last', value=ticker.get('last'), inline=True)
                    embed.add_field(name='High', value=ticker.get('high'), inline=True)
                    embed.add_field(name='Low', value=ticker.get('low'), inline=True)
                    embed.add_field(name='24h Vol', value=ticker.get('vol'), inline=True)
                    embed.set_footer(text=f"data correct as of {time}")
                    await message.channel.send("{} Here are the stats for {}".format(message.author.mention, market.get("name")), embed=embed)

    async def price_update(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                response = requests.get('https://safe.trade/api/v2/tickers/safebtc')
            except:
                data = "no data"
            else:
                data = response.json().get("ticker").get("last")
            await self.change_presence(status=discord.Status.online,
                                       activity=discord.Game(name=f'SAFE/BTC: {data}'))
            await asyncio.sleep(120)

    async def markets_update(self):
        while not self.is_closed():
            try:
                response = requests.get('https://safe.trade/api/v2/markets')
            except:
                pass
            else:
                self.markets = response.json()
            await asyncio.sleep(21600)

client = Bot()
client.run('TOKEN')