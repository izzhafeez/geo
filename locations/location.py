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
    shape: Optional[Shape] = None

    def __init__(self, name: str, lat: float=None, lon: float=None, shape: Shape=None):
        self.name = name
        self.shape = shape
        lat, lon = self._get_coords(lat, lon)
        super().__init__(lat, lon)
    
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

        return float(coords["LONGITUDE"]), float(coords["LATITUDE"])
    
    @cached_property
    def elevation(self) -> float:
        self._elevation = ElevationMap.get_elevation(self.lat, self.lon)
        return self._elevation

    def get_distance(self, point: GeoPt) -> float:
        if self.shape != None:
            return self.shape.get_nearest(point)[1]
        return super().get_distance(point)
    