from __future__ import annotations
from .location import Location, Locations
from typing import Optional, Dict, List, Callable
import pandas as pd
from os.path import join, dirname

class School(Location):
    code: Optional[int]
    funding: str
    level: str
    opening_year: Optional[int]
    gender: str

    def __init__(self, name: str, **kwargs):
        fields = ["lat", "lon", "shape", "code", "funding", "level", "opening_year", "gender"]
        self._try_setter(fields, kwargs)
        super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)
    
    def __str__(self) -> str:
        return f"<{self.level}School: {self.name}, ({self.lat}, {self.lon})>"
    
    def __repr__(self) -> str:
        return f"<{self.level}School: {self.name}>"

class PrimarySchool(School):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

class SecondarySchool(School):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        fields = ["exp", "na", "nt", "ip"]
        self._try_setter(fields, kwargs)

class TertiarySchool(School):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

class Schools(Locations):
    _FIELD_MAP = {
        "Latitude": "lat",
        "Longitude": "lon",
        "School Code": "code",
        "Funding": "funding",
        "Level": "level",
        "Opening Year": "opening_year",
        "Type": "gender",
    }

    def __init__(self, *schools: School):
        super().__init__(*schools)

    @property
    def name(self) -> str:
        return "school"

    @staticmethod
    def get(blanks=False, offline=True) -> Schools:
        raw_df = Schools._get_data_handler(offline)
        data_dict = Schools._get_data_cleaning(blanks)(raw_df)
        schools = Schools._get_data_compiling(data_dict)
        return Schools(*schools)

    @staticmethod
    def _get_data_handler(offline: bool) -> pd.DataFrame:
        if offline:
            return pd.read_csv(join(dirname(__file__), "assets/schools.csv"))
        print("Retrieving 'Schools' from Sheets...")
        raw_df = Locations.get_sheet("Schools")
        print("Retrieved.")
        return raw_df

    @staticmethod
    def _get_data_cleaning(blanks: bool) -> Callable[[pd.DataFrame], Dict]:
        if blanks:
            return lambda df: df.to_dict("records")
        return lambda df: df[df.Latitude != 0].to_dict("records")

    @staticmethod
    def _get_data_compiling(data_dict: Dict) -> List[School]:
        schools: List[School] = []
        for school_info in data_dict:
            name = school_info["Name"]
            info = Schools._field_map(school_info)
            level = info["level"]
            if level == "Primary":
                schools.append(PrimarySchool(name, **info))
            elif level == "Secondary":
                schools.append(SecondarySchool(name, **info))
            elif level == "Tertiary":
                schools.append(TertiarySchool(name, **info))
        return schools

    @staticmethod
    def _field_map(d: Dict) -> Dict:
        for old_field, new_field in Schools._FIELD_MAP.items():
            d[new_field] = d[old_field]
            d.pop(old_field)
        return d