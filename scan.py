import masscan
import mariadb
import tqdm
import json

config = json.loads(open("config.json").read())

db = mariadb.connect(
    user=config["db_username"],
    password=config["db_passwd"],
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_dbname"]
)
def scan_block(block):
    mas= masscan.PortScanner()
    mas.scan('{}.0.0.0/8'.format(block), ports='25565', arguments='--max-rate 1000000')

    for ip in tqdm.tqdm(mas.scan_result.get("scan").keys()):
        dbc = db.cursor()
        dbc.execute("insert into ips values (?, 0);", (ip,))
    db.commit()

dbc = db.cursor()
dbc.execute("select block from blocks where scanned=0")
blocks = [i for i in dbc]

for (block,) in blocks:
    try:
        scan_block(block)
        dbc = db.cursor()
        dbc.execute("update blocks set scanned=1 where block=?", (block,))
        db.commit()
    except:
        pass
