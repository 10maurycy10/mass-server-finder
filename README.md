# mass server finder

A script to scan the internet and find minecraft servers.

## Configuration

The configuration file is located add ``config.json``, an example file follows.

```json

{
        "db_passwd": "testpasswordforreadmepurposes",
        "db_username": "testusername",
        "db_host": "localhost",
        "db_port": 3306,
        "db_dbname": "minecraft",
        "recheck_interval": 3500
}
```

### SQL

The code requires multiple tables in the database, the commands used to create these can be found in ``init.sql``.

## Initial scan

The ``add_blocks.py`` script can be used to insert all the networks (That are not reserved by the INAA or DOD).

Then you can run the ``scan.py`` script to begin scanning.

## Server list pinging

To preform the server list pings, run ``ping.py``, this causes a lot of errors, witch can be safely ignored.

## Parsing

To parse and insert the results of the ping, run ``parse.py`` 
