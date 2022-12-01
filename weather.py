from collections import namedtuple
from functools import lru_cache
import os

from dotenv import load_dotenv
import pandas as pd
import pyowm

from utils import cache_maintainer


# load the OpenWeatherMap API key
load_dotenv()


owm = pyowm.OWM(os.environ.get("OWM_API_KEY"))
owm_mgr = owm.weather_manager()
City = namedtuple("City", ["id", "lat", "lon"])
los_angeles = City(id=5368361, lat=34.052231, lon=-118.243683)


@cache_maintainer(3600)  # cache for one hour
@lru_cache(maxsize=1000)
def get_weather_by_lat_lon(lat, lon, type_="pd") -> pd.DataFrame:
    """ """
    if type_ not in ["dict", "pd"]:
        raise ValueError(f"type_ must be either 'pd' or 'dict', not '{type_}'")

    weather = owm_mgr.one_call(lat=lat, lon=lon, units="imperial").current
    temperature = weather.temp["temp"]  # fahrenheit
    humidity = weather.humidity  # in %
    pressure_conversion = 0.014503773773020924
    pressure = (
        weather.barometric_pressure("hPa")["press"] * pressure_conversion
    )  # in hPa
    wind_speed = weather.wind("miles_hour")["speed"]  # in mph
    if weather.rain:
        precipitation = weather.rain["3h"]  # inches
    else:
        precipitation = 0

    if type_ == "pd":
        columns = [
            "Temperature(F)",
            "Humidity(%)",
            "Pressure(in)",
            "Wind_Speed(mph)",
            "Precipitation(in)",
        ]
        weather_df = pd.DataFrame(columns=columns, index=[0])
        weather_df[columns] = temperature, humidity, pressure, wind_speed, precipitation
        return weather_df
    elif type_ == "dict":
        return {
            "Temperature(F)": temperature,
            "Humidity(%)": humidity,
            "Pressure(in)": pressure,
            "Wind_Speed(mph)": wind_speed,
            "Precipitation(in)": precipitation,
        }


@cache_maintainer(3600)  # cache for one hour
@lru_cache(maxsize=1000)
def get_weather_by_zip(zip_code: str, type_="pd") -> pd.DataFrame:
    """ """
    if type_ not in ["dict", "pd", "tuple"]:
        raise ValueError(f"type_ must be either 'pd' or 'dict', not '{type_}'")

    weather = owm_mgr.weather_at_zip_code(zip_code, country="US").weather
    temperature = weather.temperature("fahrenheit")["temp"]
    humidity = weather.humidity  # in %
    pressure_conversion = 0.014503773773020924
    pressure = (
        weather.barometric_pressure("hPa")["press"] * pressure_conversion
    )  # in hPa
    wind_speed = weather.wind("miles_hour")["speed"]  # in mph
    if weather.rain:
        precipitation = weather.rain["3h"]  # inches
    else:
        precipitation = 0

    if type_ == "pd":
        columns = [
            "Temperature(F)",
            "Humidity(%)",
            "Pressure(in)",
            "Wind_Speed(mph)",
            "Precipitation(in)",
        ]
        weather_df = pd.DataFrame(columns=columns, index=[0])
        weather_df[columns] = temperature, humidity, pressure, wind_speed, precipitation
        return weather_df
    elif type_ == "dict":
        return {
            "Temperature(F)": temperature,
            "Humidity(%)": humidity,
            "Pressure(in)": pressure,
            "Wind_Speed(mph)": wind_speed,
            "Precipitation(in)": precipitation,
        }
    elif type_ == "tuple":
        return temperature, humidity, pressure, wind_speed, precipitation


@cache_maintainer(3600)  # cache for one hour
@lru_cache(maxsize=1000)
def get_la_weather(type_: str = "pd"):
    """"""
    if type_ not in ["dict", "pd", "tuple"]:
        raise ValueError(f"type_ must be either 'pd' or 'dict', not '{type_}'")

    weather = (owm_mgr
        .forecast_at_id(los_angeles.id, interval="3h", limit=1)
        .forecast
        .weathers[0])
    temperature = weather.temperature("fahrenheit")["temp"]
    humidity = weather.humidity  # in %
    pressure_conversion = 0.014503773773020924
    pressure = (
        weather.barometric_pressure("hPa")["press"] * pressure_conversion
    )  # in hPa
    wind_speed = weather.wind("miles_hour")["speed"]  # in mph
    if weather.rain:
        precipitation = weather.rain["3h"]  # inches
    else:
        precipitation = 0

    if type_ == "pd":
        columns = [
            "Temperature(F)",
            "Humidity(%)",
            "Pressure(in)",
            "Wind_Speed(mph)",
            "Precipitation(in)",
        ]
        weather_df = pd.DataFrame(columns=columns, index=[0])
        weather_df[columns] = temperature, humidity, pressure, wind_speed, precipitation
        return weather_df
    elif type_ == "dict":
        return {
            "Temperature(F)": temperature,
            "Humidity(%)": humidity,
            "Pressure(in)": pressure,
            "Wind_Speed(mph)": wind_speed,
            "Precipitation(in)": precipitation,
        }
    elif type_ == "tuple":
        return temperature, humidity, pressure, wind_speed, precipitation
