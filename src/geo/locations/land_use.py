from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Tuple
from os.path import dirname, join

import fiona
import geopandas as gpd
import pandas as pd
from tqdm import tqdm

from .location import Location, Locations
from geom.geo_pt import GeoPt
from structures.bounds_tree import BoundsTree

class LandUse(Location):
    """
    Object encapsulating the land use areas in Singapore.

    Fields:
        code (str): the code assigned to the land lot.
    """
    code: str

    def __init__(self, name: str, **kwargs):
        fields = ["lat", "lon", "shape", "code"]
        self._try_setter(fields, kwargs)
        super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)

class LandUses(Locations):
    # locations_interval_tree: IntervalTree[LandUse]
    _FIELD_MAP = {
        "geometry": "shape",
    }
    # https://data.gov.sg/dataset/sla-cadastral-land-parcel
    _PATH_TO_LAND_USES = join(dirname(__file__), "assets/sla-cadastral-land-parcel-kml.kml")

    def __init__(self, *areas: LandUse, name="lot"):
        # self.locations_interval_tree = IntervalTree[LandUse]()
        super().__init__(*areas, name=name)
        # self.locations_interval_tree.add_all([area.shape for area in areas if area.shape], [area for area in areas if area])

    @staticmethod
    def get(blanks=False, offline=True) -> LandUses:
        print("Handling...", end=" ")
        raw_df = LandUses._get_data_handler(offline)
        print("Done")
        print("Cleaning...", end=" ")
        data_dict = LandUses._get_data_cleaning(blanks)(raw_df)
        print("Done")
        print("Compiling...", end=" ")
        areas = LandUses._get_data_compiling(data_dict)
        print("Done")
        return LandUses(*areas)

    @staticmethod
    def _get_data_handler(offline: bool) -> pd.DataFrame:
        gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw" # type: ignore [no-redef]
        return gpd.read_file(LandUses._PATH_TO_LAND_USES, driver='KML')

    @staticmethod
    def _get_data_cleaning(blanks: bool) -> Callable[[pd.DataFrame], List[Dict[str, Any]]]:
        def clean_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
            extract_from_description = lambda pattern: df.Description.str.extract(pattern)
            df["Name"] = extract_from_description("<td>(.*?)</td>")
            df = df.drop("Description",axis=1)
            df = df[["Name", "geometry"]]
            return df.to_dict("records")
        return clean_data

    @staticmethod
    def _get_data_compiling(data_dict: List[Dict[str, Any]]) -> List[LandUse]:
        areas: List[LandUse] = []
        for info in tqdm(data_dict):
            name = info.pop("Name")
            areas.append(LandUse(name, **LandUses._field_map(info)))
        return areas

    @staticmethod
    def _field_map(d: Dict[str, Any]) -> Dict[str, Any]:
        for old_field, new_field in LandUses._FIELD_MAP.items():
            if new_field not in d:
                d[new_field] = d.pop(old_field)
        return d

    def get_nearest_to(self, point: GeoPt) -> Tuple[Optional[Location], float]:
        for _, location in self.locations.items():
            if location.shape and location.shape.contains(point):
                return (location, 0)
        return (None, float("inf"))
        