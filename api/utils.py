from functools import lru_cache
import math
import os
import sqlite3
from typing import Union

import pandas as pd


def create_db(db_name: str) -> sqlite3.Connection:
    """
    Creates a database if it doesn't already exist, returns a connection to the
    database once created or if it exists
    """
    if not os.path.exists(db_name):
        print("Creating database")
    else:
        print("Database already exits")
    return sqlite3.connect(db_name)


def connect_to_db(filename: str, debug: bool = True) -> sqlite3.Connection:
    """
    Returns a connection to the given database. If debug is true, then the
    row factory used is a list of dicts (which each represent a row in the
    database). Use debug false when used in production as the sqlite3.Row
    factory is highly optimized.
    """
    conn = sqlite3.connect(filename)
    if debug:
        # easier to debug during development
        conn.row_factory = dict_factory
    else:
        # sqlite3.Row is highly-optimized as a row factory
        conn.row_factory = sqlite3.Row
    return conn


@lru_cache
def get_all_locations(conn: sqlite3.Connection) -> list:
    """
    Get every location in the database
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
    ON z.id = a.zip_code_id;
    """
    with conn:
        results = conn.execute(query).fetchall()
    return results


@lru_cache
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
        "hse_nbr",
        "hse_frac_nbr",
        "hse_dir_cd",
        "str_nm",
        "str_sfx_cd",
        "str_sfx_dir_cd",
        "unit_range",
    ]
    return " ".join(val.title() for key, val in d_copy.items() if key in keys)


def get_all_model_data(conn: sqlite3.Connection) -> list:
    """"""
    query = """
    SELECT *
    FROM model_data;
    """
    with conn:
        results = conn.execute(query).fetchall()
    return results


def get_closest_match(conn: sqlite3.Connection, location: tuple) -> tuple:
    """"""
    distances = [
        (distance(location, (datum["Start_Lat"], datum["Start_Lng"])), datum)
        for datum in get_all_model_data(conn)
    ]
    return sorted(distances, key=lambda e: e[0])[0]


def distance(loc1: tuple, loc2: tuple, units: str = "imperial") -> float:
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

    d = math.sin(theta / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * (
        math.sin(phi / 2) ** 2
    )
    d = 2 * math.asin(math.sqrt(d))

    earth_radius = {"metric": 6371, "imperial": 3956}
    d *= earth_radius[units]
    return d


def find_nearest_location(conn: sqlite3.Connection, location: tuple) -> tuple:
    """
    Returns the distance to and the location that is nearest to the given
    latitude-longitude tuple and the distance to that location.
    """
    # 1. get all locations
    # 2. calculate the distance between the location and the address
    #    store result in list
    # 3. sort list ascending by distance
    # 4. return first result
    distances = (
        (distance(location, (loc["lat"], loc["lon"])), loc)
        for loc in get_all_locations(conn)
    )
    return sorted(distances, key=lambda e: e[0])[0]


def construct_sample(
    location_data: pd.DataFrame, weather_data: pd.DataFrame, time_data: "datetime"
) -> pd.DataFrame:
    """
    Constructs a sample for making a prediction
    """
    location_columns = [
        'Start_Lat',
        'Start_Lng',
        'Junction',
        'Railway',
        'Station',
        'Turning_Loop'
    ]
    weather_columns = [
        'Temperature(F)',
        'Humidity(%)',
        'Pressure(in)',
        'Wind_Speed(mph)',
        'Precipitation(in)',
    ]
    time_columns = [
        'Start_Month',
        'Start_Hour',
        'Start_Day_0',
        'Start_Day_1',
        'Start_Day_2',
        'Start_Day_3',
        'Start_Day_4',
        'Start_Day_5',
        'Start_Day_6'
    ]
    columns = [*location_columns, *weather_columns, *time_columns]
    sample = pd.DataFrame(index=weather_data.index, columns=columns)
    sample[location_columns] = location_data[location_columns]
    # add weather data, probably using apply
    sample[weather_columns] = None
    weekdays = {
        0: [1, 0, 0, 0, 0, 0, 0],
        1: [0, 1, 0, 0, 0, 0, 0],
        2: [0, 0, 1, 0, 0, 0, 0],
        3: [0, 0, 0, 1, 0, 0, 0],
        4: [0, 0, 0, 0, 1, 0, 0],
        5: [0, 0, 0, 0, 0, 1, 0],
        6: [0, 0, 0, 0, 0, 0, 1],
    }
    start_month = time_data.month
    start_day = time_data.weekday()
    start_hour = time_data.hour

    sample[time_columns] = start_month, start_hour, *weekdays[start_day]



    return sample
