import mariadb
import tqdm
import json
import typing as t
import matplotlib.pyplot as plt

config = json.loads(open("config.json").read())

db = mariadb.connect(
    user=config["db_username"],
    password=config["db_passwd"],
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_dbname"]
)

def get_count(block):
    dbc = db.cursor()
    dbc.execute("select count(*) from ips where ip like ?", ("{}.%.%.%".format(block),));
    return [i for i in dbc][0][0];

counts = [get_count(block) for block in tqdm.tqdm(range(256))]
arr = [i for i in range(256)]
for (block, count) in enumerate(counts):
    print(block, count)
plt.bar(arr,counts)
plt.show()
