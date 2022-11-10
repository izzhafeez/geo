from __future__ import annotations
from os.path import join, dirname
from typing import Any, Callable, Dict, List, Optional, Tuple

import geopandas as gpd
import pandas as pd

from structures.kdtree import KDTree
from .connection import Connection
from .exit import Exits
from .platform import Platform
from .platform_code import PlatformCode
from ..location import Location, Locations

class Station(Location):
    """
    Station in the MRT network.
    """
    platforms: List[Platform]
    abbr: Optional[str]
    address: Optional[str]
    postcode: Optional[str]
    chinese: Optional[str]
    
    def __init__(self, name: str, platforms: List[Platform], **kwargs):
        fields = ["lat", "lon", "shape", "abbr", "address", "postcode", "chinese"]
        self._try_setter(fields, kwargs)
        super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)
        self.platforms = platforms

class Stations(Locations):
    stations_by_year: KDTree[Location]

    _FIELD_MAP = {
        "Abbreviation": "abbr",
        "Opening Year": "opening_year",
        "Address": "address",
        "Postcode": "postcode",
        "Lat": "lat",
        "Long": "lon",
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
    def get(blanks: bool=True, offline: bool=True) -> Stations:
        raw_df = Stations._get_data_handler(offline)
        data_dict = Stations._get_data_cleaning(blanks)(raw_df)
        stations = Stations._get_data_compiling(data_dict)
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
    def _get_data_compiling(data_dict: List[Dict[str, Any]]) -> List[Station]:
        station_platforms: Dict[str, List[Platform]] = {}
        station_infos: Dict[str, Dict[str, Any]] = {}
        stations: List[Station] = []
        
        for platform_info in data_dict:
            name = platform_info["Name"]
            platform_code = PlatformCode(platform_info["Label"])
            platform_info = Stations._field_map(platform_info)
            platform_info["platform_code"] = platform_code
            # lat = platform_info.get("lat")
            # lon = platform_info.get("lon")
            # opening_year = platform_info.get("opening_year")
            # closing_year = platform_info.get("closing_year")
            # platform = Platform(platform_code, opening_year, closing_year)
            platform = Platform(platform_code.code, **platform_info)
            if name not in station_platforms:
                station_platforms[name] = [platform]
                station_infos[name] = platform_info
            else:
                station_platforms[name].append(platform)
                
        for name, platforms in station_platforms.items():
            stations.append(Station(name, platforms, **station_infos[name]))
        return stations

    @staticmethod
    def _field_map(d: Dict) -> Dict:
        for old_field, new_field in Stations._FIELD_MAP.items():
            d[new_field] = d.pop(old_field)
        return d
