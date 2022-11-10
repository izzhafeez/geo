from __future__ import annotations
from os.path import dirname, join
from typing import Any, Callable, Dict, List, Optional

from shapely.geometry import Polygon
import pandas as pd
import pickle

from .location import Location, Locations
from ..geom.shape import Shape

class Mall(Location):
    """
    Object to encapsulate a Mall in Singapore

    Fields:
        floors (Optional[int]): the number of floors in the mall, exclusive of parking and residential floors.
        stores (Optional[int]): the number of stores in the mall, decided based on the mall directory.
        opening_year (Optional[int]): the year the mall opened.
            This is based on the current name of the mall, so Funan and KINEX count as 2019.
        retail_area (Optional[float]): the total retail space available in the mall.
            This only includes shop space and not walkways and escalators etc.
    """
    floors: Optional[int]
    stores: Optional[int]
    opening_year: Optional[int]
    retail_area: Optional[float]

    def __init__(self, name: str, **kwargs):
        fields = ["lat", "lon", "shape", "floors", "stores", "opening_year", "retail_area", "planning_area"]
        self._try_setter(fields, kwargs)
        super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)

class Malls(Locations):
    _FIELD_MAP = {
        "Latitude": "lat",
        "Longitude": "lon",
        "Floors": "floors",
        "Stores": "stores",
        "Opening year": "opening_year",
        "Area": "retail_area",
        "shape": "shape",
    }

    def __init__(self, *malls: Mall, name: str="mall"):
        super().__init__(*malls, name=name)

    @staticmethod
    def get(blanks: bool=False, offline: bool=True) -> Malls:
        raw_df = Malls._get_data_handler(offline)
        data_dict = Malls._get_data_cleaning(blanks)(raw_df)
        malls = Malls._get_data_compiling(data_dict)
        return Malls(*malls)

    @staticmethod
    def _get_data_handler(offline: bool) -> pd.DataFrame:
        if offline:
            return pd.read_csv(join(dirname(__file__), "assets/malls.csv"))
        print("Retrieving 'Malls Raw' from Sheets...")
        raw_df = Locations.get_sheet("Malls Raw")
        print("Retrieved.")
        return raw_df

    @staticmethod
    def _get_data_cleaning(blanks: bool) -> Callable[[pd.DataFrame], Dict[str, Any]]:
        if blanks:
            return lambda df: df.set_index("Name").to_dict("index")
        return lambda df: df[pd.notna(df.Floors)
                             & pd.notna(df.Stores)
                             & pd.notna(df.Area)].set_index("Name").to_dict("index")
    
    @staticmethod
    def _get_data_compiling(data_dict: Dict[str, Any]) -> List[Mall]:
        malls: List[Mall] = []
        with open(join(dirname(__file__), "assets/mall_shapes.pickle"), 'rb') as f:
            mall_shapes_dict: Dict[str, Polygon] = pickle.load(f)
        for name, info in data_dict.items():
            shape = Shape.from_polygon(mall_shapes_dict.get(name))
            info["shape"] = shape
            malls.append(Mall(name, **Malls._field_map(info)))
        return malls

    @staticmethod
    def _field_map(d: Dict[str, Any]) -> Dict[str, Any]:
        for old_field, new_field in Malls._FIELD_MAP.items():
            d[new_field] = d.pop(old_field)
        return d
