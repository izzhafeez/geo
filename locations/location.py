from ..geometry.elevation import ElevationMap
from ..geometry.pt import GeoPt
from ..geometry.shape import Shape
from ..utils.float import check_all_float
from functools import cached_property
import numpy as np
import json
import requests
from typing import Tuple, Optional

class Location(GeoPt):
    name: str
    lat: Optional[float] = None
    lon: Optional[float] = None

    def __init__(self, name: str, lat: float=None, lon: float=None):
        self.name = name
        lat, lon = self._get_coords(lat, lon)
        super().__init__(lat, lon)

    @staticmethod
    def of(name: str, lat: float=None, lon: float=None, shape: Shape=None):
        if shape != None:
            return ShapedLocation(name, shape)
        return Location(name, lat, lon)
    
    def _get_coords(self, lat: float, lon: float) -> None:
        if check_all_float(lat, lon):
            return lat, lon
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

        return float(coords["LONGITUDE"]), float(coords["LATITUDE"])
    
    @cached_property
    def elevation(self) -> float:
        self._elevation = ElevationMap.get_elevation(self.lat, self.lon)
        return self._elevation

class ShapedLocation(Location):
    name: str
    shape: Shape

    def __init__(self, name: str, shape: Shape):
        super().__init__(name, *shape.points.center.coords_as_tuple_yx())
        self.shape = Shape

    def get_distance(self, point: GeoPt) -> float:
        return self.shape.get_nearest(point)[1]
    