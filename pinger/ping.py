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
        return (ip,'\"Erroring\"',1)



async def mass_ping(ips):
    return await asyncio.gather(*[
        ping(ip, 25565) for ip in ips
    ])

async def mass_ping_insert(ips):
    data = [result for result in await mass_ping(ips)]
    
    rawpings = [(json.dumps(ping), ip, error, int(time.time())) for (ip,ping,error) in data]
    pinged_ips = [(int(time.time()),ip) for (ip,ping,error) in data]

    dbc = db.cursor()

    dbc.executemany("insert into rawpings values (?, ?, ?, ?);", rawpings);
    dbc.executemany("update ips set lastping=? where ip=?;", pinged_ips);
    db.commit()

import logging
logging.getLogger('asyncio').setLevel(logging.CRITICAL)

dbc = db.cursor()
dbc.execute("select ip from ips where lastping is null or lastping = 0;");
ips = [ip[0] for ip in dbc]
ipblocks = list(batch(ips, n=2));

print("pinging new ips")

for ipbatch in tqdm.tqdm(ipblocks):
    asyncio.run(mass_ping_insert(ipbatch))
    

recheck_time = time.time() - config["recheck_interval"];    
dbc = db.cursor()
dbc.execute("select ip from ips where lastping<?;", (recheck_time,));
ips = [ip[0] for ip in dbc]
ipblocks = list(batch(ips, n=1000));

print("repinging old ips")

for ipbatch in tqdm.tqdm(ipblocks):
    asyncio.run(mass_ping_insert(ipbatch))

  
