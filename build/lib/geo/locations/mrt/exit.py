from __future__ import annotations
from os.path import dirname, join
from typing import Callable, Dict, List

import geopandas as gpd
import pandas as pd

from ...locations.location import Location, Locations

class Exit(Location):
    """
    Encapsulates a train station exit.

    Fields:
        exit_code (str): the code given to the station exit.
    """
    exit_code: str

    def __init__(self, name: str, **kwargs):
        fields = ["lat", "lon", "shape", "exit_code"]
        self._try_setter(fields, kwargs)
        super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)

class Exits(Locations):
    _FIELD_MAP = {
        "EXIT_CODE_": "exit_code",
    }

    def __init__(self, *exits: Exit, name: str="exit"):
        super().__init__(*exits, name=name)

    @staticmethod
    def get(blanks: bool=False, offline: bool=True) -> Exits:
        raw_df = Exits._get_data_handler(offline)
        data_dict = Exits._get_data_cleaning(blanks)(raw_df)
        exits = Exits._get_data_compiling(data_dict)
        return Exits(*exits)

    @staticmethod
    def _get_data_handler(offline: bool) -> pd.DataFrame:
        raw_df = gpd.read_file(join(dirname(__file__), "assets/Train_Station_Exit_Layer.shp"))
        raw_df["geometry"] = raw_df.geometry.to_crs(epsg=4326)
        return raw_df

    @staticmethod
    def _get_data_cleaning(blanks: bool) -> Callable[[pd.DataFrame], Dict]:
        return lambda df: df.to_dict("index")
    
    @staticmethod
    def _get_data_compiling(data_dict: Dict) -> List[Exit]:
        exits: List[Exit] = []
        for name, info in data_dict.items():
            exits.append(Exit(name, **Exits._field_map(info)))
        return exits

    @staticmethod
    def _field_map(d: Dict) -> Dict:
        for old_field, new_field in Exits._FIELD_MAP.items():
            d[new_field] = d[old_field]
            d.pop(old_field)
        d["lat"] = d["geometry"].y
        d["lon"] = d["geometry"].x
        return d