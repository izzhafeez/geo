from __future__ import annotations
from .location import Location, Locations
from typing import Optional, Dict, List, Callable
import pandas as pd
from os.path import join, dirname

class Mall(Location):
    floors: Optional[int]
    stores: Optional[int]
    opening_year: Optional[int]
    retail_area: Optional[float]

    def __init__(self, name: str, **kwargs):
        fields = ["lat", "lon", "shape", "floors", "stores", "opening_year", "retail_area"]
        self._try_setter(fields, kwargs)
        super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)

    def __str__(self) -> str:
        return f"<Mall: {self.name}, ({self.lat}, {self.lon})>"
    
    def __repr__(self) -> str:
        return f"<Mall: {self.name}>"

class Malls(Locations):
    _FIELD_MAP = {
        "Latitude": "lat",
        "Longitude": "lon",
        "Floors": "floors",
        "Stores": "stores",
        "Opening year": "opening_year",
        "Area": "retail_area"
    }

    def __init__(self, *malls: Mall):
        super().__init__(*malls)

    @property
    def name(self) -> str:
        return "mall"

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
    def _get_data_cleaning(blanks: bool) -> Callable[[pd.DataFrame], Dict]:
        if blanks:
            return lambda df: df.set_index("Name").to_dict("index")
        return lambda df: df[
            pd.notna(df.Floors)
            & pd.notna(df.Stores)
            & pd.notna(df.Area)].set_index("Name").to_dict("index")
    
    @staticmethod
    def _get_data_compiling(data_dict: Dict) -> List[Mall]:
        malls: List[Mall] = []
        for name, info in data_dict.items():
            malls.append(Mall(name, **Malls._field_map(info)))
        return malls

    @staticmethod
    def _field_map(d: Dict) -> Dict:
        for old_field, new_field in Malls._FIELD_MAP.items():
            d[new_field] = d[old_field]
            d.pop(old_field)
        return d
