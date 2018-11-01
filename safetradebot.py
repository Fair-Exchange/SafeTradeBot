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
                    embed.add_field(name="$votes", value="Actual voting list of https://vote.safe.trade/", inline=False)
                    await message.author.send(f"Hi {message.author.mention}. Here are the commands for Safe.TradeBot", embed=embed)
                elif command == "$markets":
                    if not isinstance(message.channel, discord.DMChannel):
                        await message.channel.send(f"Hi {message.author.mention}. I have sent you a direct message with market list")

                    embed = discord.Embed(title="Markets available on Safe.Trade", url="https://safe.trade", color=0x131afe)
                    embed.set_author(name="Safe.TradeBot", url="http://www.safecoin.org",
                                    icon_url="https://safe.trade/assets/logo2-f90245b6bdcfa4f7582e36d0bc7c69d513934aa8c5a1c6cbc884ef91768bda00.png")
                    embed.add_field(name='Markets', value="\n".join(sorted(market.get("name") for market in self.markets)), inline=True)
                    await message.author.send(f"{message.author.mention} Here are the available markets for safe.trade", embed=embed)
                elif command == "$votes":
                    try:
                        response = requests.get("https://vote.safe.trade/api/stats")
                    except:
                        await message.channel.send(f"{message.author.mention} Voting list is unavailable at this time")
                        return
                    data = response.json()
                    embed = discord.Embed(title="Voting list for vote.safe.trade", url="https://vote.safe.trade", color=0x131afe)
                    embed.set_author(name="Safe.TradeBot", url="http://www.safecoin.org",
                                    icon_url="https://safe.trade/assets/logo2-f90245b6bdcfa4f7582e36d0bc7c69d513934aa8c5a1c6cbc884ef91768bda00.png")
                    embed.add_field(name="Round #{} ending on {}".format(data["round"]["number"], datetime.date.fromtimestamp(data["round"]["endDate"]).strftime("%h %d %Y")), value="󠀠", inline=False)
                    s = max(8, max(len(item["name"]) for item in data["items"]))
                    v = max(5, max(len(item["votes"]) for item in data["items"]))
                    embed.add_field(name="Voting list", value="""
```
+--+---------{t}-+------+------{j}-+
|# | Currency{0} |Ticker| Votes{1} |
+--+---------{t}-+------+------{j}-+
{votes}
+--+---------{t}-+------+------{j}-+
```
""".format(
    " "*(s-8), " "*(v-5), t="-"*(s-8), j="-"*(v-5),
    votes="\n".join("|{:<2d}| {:<{s}} | {:<4} | {:<{v}} |".format(item["topNumber"], item["name"], item["ticker"], item["votes"], s=s, v=v) for item in data["items"])
), inline=False)
                    await message.channel.send(f"{message.author.mention} Here are the current vote results for Safe.Trade", embed=embed)
                elif re.match(r"^\$[a-zA-Z]{3,}(?:\/?[a-zA-Z]{3,})?$", command):
                    pair = message.content[1:].upper()
                    for market in self.markets:
                        if pair in (market.get("name"),
                                    market.get("name").replace("/", ""),
                                    "/".join(market.get("name").split("/")[::-1]),
                                    "".join(market.get("name").split("/")[::-1])):
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

                    embed = discord.Embed(title="{arrow} {} {arrow}\t{:+.2f}%".format(market.get("name"), percentage, arrow="🔼" if percentage>= 0 else "🔽"), url="https://safe.trade", color=0x131afe)
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