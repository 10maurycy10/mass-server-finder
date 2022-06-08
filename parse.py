import mariadb
import tqdm
import json
import typing as t
import asyncio
from dataclasses import dataclass
from mcstatus import JavaServer

config = json.loads(open("config.json").read())

db = mariadb.connect(
    user=config["db_username"],
    password=config["db_passwd"],
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_dbname"]
)

dbc = db.cursor()
dbc.execute("select ip,data,timestamp from rawpings where error=0 and not (ip, timestamp) in (select ip,timestamp from servers);");
raw = [raw for raw in dbc]

for (ip, data, time) in raw: 
    data = json.loads(data)
    name = data.get('description')
    version_obj = data.get('version')
    version_name = "unknown"
    if version_obj:
        version_name = version_obj.get('name') + " [" + str(version_obj.get("protocol")) + "]"
    players = data.get("players")
    player_online = -1
    player_cap = -1
    if players:
        player_online = players.get("online")
        player_cap = players.get("max")

    dbc = db.cursor()
    dbc.execute("insert into servers (cap, online, ip, version, name, timestamp) values (?, ?, ?, ?, ?, ?)", (player_cap, player_online, ip, version_name, json.dumps(name), time))

    if players.get("sample"):
        for player in players.get("sample"):
            dbc = db.cursor()
            dbc.execute("insert into players (uuid, name, server, timestamp) values (?, ?, ?, ?);", (player.get("id"), player.get("name"), ip, time))

db.commit()
