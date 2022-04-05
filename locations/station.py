from __future__ import annotations
from .location import Location, Locations
from ..structures.kdtree import KDTree
from typing import Dict, List, Callable, Protocol
import pandas as pd
import geopandas as gpd
from os.path import join, dirname

class Station(Location):
    code: str

    def __init__(self, name: str, **kwargs):
        fields = ["lat", "lon", "shape", "code"]
        self._try_setter(fields, kwargs)
        super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)

class MRTStation(Station):
    def __init__(self):
        pass

class LRTStation(Station):
    def __init__(self):
        pass

class Stations(Locations):
    stations_by_year: KDTree

    _FIELD_MAP = {
        "EXIT_CODE_": "exit_code",
    }

    def __init__(self, *stations: Station, name: str="station"):
        super().__init__(*stations, name=name)

    @staticmethod
    def get(blanks: bool=False, offline: bool=True) -> Stations:
        pass

    @staticmethod
    def _get_data_handler(offline: bool) -> pd.DataFrame:
        raw_df = gpd.read_file(join(dirname(__file__), "assets/MRTLRTStnPtt.shp"))
        raw_df["geometry"] = raw_df.geometry.to_crs(epsg=4326)
        return raw_df

    @staticmethod
    def _get_data_cleaning(blanks: bool) -> Callable[[pd.DataFrame], Dict]:
        pass
    
    @staticmethod
    def _get_data_compiling(data_dict: Dict) -> List[Station]:
        pass

    @staticmethod
    def _field_map(d: Dict) -> Dict:
        for old_field, new_field in Stations._FIELD_MAP.items():
            d[new_field] = d[old_field]
            d.pop(old_field)
        d["lat"] = d["geometry"].y
        d["lon"] = d["geometry"].x
        return d
