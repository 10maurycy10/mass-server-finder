#!/bin/sh
while true ; do 
echo "Waiting"
sleep 30
echo "Pinging"
python3 ping.py
echo "Parsing"
python3 parse.py
done
