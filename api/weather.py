from functools import lru_cache
import warnings

from meteostat import Hourly, Stations, units
import pandas as pd


# meteostat catches exceptions if a path cannot be loaded and
# issues a warning instead, leaving us without a way of knowing
# this without directly checking the returned data. this should
# allow us to capture the warnings as if they are exceptions. see
#
warnings.filterwarnings("error")


# @lru_cache
def get_hourly_data(location: tuple, period: tuple) -> "pd.DataFrame":
    """"""
    start, end = period
    # find the closest station
    # adapted from: https://dev.meteostat.net/python/stations.html#example
    station = Stations().nearby(*location).fetch(5)
    # adapted from:
    # https://dev.meteostat.net/python/api/timeseries/interpolate.html#examples
    data = (
        Hourly(station, start=start, end=end)
        .normalize()
        .interpolate()
        .convert(units.imperial)
        .fetch()
    )
    # convert hPa to PSI
    pressure_conversion = 0.014503773773020924
    speed_conversion = 0.6213711922
    data.pres = data.pres.apply(lambda r: r * pressure_conversion)
    data.wspd = data.wspd.apply(lambda r: r * speed_conversion)
    data = transform_data(data)
    return data


def transform_data(data: pd.DataFrame) -> pd.DataFrame:
    """"""
    wc = {
        'temp': 'Temperature(F)',
        'rhum': 'Humidity(%)',
        'pres': 'Pressure(in)',
        'wspd': 'Wind_Speed(mph)',
        'prcp': 'Precipitation(in)'
    }
    wdata = data.rename(columns=wc)
    wdata = pd.DataFrame(wdata[list(wc.values())])
    return wdata