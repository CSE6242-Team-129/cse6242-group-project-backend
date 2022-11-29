from datetime import datetime
from functools import lru_cache
import math
import os
import sqlite3
import time

import pandas as pd

from models import Classifier, InputData


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
    conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES)
    if debug:
        # easier to debug during development
        conn.row_factory = dict_factory
    else:
        # sqlite3.Row is highly-optimized as a row factory
        conn.row_factory = sqlite3.Row

    # convert string data to boolean, adapted from:
    # https://stackoverflow.com/a/16936992
    # sqlite3.register_adapter(str, bool)
    # sqlite3.register_converter("INTEGER", lambda s: s == "True")
    return conn


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


@lru_cache
def get_all_model_data(conn: sqlite3.Connection, type_: str = "list") -> list:
    """"""
    query = """
    SELECT
        Start_Lat,
        Start_Lng,
        Amenity,
        Bump,
        Crossing,
        Give_Way,
        Junction,
        No_Exit,
        Railway,
        Roundabout,
        Station,
        Stop,
        Traffic_Calming,
        Traffic_Signal,
        Turning_Loop,
        Zip_Code
    FROM model_data;
    """
    with conn:
        results = conn.execute(query).fetchall()

    if type_ == "pd":
        results = pd.DataFrame(results)
    return results


@lru_cache
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


def cache_maintainer(clear_time: int):
    """
    A function decorator that clears lru_cache clear_time seconds
    :param clear_time: In seconds, how often to clear cache (only checks when
    called)

    Source: https://stackoverflow.com/a/62843760
    """

    def inner(func):
        def wrapper(*args, **kwargs):
            if hasattr(func, "next_clear"):
                if time.time() > func.next_clear:
                    func.cache_clear()
                    func.next_clear = time.time() + clear_time
            else:
                func.next_clear = time.time() + clear_time

            return func(*args, **kwargs)

        return wrapper

    return inner


def get_all_zip_codes(conn: sqlite3.Connection) -> list:
    query = "SELECT zip_code FROM zip_codes;"
    with conn:
        zips = conn.execute(query).fetchall()

    return [zc['zip_code'] for zc in zips]


def make_prediction(location: pd.DataFrame, weather: pd.DataFrame, classifier: Classifier) -> pd.DataFrame:
    """"""
    columns = [
        "Temperature(F)",
        "Humidity(%)",
        "Pressure(in)",
        "Wind_Speed(mph)",
        "Precipitation(in)",
    ]
    location[columns] = weather
    location["Start_Time"] = datetime.now()
    idata = InputData(data=location)
    prediction = classifier.predict(idata.data_ohe, idata.index, type_="list")
    return prediction