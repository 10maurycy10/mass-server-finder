#!/bin/sh
mariadb minecraft < init.sql
python3 add_blocks.sh
