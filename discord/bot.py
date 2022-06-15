import json
import discord
from discord.ext import commands
import random
import mariadb
import time
import datetime

config = json.loads(open("config.json").read())

db = mariadb.connect(
    user=config["db_username"],
    password=config["db_passwd"],
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_dbname"]
)


description = '''A frontend for let's minecraft server db.'''

intents = discord.Intents.default()
intents.members = True
#intents.message_content = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

def print_chat(data):
    text = ""
    if "text" in data:
        text = text + data["text"]
    if "extra" in data:
        for obj in data["extra"]:
            text = text + print_chat(obj)
    return text

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command(help="Show the status for a java server ip, cached data.")
async def status(ctx, ip: str):
    print("Status for " + ip)
    """Shows the last seen status of a server."""
    dbc = db.cursor()
    dbc.execute("select timestamp,cap,online,name,modded,version from servers where ip=? order by -timestamp;", (ip,))
    stats = next(dbc)
    if stats:
        time = datetime.datetime.fromtimestamp(stats[0])
        cap = stats[1]
        online = stats[2]
        name = stats[3]
        modded = stats[4]
        version = stats[5]
        print(stats)
        embed = discord.Embed(title=f"__**{ip} Stats as of {time}:**__",timestamp= ctx.message.created_at)
        embed.add_field(name="Last seen", value=time)
        embed.add_field(name="Player cap", value=cap)
        embed.add_field(name="Players", value=online)
        embed.add_field(name="Version", value=version)
        if modded == 1:
            embed.add_field(name="Is modded", value="yes")
        else:
            embed.add_field(name="Is modded", value="no")
        if name[0] == '{':
            embed.add_field(name="MOTD", value=print_chat(json.loads(name)))
        else:
            embed.add_field(name="MOTD", value=name)
        await ctx.send(embed=embed)
    else:
        await ctx.send("I have never seen that server. :(")
    print("Done")

@bot.command(help="Search database for a player, Unrelyable as servers dont return full playerdata on server list ping.")
async def wherewas(ctx, username: str):
    print("Searching for " + username)
    embed = discord.Embed(title=f"__**Seen {username}**__",timestamp= ctx.message.created_at)
    dbc = db.cursor()
    dbc.execute("select server,timestamp from players where name=?;", (username,))
    for record in dbc:
        ip = record[0];
        time = datetime.datetime.fromtimestamp(record[1])
        embed.add_field(name=ip, value=time)
    await ctx.send(embed=embed)
    print("Done")

@bot.command(help="Find a server by searching for a substring in the motd")
async def inmotd(ctx, substring: str):
    print("Searching in motds " + substring)
    dbc = db.cursor()
    dbc.execute("select ip,name from servers where name like ? group by ip;", ("%" + substring + "%",))
    embed = discord.Embed(title=f"__**Servers matching {substring}**__",timestamp= ctx.message.created_at)
    for record in dbc:
        if record[1][0] == "{":
            embed.add_field(name=record[0], value=print_chat(json.loads(record[1])))
        else:
            embed.add_field(name=record[0], value=record[1])
    await ctx.send(embed=embed);
    print("Done")

@bot.command(help="Shows a random server ip")
async def rand(ctx):
    print("Random server")
    dbc = db.cursor()
    dbc.execute("select ip,version from servers order by rand() limit 1");
    server = next(dbc)
    embed = discord.Embed(title=f"__**Random server**__",timestamp= ctx.message.created_at)
    if server:
        embed.add_field(name="ip", value=server[0])
        embed.add_field(name="version", value=server[1])
    await ctx.send(embed=embed);
    print("Done")

@bot.command(help="Shows a random server running a given version")
async def randver(ctx, version: str):
    print("Random server " + version)
    dbc = db.cursor()
    dbc.execute("select ip,version from servers where version like ? order by rand() limit 1", (version + "%",));
    server = next(dbc)
    embed = discord.Embed(title=f"__**Random server**__",timestamp= ctx.message.created_at)
    if server:
        embed.add_field(name="ip", value=server[0])
        embed.add_field(name="version", value=server[1])
    else:
        embed.add_field(name="error", value="no servers matched")
    await ctx.send(embed=embed);
    print(done)


bot.run(config["token"])
