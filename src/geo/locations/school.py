from __future__ import annotations
from os.path import dirname, join
from typing import Any, Callable, Dict, List, Optional

from shapely.geometry import Polygon
import pandas as pd
import pickle

from .location import Location, Locations
from ..geom.shape import Shape

class School(Location):
    """
    Object to encapsulate a school in Singapore.

    Fields:
        code (Optional[int]): the code number assigned to the school, usually a 4 digit number.
        funding (str): whether the school is government funded etc.
        level (str): whether the school is Primary, Secondary or Tertiary level.
        opening_year (Optional[int]): the year the school was opened.
            If the school has been renamed/merged, choose that year instead.
        gender (str): whether the school is mixed, girls or boys.
    """
    code:         Optional[int]
    funding:      str
    level:        str
    opening_year: Optional[int]
    gender:       str

    def __init__(self, name: str, **kwargs):
        fields = ["lat", "lon", "shape", "code", "funding", "level", "opening_year", "gender"]
        self._try_setter(fields, kwargs)
        super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)

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
        "shape": "shape",
    }

    def __init__(self, *schools: School, name="school"):
        super().__init__(*schools, name=name)

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
    def _get_data_cleaning(blanks: bool) -> Callable[[pd.DataFrame], List[Dict[str, Any]]]:
        if blanks:
            return lambda df: df.to_dict("records")
        def clean_df(df):
            filtered_df: pd.DataFrame = df[df.Latitude != 0]
            return filtered_df.to_dict("records")
        return clean_df

    @staticmethod
    def _get_data_compiling(data_dict: List[Dict[str, Any]]) -> List[School]:
        schools: List[School] = []
        with open(join(dirname(__file__), "assets/school_shapes.pickle"), 'rb') as f:
            school_shapes_dict: Dict[str, Polygon] = pickle.load(f)
        for school_info in data_dict:
            name = school_info["Name"]
            shape = Shape.from_polygon(school_shapes_dict.get(name))
            school_info["shape"] = shape
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
    def _field_map(d: Dict[str, Any]) -> Dict[str, Any]:
        for old_field, new_field in Schools._FIELD_MAP.items():
            d[new_field] = d.pop(old_field)
        return d