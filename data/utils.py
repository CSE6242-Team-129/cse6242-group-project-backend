import ast
import csv
import zipfile

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
    df[['Latitude', 'Longitude']] = pd.DataFrame(
        df.Location.apply(lambda r: to_tuple(r)).tolist(), index=df.index
    )

    df.Latitude = df.Latitude.astype(float)
    df.Longitude = df.Longitude.astype(float)
    return df


def load_df(filename, headers: bool=True) -> pd.DataFrame:
    """"""
    data =load_data(filename, headers)
    df = pd.DataFrame(data)
    return df