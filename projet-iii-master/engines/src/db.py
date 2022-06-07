# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>

import logging
import json
import sqlite3

import pandas as pd

conn = None
curr = None

def setDB(path):
    # pylint: disable=global-statement
    global conn
    global curr
    try:
        conn = sqlite3.connect(path)
        curr  = conn.cursor()
        logging.info("using database %s", path)
    except sqlite3.OperationalError:
        logging.error("can't open database %s => fallback to memory", path)
        conn = sqlite3.connect(":memory:")
        curr  = conn.cursor()


def make_json_from_sql(query):
    logging.info("SQL: %s", query)
    return json.loads(pd.read_sql_query(query, conn).to_json(orient="records"))

def execute(*args):
    return curr.execute(*args)

def get_station_id(name):
    # pylint: disable=line-too-long
    return make_json_from_sql(f"""SELECT Code as code, name as nom FROM STATION where name like "%{name}%";""")

def get_station(code):
    if code:
        # pylint: disable=line-too-long
        query = f"SELECT distinct Code as code, name as nom, latitude as latitude, longitude as longitude FROM STATION WHERE Code = {int(code)};"
    else:
        # pylint: disable=line-too-long
        query = "SELECT distinct Code as code, name as nom, latitude as latitude, longitude as longitude FROM STATION;"
    return make_json_from_sql(query)
