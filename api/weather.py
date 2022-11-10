from collections import namedtuple
from dataclasses import dataclass
from functools import lru_cache

from meteostat import Hourly, Point, units

import utils


LA_STATIONS = [
    {
        "country": "US",
        "id": "72295",
        "identifiers": {
            "icao": "KLAX",
            "national": None,
            "wmo": "72295"
        },
        "inventory": {
            "daily": {
                "end": "2022-11-03",
                "start": "1944-01-01"
            },
            "hourly": {
                "end": "2022-11-09",
                "start": "1944-01-01"
            },
            "model": {
                "end": "2022-11-18",
                "start": "2018-01-28"
            },
            "monthly": {
                "end": 2022,
                "start": 1944
            },
            "normals": {
                "end": 2020,
                "start": 1961
            }
        },
        "location": {
            "elevation": 38,
            "latitude": 33.9333,
            "longitude": -118.3833
        },
        "name": {
            "en": "Los Angeles Airport"
        },
        "region": "CA",
        "timezone": "America/Los_Angeles"
    },
    {
        "country": "US",
        "id": "KCQT0",
        "identifiers": {
            "icao": "KCQT",
            "national": None,
            "wmo": None
        },
        "inventory": {
            "daily": {
                "end": "2022-04-24",
                "start": "2000-01-01"
            },
            "hourly": {
                "end": "2022-11-09",
                "start": "2000-01-01"
            },
            "model": {
                "end": "2022-11-18",
                "start": "2021-01-01"
            },
            "monthly": {
                "end": 2021,
                "start": 2000
            },
            "normals": {
                "end": 1990,
                "start": 1961
            }
        },
        "location": {
            "elevation": 56,
            "latitude": 34.0167,
            "longitude": -118.2833
        },
        "name": {
            "en": "Los Angeles / Jefferson"
        },
        "region": "CA",
        "timezone": "America/Los_Angeles"
    },
    {
        "country": "US",
        "id": "KWHP0",
        "identifiers": {
            "icao": "KWHP",
            "national": None,
            "wmo": None
        },
        "inventory": {
            "daily": {
                "end": None,
                "start": None
            },
            "hourly": {
                "end": "2022-11-09",
                "start": "2006-01-01"
            },
            "model": {
                "end": "2022-11-18",
                "start": "2021-01-02"
            },
            "monthly": {
                "end": None,
                "start": None
            },
            "normals": {
                "end": 1990,
                "start": 1961
            }
        },
        "location": {
            "elevation": 306,
            "latitude": 34.2593,
            "longitude": -118.4134
        },
        "name": {
            "en": "Los Angeles / Pacoima"
        },
        "region": "CA",
        "timezone": "America/Los_Angeles"
    }
]


@dataclass
class Station:
    """
    Class representing a weather station used by Meteostat
    """
    location: dict
    name: str
    id: str
    inventory: dict

    def distance(self, point: tuple) -> float:
        """
        Calculates the distance (km) from the given point to the station

        Args
        ----
        point (tuple): tuple of coordinates (latitude, longitude) of the point

        Returns
        -------
        (float) distance (km) from the given point to the station
        """
        return utils.distance(point, self.coordinates)

    @property
    def coordinates(self) -> tuple:
        """
        Returns the coordinates (latitude, longitude) of the station as tuple
        """
        return self.location['lat'], self.location['lon']

    @staticmethod
    def from_dict(d: dict) -> 'Station':
        loc = d['location']
        location = {
            'lat': loc['latitude'],
            'lon': loc['longitude'],
            'alt': loc['elevation']
        }
        return Station(
            location=location,
            name=d['name'],
            id=d['id'],
            inventory=d['inventory']
        )

    def __repr__(self) -> str:
        return f'<Station name={self.name}>'

@lru_cache
def get_hourly_data(location: tuple, period: tuple) -> 'pd.DataFrame':
    """"""
    lat, lon, alt = location
    start, end = period
    loc = Point(lat=lat, lon=lon, alt=alt)
    data = Hourly(loc=loc, start=start, end=end).convert(units.imperial).fetch()
    data.pres = data.pres.apply(lambda r: hpa_to_psi(r), axis=1)
    return data


def hpa_to_psi(r: float) -> float:
    """
    Converts the pressure data from hPa to PSI.
    """
    conversion = 0.014503773773020924
    return r * conversion


def find_closest_station(stations: list, location: tuple) -> list:
    """
    Finds the station that is closest to the given location

    Args
    ----
    stations (list): list of stations
    location (tuple): coordinate (latitude, longitude) of the given location

    Returns
    -------
    (tuple) the distance, the closest station
    """
    return sorted([
        (station.distance(location), station)
        for station in stations
    ], key=lambda e: e[0])[0]


def get_la_stations():
    """
    Get all Stations in Los Angeles
    """
    return [Station.from_dict(s) for s in LA_STATIONS]


if __name__ == '__main__':
    # connection = utils.connect_to_db('api/locations.db')
    connection = utils.connect_to_db('locations.db')
    eagle_rock = utils.get_locations_by_zip(connection, '90041')
    stations = [Station.from_dict(s) for s in LA_STATIONS]
    stations[0].distance((eagle_rock[0]['lat'], eagle_rock[0]['lon']))
    distances = [
        (station.distance((er['lat'], er['lon'])), er, station)
        for station in stations
        for er in eagle_rock
    ]
    # print()
    import random
    loc = random.choice(eagle_rock)
    closest = find_closest_station(stations, (loc['lat'], loc['lon']))

    print(closest)
