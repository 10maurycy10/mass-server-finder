import mariadb
import tqdm
import json
import typing as t
import asyncio
from mcstatus import JavaServer
import time

config = json.loads(open("config.json").read())

db = mariadb.connect(
    user=config["db_username"],
    password=config["db_passwd"],
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_dbname"]
)


def batch(iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

async def ping(ip, port):
    try:
        status = await JavaServer(host=ip, port=port).async_status()
        return (ip,status.raw, 0)
    except Exception as e:
        return (ip,"\"Erroring\"", 1)


async def mass_ping(ips):
    return await asyncio.gather(*[
        ping(ip, 25565) for ip in ips
    ])

async def mass_ping_insert(ips):
    for (ip, ping, error) in tqdm.tqdm(await mass_ping(ips)):
            dbc = db.cursor()
            dbc.execute("insert into rawpings values (?, ?, ?, ?);", (json.dumps(ping), ip, error, int(time.time())))
            dbc.execute("update ips set lastping=? where ip=?;", (int(time.time()),ip))
    db.commit()

while True:
    recheck_time = time.time() - config["recheck_interval"];
    dbc = db.cursor()
    dbc.execute("select ip from ips where lastping<? or lastping is null limit 1000;", (recheck_time,));
    ips = [ip[0] for ip in dbc]
    if len(ips) == 0:
        break
    asyncio.run(mass_ping_insert(ips))
