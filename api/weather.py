from functools import lru_cache

from meteostat import Hourly, Stations, units


@lru_cache
def get_hourly_data(location: tuple, period: tuple) -> "pd.DataFrame":
    """"""
    start, end = period
    # find the closest station
    # adapted from: https://dev.meteostat.net/python/stations.html#example
    station = Stations().nearby(*location).fetch(1)
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
    conversion = 0.014503773773020924
    data.pres = data.pres.apply(lambda r: r * conversion)
    return data
