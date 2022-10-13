import json
import discord
from discord.ext import commands
import random
import os
import mariadb
import time
import datetime
from mcstatus import JavaServer

# load the configuration file
config = json.loads(open("config.json").read())

# connect to database
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
intents.message_content = True

bot = commands.Bot(command_prefix='.', description=description, intents=intents)

def sample(dbc):
    for i in dbc:
        return i
    return None

def truncate(s):
    print("truncating", s)
    if len(s.rstrip())==0:
        return "[EMPTY]"
    if len(s)>1024:
        return s[:1024]
    else:
        return s

# format json chat for use in discord
# TODO convert json formating to ansi insted of discording
def format_chat(data):
    print(data)
    text = ""
    if "text" in data:
        text = text + data["text"]
    if "extra" in data:
        for obj in data["extra"]:
            text = text + format_chat(obj)
    return text

# lookup table for converting (depricated) chat control codes into ansi.
chat_control_ansi = {
        "0": "[30m",
        "1": "[34m",
        "2": "[32m",
        "3": "[36m",
        "4": "[31m",
        "5": "[35m",
        "6": "[33m",
        "7": "[37m",
        "8": "[90m",
        "9": "[94m",
        "a": "[92m",
        "b": "[96m",
        "c": "[91m",
        "d": "[95m",
        "e": "[93m",
        "f": "[97m",

        "k": "[8m",
        "l": "[1m",
        "m": "[9m",
        "n": "[4m",
        "o": "[3m",
        "r": "[0m",
}

# convert minecraft selectors into ansi color codes
def selectors_to_ansi(text):
    ansibuffer = ""
    while len(text) > 0:
        c = text[0]
        if c == '§' or c == '&':
            ansibuffer = ansibuffer + chat_control_ansi[text[1]]
            print(json.dumps(chat_control_ansi[text[1]]))
            text = text[2:]
        else:
            ansibuffer = ansibuffer + c
            text = text[1:]
    print(json.dumps(ansibuffer))
    return ansibuffer
# format chat for use in disord
def print_chat(chat):
    if chat[0] == '{':
        return '```ansi\n' + selectors_to_ansi(format_chat(json.loads(chat))) + '\n```'
    else:
        return '```ansi\n' + selectors_to_ansi(chat) + '\n```'


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command(help="Show the status for a java server ip, cached data.")
async def status(ctx, ip: str):
    db.commit()
    print("Status for " + ip)
    """Shows the last seen status of a server."""
    dbc = db.cursor()
    dbc.execute("select timestamp,cap,online,name,modded,version from servers where ip=? order by -timestamp;", (ip,))

    stats = sample(dbc)
    if stats:
        time = datetime.datetime.fromtimestamp(stats[0])
        cap = stats[1]
        online = stats[2]
        name = stats[3]
        modded = stats[4]
        version = stats[5]
        print(stats)
        embed = discord.Embed(title=f"__**{ip} Stats as of {time}:**__",timestamp= ctx.message.created_at)
        embed.add_field(name="Last seen", value=truncate(str(time)))
        embed.add_field(name="Player cap", value=truncate(str(cap)))
        embed.add_field(name="Players", value=truncate(str(online)))
        embed.add_field(name="Version", value=truncate(version))
        if modded == 1:
            embed.add_field(name="Is modded", value="yes")
        else:
            embed.add_field(name="Is modded", value="no")
        embed.add_field(name="MOTD", value=truncate(print_chat(name)))
        await ctx.send(embed=embed)
    else:
        await ctx.send("I have never seen that server. :(")
    print("Done")

@bot.command(help="Search database for a player, Unrelyable as servers dont return full playerdata on server list ping.")
async def wherewas(ctx, username: str):
    print("Searching for " + username)
    embed = discord.Embed(title=f"__**Seen {username}**__",timestamp= ctx.message.created_at)
    dbc = db.cursor()
    dbc.execute("select server,timestamp from players where name=? limit 50;", (username,))
    for record in dbc:
        ip = record[0];
        time = datetime.datetime.fromtimestamp(record[1])
        embed.add_field(name=ip, value=time)
    await ctx.send(embed=embed)
    print("Done")

@bot.command(help="Find a server by searching for a substring in the motd")
async def inmotd(ctx, substring: str):
    db.commit()
    print("Searching in motds " + substring)
    dbc = db.cursor()
    dbc.execute("select ip,name from servers where name like ? group by ip limit 50;", ("%" + substring + "%",))
    embed = discord.Embed(title=f"__**Servers matching {substring}**__",timestamp= ctx.message.created_at)
    for record in dbc:
        if record[1][0] == "{":
            embed.add_field(name=record[0], value=truncate(print_chat(record[1])))
        else:
            embed.add_field(name=record[0], value=truncate(record[1]))
    await ctx.send(embed=embed);
    print("Done")

@bot.command(help="Shows a random server ip")
async def rand(ctx):
    db.commit()
    print("Random server")
    dbc = db.cursor()
    dbc.execute("select ip,version from servers order by rand() limit 1");
    server = sample(dbc)
    embed = discord.Embed(title=f"__**Random server**__",timestamp= ctx.message.created_at)
    if server:
        embed.add_field(name="ip", value=server[0])
        embed.add_field(name="version", value=truncate(server[1]))
    await ctx.send(embed=embed);
    print("Done")

@bot.command(help="Shows a random server running a given version")
async def randver(ctx, version: str):
    db.commit()
    print("Random server " + version)
    dbc = db.cursor()
    dbc.execute("select ip,version from servers where version like ? order by rand() limit 1", (version + "%",));
    server = sample(dbc)
    embed = discord.Embed(title=f"__**Random server**__",timestamp= ctx.message.created_at)
    if server:
        embed.add_field(name="ip", value=server[0])
        embed.add_field(name="version", value=truncate(server[1]))
    else:
        embed.add_field(name="error", value="no servers matched")
    await ctx.send(embed=embed);
    print("done")

#TODO fix motd formating
@bot.command(help="Pings a server to get realtime data")
async def ping(ctx, ip: str):
    db.commit()
    embed = discord.Embed(title=f"__**Stats for {ip} as of NOW**__",timestamp= ctx.message.created_at)
    if True:
    #try:
        status = await JavaServer(host=ip, port=25565).async_status()
        motd = status.description
        online = status.players.online
        cap = status.players.max
        version = (status.version.name + " [" + str(status.version.protocol) + ']')
        #status = json.loads(status)
        embed.add_field(name="ip", value=ip)
        embed.add_field(name="Version", value=truncate(version))
        if len(motd) > 0:
            print(motd)
            if motd[0] == '{':
                embed.add_field(name="MOTD", value=truncate(print_chat(motd)))
            else:
                embed.add_field(name="MOTD", value=truncate(motd))
        embed.add_field(name="Online", value=truncate(str(online)))
        embed.add_field(name="Player cap", value=truncate(str(cap)))
    #except Exception as e:
    #    print("error pinging", e)
    #    embed.add_field(name="error", value=e)
    await ctx.send(embed=embed)

bot.run(os.environ["DISCORD_TOKEN"])
