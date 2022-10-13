import masscan
import mariadb
import tqdm
import json

config = json.loads(open("/opt/scanner/config.json").read())

db = mariadb.connect(
    user=config["db_username"],
    password=config["db_passwd"],
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_dbname"]
)
def scan_block(block):
    mas= masscan.PortScanner()
    mas.scan('{}.0.0.0/8'.format(block), ports='25565', arguments='--max-rate 10000')

    for ip in tqdm.tqdm(mas.scan_result.get("scan").keys()):
        dbc = db.cursor()
        dbc.execute("insert into ips values (?, 0);", (ip,))
    db.commit()

dbc = db.cursor()
dbc.execute("select block from blocks where scanned=0")
blocks = [i for i in dbc]
allblocks =  [12,17,19,38,48,56,73,1,2,3,4,5,8,13,14,15,16,18,20,24,25,27,31,32,34,39,40,41,42,43,44,46,50,51,52,53,54,57,58,59,60,61,62,63,64,65,66,68,69,70,71, 72, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85,86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 128, 129, 130, 131,132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 216, 217, 218, 219, 220, 221, 222, 223]

if len(blocks) == 0:
    print("Inserting blocks")
    for block in allblocks:
        dbc = db.cursor()
        dbc.execute("insert into blocks values (?, 0);", (block,))
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
    except masscan.NetworkConnectionError as e:
        print(e)
