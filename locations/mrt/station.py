from __future__ import annotations
from os.path import join, dirname
from typing import Any, Callable, Dict, List, Tuple

import geopandas as gpd
import pandas as pd

from structures.kdtree import KDTree
from .exit import Exits
from .platform import Platform
from .station_code import StationCode
from ..location import Location, Locations

class Station(Location):
    def __init__(self, name: str, codes: List[StationCode], **kwargs):
        fields = ["lat", "lon", "shape"]
        self._try_setter(fields, kwargs)
        super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)
        self.codes = codes

class MRTStation(Station):
    def __init__(self):
        pass

class LRTStation(Station):
    def __init__(self):
        pass

class Stations(Locations):
    stations_by_year: KDTree

    _FIELD_MAP = {
        "Abbreviation": "abbr",
        "Opening Year": "opening_year",
        "Address": "address",
        "Postcode": "postcode",
        "Lat": "lat",
        "Long": "long",
        "Closing Year": "closing_year",
        "Chinese": "chinese",
    }

    def __init__(self,
                 *stations: Station,
                 name: str="station",
                 platforms: Dict[str, Station]={}):
        super().__init__(*stations, name=name)
        self.platforms = platforms

    @staticmethod
    def get(blanks: bool=False, offline: bool=True) -> Stations:
        raw_df = Stations._get_data_handler(offline)
        data_dict = Stations._get_data_cleaning(blanks)(raw_df)
        stations, platforms = Stations._get_data_compiling(data_dict)
        return Stations(*stations)

    @staticmethod
    def _get_data_handler(offline: bool) -> pd.DataFrame:
        raw_df = pd.read_csv(join(dirname(__file__), "assets/mrt.csv"))
        return raw_df

    @staticmethod
    def _get_data_cleaning(blanks: bool) -> Callable[[pd.DataFrame], List[Dict[str, Any]]]:
        if blanks:
            return lambda df: df.to_dict("records")
        def clean_df(df):
            filtered_df: pd.DataFrame = df[pd.notnull(df.Abbreviation)
                                           & pd.notnull(df["Opening Year"])
                                           & pd.notnull(df.Address)
                                           & pd.notnull(df.Postcode)]
            return filtered_df.to_dict("records")
        return clean_df
    
    @staticmethod
    def _get_data_compiling(data_dict: List[Dict[str, Any]]) -> Tuple[List[Station], Dict[str, Station]]:
        stations:  List[Station] = []
        platforms: Dict[str, Platform] = {}
        for platform_info in data_dict:
            name = platform_info["Name"]
            platform_code = platform_info["Label"]
            platform_info = Stations._field_map(platform_info)
            station = Station(name, **platform_info)
            stations.append(station)
            platforms[platform_code] = station                
        return (stations, platforms)

    @staticmethod
    def _field_map(d: Dict) -> Dict:
        for old_field, new_field in Stations._FIELD_MAP.items():
            d[new_field] = d[old_field]
            d.pop(old_field)
        d["lat"] = d["geometry"].y
        d["lon"] = d["geometry"].x
        return d
