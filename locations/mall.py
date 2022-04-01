from __future__ import annotations
from .location import Location, Locations
from typing import Optional, Dict, List
import pandas as pd

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

    @staticmethod
    def get(blanks=False) -> Malls:
        print("Retrieving 'Malls Raw' from Sheets...")
        raw_malls_df = Locations.get_sheet("Malls Raw")
        print("Retrieved.")
        if blanks:
            malls_dict = raw_malls_df.set_index("Name").to_dict("index")
        else:
            malls_dict = raw_malls_df[
                pd.notna(raw_malls_df.Floors)
                & pd.notna(raw_malls_df.Stores)
                & pd.notna(raw_malls_df.Area)].set_index("Name").to_dict("index")
        malls: List[Mall] = []
        for name, info in malls_dict.items():
            malls.append(Mall(name, **Malls._field_map(info)))
        return Malls(*malls)

    @staticmethod
    def _field_map(d: Dict) -> Dict:
        for old_field, new_field in Malls._FIELD_MAP.items():
            d[new_field] = d[old_field]
            d.pop(old_field)
        return d
