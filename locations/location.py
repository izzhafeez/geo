from __future__ import annotations
from ..geometry.elevation import ElevationMap
from ..geometry.pt import GeoPt
from ..geometry.shape import Shape
from ..utils.float import check_all_float
from functools import cached_property
import numpy as np
import json
import requests
from typing import Tuple, Optional, Dict, List, Any, Callable
import pandas as pd
from gsheets import Sheets
from abc import ABC, abstractmethod
from ..structures.kdtree import KDTree

class Location(GeoPt, ABC):
    name: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    shape: Optional[Shape] = None
    _nearest: Dict[Location, float]

    def __init__(self, name: str, lat: float=None, lon: float=None, shape: Shape=None):
        self.name = name
        self.shape = shape
        lat, lon = self._get_coords(lat, lon)
        self._nearest = {}
        super().__init__(lat=lat, lon=lon)

    def __str__(self) -> str:
        type_ = str(type(self)).split(".")[-1].split("'")[0]
        return f"<{type_}: {self.name}, ({self.lat}, {self.lon})>"

    def __repr__(self) -> str:
        type_ = str(type(self)).split(".")[-1].split("'")[0]
        return f"<{type_}: {self.name}>"
    
    def _get_coords(self, lat: float, lon: float) -> None:
        if check_all_float(lat, lon):
            return lat, lon
        if self.shape != None:
            return self.shape.points.center.coords_as_tuple_yx()
        try:
            return self._get_coords_from_api(self.name)
        except IndexError:
            print(self.name, "could not be found.")
            return np.nan, np.nan

    def _get_coords_from_api(self, name: str) -> Tuple[float, float]:
        search_term = "+".join(name.split())
        search_url = ("https://developers.onemap.sg/commonapi"
                f"/search?searchVal={search_term}"
                "&returnGeom=Y&getAddrDetails=Y")
        coords = json.loads(requests.get(search_url).text)["results"][0]

        return float(coords["LATITUDE"]), float(coords["LONGITUDE"])
    
    @cached_property
    def elevation(self) -> float:
        self._elevation = ElevationMap.get_elevation(lat=self.lat, lon=self.lon)
        return self._elevation

    def get_distance(self, point: GeoPt) -> float:
        if self.shape != None:
            return self.shape.get_nearest(point)[1]
        return super().get_distance(point)

    def _try_setter(self, fields: List[str], items: Dict):
        for field in fields:
            if field in items and not pd.isna(items[field]):
                setattr(self, field, items[field])
            else:
                setattr(self, field, None)

    def map_nearest(self, name: str, locations: Locations) -> Tuple[Location, float]:
        self._nearest[name] = locations.get_nearest_to(self)
        setattr(self, "nearest_"+name, self._nearest[name])
        return self._nearest[name]

    def nearest(self, name: str) -> Tuple[Location, float]:
        if name not in self._nearest:
            print(f"Nearest '{name}' not defined. Available options: {', '.join([self._nearest.keys()])}.")
            return (None, float("inf"))
        return self._nearest[name]

class Locations(ABC):
    locations_kdtree: KDTree
    locations: Dict[str, Location]
    name: str

    _SHEET_ID = "1M9Ujc54yZZPlxOX3yxWuqcuJOxzIrDYz4TAFx8ifB8c"

    def __init__(self, *locations: Location, name: str):
        self.name = name
        self.locations_kdtree = KDTree()
        self.locations = {}
        for location in locations:
            self.locations_kdtree.add(location)
            self.locations[location.name] = location

    def __getitem__(self, search_term="") -> Location:
        if search_term in self.locations:
            return self.locations[search_term]
        search_results = dict(filter(
            lambda location: search_term in location[0],
            self.locations.items()))
        if len(search_results) == 1:
            return list(search_results.values())[0]
        if len(search_results) == 0:
            print(f"{search_term} not found. Please try again.")
            return None
        print(f"'{search_term}' produced multiple locations "
            f"({', '.join(list(search_results.keys()))}). "
            "Returning first result.")
        return list(search_results.values())[0]

    @staticmethod
    @abstractmethod
    def get(blanks: bool, offline: bool) -> Locations:
        pass

    @staticmethod
    @abstractmethod
    def _get_data_handler(offline: bool) -> pd.DataFrame:
        pass

    @staticmethod
    @abstractmethod
    def _get_data_cleaning(blanks: bool) -> Dict[str, Any]:
        pass

    @staticmethod
    @abstractmethod
    def _get_data_compiling() -> Locations:
        pass

    @staticmethod
    def get_sheet(name: str) -> pd.DataFrame:
	    sheets = Sheets.from_files('client_secrets.json','~/storage.json')[Locations._SHEET_ID]
	    return sheets.find(name).to_frame()

    def get_with_regex(self, search_term: str="") -> Dict[str, Location]:
        search_results = dict(filter(
            lambda location: search_term in location[0],
            self.locations.items()))
        return search_results

    def get_nearest_to(self, point: GeoPt) -> Tuple[GeoPt, float]:
        return self.locations_kdtree.nearest(point)

    def map_nearest_to(self, locations: Locations) -> List[Tuple[str, Tuple[Location, float]]]:
        to_return = []
        for name, location in self.locations.items():
            location.map_nearest(locations.name, locations)
            to_return.append((name, location.nearest(locations.name)))
        return to_return

    def filter(self, location_filter: Callable[[Location], bool]=lambda location: True, name: str="") -> Locations:
        locations = type(self)(*list(filter(location_filter, self.locations.values())))
        if name == "":
            locations.name = self.name
        else:
            locations.name = name
        return locations

    def show(self, attr: str="name") -> Dict[str, Any]:
        return {name: getattr(value, attr) for name, value in self.locations.items()}

    def sort(self, comparator: Callable[[Location], Any], reverse=False) -> str:
        return {k: comparator(v) for k, v in sorted(self.locations.items(), key=lambda item: comparator(item[1]), reverse=reverse)}
