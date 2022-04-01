from __future__ import annotations
from .location import Location, Locations
from typing import Optional, Dict, List
import pandas as pd

class School(Location):
    code: Optional[int]
    funding: str
    level: str
    opening_year: Optional[int]
    gender: str

    def __init__(self, name: str, **kwargs):
        fields = ["lat", "lon", "shape", "code", "funding", "opening_year", "gender"]
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
        "Gender": "gender",
    }

    def __init__(self, *schools: School):
        super().__init__(*schools)

    @staticmethod
    def get(blanks=False) -> Schools:
        print("Retrieving 'Schools' from Sheets...")
        raw_schools_df = Locations.get_sheet("Schools")
        print("Retrieved.")
        if blanks:
            schools_dict = raw_schools_df.to_dict("records")
        else:
            schools_dict = raw_schools_df[raw_schools_df.Latitude != 0].to_dict("records")
        schools: List[School] = []
        for school_dict in schools_dict:
            name = school_dict["Name"]
            info = Schools._field_map(school_dict)
            level = info["level"]
            if level == "Primary":
                schools.append(PrimarySchool(name, **info))
            elif level == "Secondary":
                schools.append(SecondarySchool(name, **info))
            elif level == "Tertiary":
                schools.append(TertiarySchool(name, **info))
        return Schools(*schools)

    @staticmethod
    def _field_map(d: Dict) -> Dict:
        for old_field, new_field in Schools._FIELD_MAP.items():
            d[new_field] = d[old_field]
            d.pop(old_field)
        return d