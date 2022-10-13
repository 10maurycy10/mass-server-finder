CREATE DATABASE IF NOT EXISTS minecraft;

USE minecraft;

create table blocks (block int, scanned bool);
create index iscanned on blocks (scanned);

create table ips (ip varchar(20), lastping int); -- All the ips returned by the port scanner, and a timestamp to avoid flooding anyone with packats.
create index ilastping on ips (lastping);

create table rawpings (data text, ip varchar(20), error bool, timestamp int); -- Raw data from server list pings.
create index oerror on rawpings (error);

create table servers (ip varchar(20), name text, cap int, online int, version text, timestamp int, modded bool); -- Parsed data from rawpings, players are stored in the players table
create index iip on servers (ip);
create index oname on servers (name);

create table players (name text, uuid varchar(256), server varchar(20), timestamp int); -- Player data from parsing the raw pings
create index iname on players (name);
create index iserver on players (server);

create table joinrecords (server varchar(20), whitelisted bool, timestamp int);
create index iserver on joinrecords (server);

create table joinplayers (server varchar(20), playername text, uuid varchar(256), timestamp int);
create index iserver on joinplayers (server, timestamp);

commit;
