from __future__ import annotations
import geopandas as gpd
import pandas as pd
import fiona
from ..geometry.pt import GeoPt
from ..structures.interval2d import IntervalTree
from shapely import geometry
from .location import Location, Locations
from typing import Callable, Dict, List, Any, Tuple
from os.path import join, dirname

class PlanningArea(Location):
    """
    Object encapsulating the planning areas in Singapore.

    Fields:
        code (str): the code assigned to the planning subzone.
        planning_area (str): the medium-level division of Singapore (Woodlands, Tampines, Bedok etc.)
        region (str): the broadest-level division of Singapore (East, West, North etc.)
    """
    code: str
    planning_area: str
    region: str

    def __init__(self, name: str, **kwargs):
        fields = ["lat", "lon", "shape", "code", "planning_area", "region"]
        self._try_setter(fields, kwargs)
        super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)

class PlanningAreas(Locations):
    locations_interval_tree: IntervalTree
    _FIELD_MAP = {
        "geometry": "shape",
        "SubzoneCode": "code",
        "Planning": "planning_area",
        "Region": "region",
    }
    _PATH_TO_PLANNING_AREAS = join(dirname(__file__), "assets/Subzone_Census2010.kml")

    def __init__(self, *areas: PlanningArea, name="planning_area"):
        self.locations_interval_tree = IntervalTree()
        super().__init__(*areas, name=name)
        self.locations_interval_tree.add_all([area.shape for area in areas], areas)

    @staticmethod
    def get(blanks=False, offline=True) -> PlanningAreas:
        raw_df = PlanningAreas._get_data_handler(offline)
        data_dict = PlanningAreas._get_data_cleaning(blanks)(raw_df)
        areas = PlanningAreas._get_data_compiling(data_dict)
        return PlanningAreas(*areas)

    @staticmethod
    def _get_data_handler(offline: bool) -> pd.DataFrame:
        gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
        return gpd.read_file(PlanningAreas._PATH_TO_PLANNING_AREAS, driver='KML')

    @staticmethod
    def _get_data_cleaning(blanks: bool) -> Callable[[pd.DataFrame], List[Dict[str, Any]]]:
        def clean_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
            extract_from_description = lambda pattern: df.Description.str.extract(pattern)
            df["SubzoneCode"]  = extract_from_description("Subzone Code.*?<td>(.*?)</td>")
            df["Planning"]     = extract_from_description("Planning Area Name.*?<td>(.*?)</td>")
            df["Region"]       = extract_from_description("Region Name.*?<td>(.*?)</td>")
            df = df.drop("Description",axis=1)
            # df["bounds"] = df.geometry.apply(lambda x: x.bounds)
            df = df[["Name", "SubzoneCode", "Planning", "Region", "geometry"]]
            return df.to_dict("records")
        return clean_data

    @staticmethod
    def _get_data_compiling(data_dict: List[Dict[str, Any]]) -> List[PlanningArea]:
        areas: List[PlanningArea] = []
        for info in data_dict:
            name = info.pop("Name")
            areas.append(PlanningArea(name, **PlanningAreas._field_map(info)))
        return areas

    @staticmethod
    def _field_map(d: Dict[str, Any]) -> Dict[str, Any]:
        for old_field, new_field in PlanningAreas._FIELD_MAP.items():
            if new_field not in d:
                d[new_field] = d.pop(old_field)
        return d

    def get_nearest_to(self, point: GeoPt) -> Tuple[PlanningArea, float]:
        return (self.locations_interval_tree.find_shape(point), 0)
        