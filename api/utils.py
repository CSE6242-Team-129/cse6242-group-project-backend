import ast
import csv
import json
import os
import sqlite3

import pandas as pd


def load_data(filename, headers: bool=True) -> list:
    """
    Load the data from the given CSV file

    Params
    ------
    filename: the name of the CSV file
    headers (bool): indicates if the CSV file has headers (True) or not (False)

    Returns
    -------
    (list): a list of the data in the CSV file
    """
    with open(filename, 'r') as f:
        if headers:
            reader = csv.DictReader(f)
        else:
            reader = csv.reader(f)
        return  [row for row in reader]


def extract_lat_lon(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts the latitude and longitude from the 'Location' key the given
    DataFrame and puts them into their own columns named 'Latitude' and
    'Longitude', respectively

    """
    def to_tuple(row):
        d = ast.literal_eval(row)
        return d['latitude'], d['longitude']

    # adapted from:
    # https://gist.github.com/sammatuba/70269c2b5268a83344f5de609ea9b3cc
    # Line 19
    df[['latitude', 'longitude']] = pd.DataFrame(
        df.location.apply(lambda r: to_tuple(r)).tolist(), index=df.index
    )

    df.latitude = df.latitude.astype(float)
    df.longitude = df.longitude.astype(float)
    return df


def transform_date_time(df: pd.DataFrame) -> pd.DataFrame:
    """"""
    suffix = 'T00:00:00.000'
    def get_date(row: str):
        return row.removesuffix(suffix)

    df['date_occurred'] = pd.DataFrame(
        df['date_occurred'].apply(lambda r: get_date(r)).tolist(), index=df.index
    )
    return df


def change_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """"""
    df.columns = [
        old_col_name.replace(' ', '_').replace('(', '').replace(')', '').lower()
        for old_col_name in df.columns
    ]

    return df


def clean_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """"""
    def trim_ws(row):
        return ' '.join(str(row).split()).title()


    df.address = pd.DataFrame(
        df.address.astype(str).apply(lambda r: trim_ws(r))
    )
    df.cross_street = pd.DataFrame(
        df.cross_street.astype(str).apply(lambda r: trim_ws(r))
    )
    return df


def load_df(filename, headers: bool=True) -> pd.DataFrame:
    """"""
    data =load_data(filename, headers)
    df = pd.DataFrame(data)
    return df


def create_db(db_name: str) -> sqlite3.Connection:
    """"""
    if not os.path.exists(db_name):
        print('Creating database')
    else:
        print('Database already exits')
    return sqlite3.connect(db_name)


def connect_to_db(filename: str) -> sqlite3.Connection:
    """"""
    conn = sqlite3.connect(filename)
    conn.row_factory = sqlite3.Row
    return conn


def create_table(conn: sqlite3.Connection) -> sqlite3.Connection:
    """"""
    schema = """CREATE TABLE accidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zipcode VARCHAR(5),
        latitude DOUBLE,
        longitude DOUBLE,
        area_name TEXT,
        area_id INTEGER,
        street TEXT,
        cross_street TEXT,
        time
    );
    """
    conn.execute(schema)
    return conn


def insert_data(conn: sqlite3.Connection, data: list) -> sqlite3.Connection:
    """"""
    query = """INSERT INTO accidents (zipcode, latitude, longitude, area_name)
    VALUES (:zipcode, :latitude, :longitude, :area_name);
    """
    cursor = conn.cursor()
    cursor.executemany(query, data)
    conn.commit()
    cursor.close()
    return conn


def get_random_entries(conn: sqlite3.Connection, limit: int) -> list:
    """"""
    cursor = conn.cursor()
    results = cursor.execute(f"""SELECT *
    FROM accidents
    ORDER BY RANDOM()
    LIMIT ?;
    """, [limit])
    # adapted from:
    # https://nickgeorge.net/programming/python-sqlite3-extract-to-dictionary/
    return [
        {k: item[k] for k in item.keys()}
        for item in results.fetchall()
    ]
