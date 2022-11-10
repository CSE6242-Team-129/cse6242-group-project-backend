import math
import os
import sqlite3
from typing import Union


def create_db(db_name: str) -> sqlite3.Connection:
    """"""
    if not os.path.exists(db_name):
        print("Creating database")
    else:
        print("Database already exits")
    return sqlite3.connect(db_name)


def connect_to_db(filename: str, debug: bool=True) -> sqlite3.Connection:
    """"""
    conn = sqlite3.connect(filename)
    if debug:
        # easier to debug during development
        conn.row_factory = dict_factory
    else:
        # sqlite3.Row is highly-optimized as a row factory
        conn.row_factory = sqlite3.Row
    return conn


def get_locations_by_zip(conn: sqlite3.Connection, zip_code: Union[str, int]) -> list:
    """
    Query locations by zip code.

    Args
    ----
    conn (sqlite3.Connection): connection to the database
    zip_code (str|int): the zip code to query by.

    Returns
    (list[dict]): list of dicts of the result of the query.
    """
    query = """
    SELECT
        a.hse_nbr,
        a.hse_frac_nbr,
        a.hse_dir_cd,
        a.str_nm,
        a.str_sfx_cd,
        a.str_sfx_dir_cd,
        a.unit_range,
        a.lat,
        a.lon,
        z.zip_code
    FROM addresses AS a
    JOIN zip_codes AS z
    ON z.id = a.zip_code_id
    WHERE z.zip_code = ?;
    """
    with conn:
        result = conn.execute(query, [zip_code]).fetchall()
    return result



def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
    """
    Converts a sqlite3.Row object to a dictionary. Use this when debugging.
    Adapted from:
    https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory

    Args
    ----
    cursor (sqlite3.Cursor): the SQLite database cursor
    row (sqlite3.Row): the row resulting from the query

    Returns
    -------
    (dict): a dictionary of the result
    """
    col_names = [col[0] for col in cursor.description]
    return {key: value for key, value in zip(col_names, row)}


def construct_address(d: dict) -> str:
    """
    Constructs and address from a row in the 'addresses' table

    Args
    ----
    d (dict): the dictionary of the address to be constructed. Example:
        {
            'hse_nbr': 388,
            'hse_frac_nbr': None,
            'hse_dir_cd': 'W',
            'str_nm': 'AVENUE 45',
            'str_sfx_cd': None,
            'str_sfx_dir_cd': None,
            'unit_range': None,
            'lat': 34.09968,
            'lon': -118.21117,
            'zip_code': '90065'
        }

    Returns
    (str) the constructed address. From the example given above,
        '388 W Avenue 45'
    """
    d_copy = {key: str(val) for key, val in d.items() if not val is None}
    keys = [
        'hse_nbr', 'hse_frac_nbr', 'hse_dir_cd', 'str_nm',
        'str_sfx_cd', 'str_sfx_dir_cd', 'unit_range'
    ]
    return ' '.join(
        val.title() for key, val in d_copy.items()
        if key in keys
    )


def distance(loc1: tuple, loc2: tuple, units: str='imperial') -> float:
    """
    Calculates the distance from the given point to the station

    Args
    ----
    loc1 (tuple): tuple of coordinates (latitude, longitude) of the point
    loc2 (tuple): tuple of coordinates (latitude, longitude) of the point
    units (str): what system to use, imperial (default) or metric

    Returns
    -------
    (float) distance from the given point to the station
    adapted from:
    https://www.geeksforgeeks.org/program-distance-two-points-earth/
    """
    lat1, lon1 = math.radians(loc1[0]), math.radians(loc1[1])
    lat2, lon2 = math.radians(loc2[0]), math.radians(loc2[1])

    phi = lon2 - lon1
    theta = lat2 - lat1

    d = (math.sin(theta / 2)**2 +
         math.cos(lat1) * math.cos(lat2) * (math.sin(phi / 2)**2))
    d = 2 * math.asin(math.sqrt(d))


    earth_radius = {'metric': 6371, 'imperial': 3956}
    d *= earth_radius[units]
    return d
