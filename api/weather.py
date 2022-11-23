from collections import namedtuple
from functools import lru_cache
import os
import warnings

from dotenv import load_dotenv
from meteostat import Hourly, Stations, units
import pandas as pd
import pyowm


# load the OpenWeatherMap API key
load_dotenv()
# meteostat catches exceptions if a path cannot be loaded and
# issues a warning instead, leaving us without a way of knowing
# this without directly checking the returned data. this should
# allow us to capture the warnings as if they are exceptions. see
#
warnings.filterwarnings("error")


owm = pyowm.OWM(os.environ.get("OWM_API_KEY"))
owm_mgr = owm.weather_manager()
los_angeles = (
    owm.city_id_registry()
        .ids_for("Los Angeles", country="US", matching="exact")
)[0]
City = namedtuple('City', ['id', 'name', 'country', 'state', 'lat', 'lon'])
los_angeles = City(*los_angeles)


# TODO: maybe use custom cache maintainer function found here
# https://stackoverflow.com/a/62843760

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


def get_owm_weather(lat, lon) -> pd.DataFrame:
    """
    """
    # if location:
    #     lat, lon = location
    # else:
    # lat, lon = (location) if location else los_angeles.lat, los_angeles.lon
    weather = owm_mgr.one_call(lat=lat, lon=lon, units="imperial").current
    temperature = weather.temp["temp"] # fahrenheit
    humidity = weather.humidity # in %
    pressure_conversion = 0.014503773773020924
    pressure = weather.barometric_pressure("hPa")["press"] * pressure_conversion # in hPa
    wind_speed = weather.wind("miles_hour")["speed"] # in mph
    if weather.rain:
        precipitation = weather.rain # inches
    else:
        precipitation = 0

    columns = [
        'Temperature(F)',
        'Humidity(%)',
        'Pressure(in)',
        'Wind_Speed(mph)',
        'Precipitation(in)'
    ]
    weather_df = pd.DataFrame(columns=columns, index=[0])
    weather_df[columns] = temperature, humidity, pressure, wind_speed, precipitation
    return weather_df
