from __future__ import annotations
from ..geometry.elevation import ElevationMap
from ..geometry.pt import GeoPt
from ..geometry.shape import Shape
from ..utils.float import is_float
from ..structures.kdtree import KDTree
from ..structures.bound import Bound
from functools import cached_property
import numpy as np
import json
import requests
from typing import Tuple, Optional, Dict, List, Any, Callable, Union
import pandas as pd
from gsheets import models, Sheets
from abc import ABC, abstractmethod

class Location(GeoPt, ABC):
    """
    Object to encapsulate a location in Singapore.
    
    Fields:
        name (str): the name of the location.
        lat (float): the latitude coordinate of the location.
        lon (float): the longitude coordinate of the location.
        shape (Optional[Shape]): the shape representing the location, if available.
        _nearest (Dict[str, Tuple[Location, float]]): the dictionary storing
            the nearest (malls, schools etc.) to that particular location.
    """
    name:     str
    lat:      float
    lon:      float
    shape:    Optional[Shape] = None
    _nearest: Dict[str, Tuple[GeoPt, float]]

    def __init__(self, name: str, lat: float=None, lon: float=None, shape: Shape=None):
        """
        Initialiser for the Location object

        Args:
            name (str): the name of the location.
            lat (float, optional): the latitude coordinate of the location.
                Defaults to None.
            lon (float, optional): the longitude coordinate of the location.
                Defaults to None.
            shape (Shape, optional): the shape representing the location.
                Defaults to None.
        """
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
    
    def _get_coords(self, lat: Optional[float], lon: Optional[float]) -> Tuple[float, float]:
        """
        If latitude or longitude are not available, first check whether the shape is available.
        If shape is available, then compute the center of the shape.
        Otherwise, query developers.onemap.sg to obtain the lat long based on its name.

        Args:
            lat (Optional[float]): latitude.
            lon (Optional[float]): longitude.

        Returns:
            Tuple[float, float]: new lat long values.
        """
        if lat and lon and is_float(lat) and is_float(lon):
            return lat, lon
        if self.shape is not None:
            return Bound.get_bound_from_shape(self.shape).center.as_geo_pt().coords_as_tuple_yx()
        try:
            return self._get_coords_from_api(self.name)
        except IndexError:
            print(self.name, "could not be found.")
            return np.nan, np.nan

    def _get_coords_from_api(self, name: str) -> Tuple[float, float]:
        """
        Queries developers.onemap.sg to obtain lat long values.

        Args:
            name (str): name of the location to be queried.

        Returns:
            Tuple[float, float]: newly mapped lat long values.
        """
        search_term = "+".join(name.split())
        search_url = ("https://developers.onemap.sg/commonapi"
                      f"/search?searchVal={search_term}"
                      "&returnGeom=Y&getAddrDetails=Y")
        coords = json.loads(requests.get(search_url).text)["results"][0]

        return float(coords["LATITUDE"]), float(coords["LONGITUDE"])
    
    @cached_property
    def elevation(self) -> float:
        """
        Lazily gets elevation value of the location.

        Returns:
            float: elevation at the location.
        """
        self._elevation = ElevationMap.get_elevation(lat=self.lat, lon=self.lon)
        return self._elevation

    def get_distance(self, point: GeoPt) -> float:
        """
        Gets distance from the location to another point on Earth.

        Args:
            point (GeoPt): the destination point to query.

        Returns:
            float: distance in metres.
        """
        if self.shape is not None:
            if self.shape.contains(point):
                return 0
            return self.shape.get_nearest(point)[1]
        return super().get_distance(point)

    def _try_setter(self, fields: List[str], items: Dict[str, Any]) -> None:
        """
        For each field in the specified fields list,
            the method will try to assign it to the object.
        If not possible, then it will just skip it.

        Args:
            fields (List[str]): list of fields to be included in the object.
            items (Dict[str, Any]): dictionary containing the fields and values.
                May not always contain all the fields needed.
        """
        for field in fields:
            if field in items and not pd.isna(items[field]):
                setattr(self, field, items[field])
            else:
                setattr(self, field, None)

    def map_nearest(self, name: str, locations: Locations) -> Tuple[GeoPt, float]:
        """
        From a set of locations, get the nearest one to this location.

        Args:
            name (str): name to assign to this group of locations (malls etc.)
            locations (Locations): collection of locations to search from.

        Returns:
            Tuple[GeoPt, float]: pair of point and distance to point.
        """
        self._nearest[name] = locations.get_nearest_to(self)
        setattr(self, "nearest_"+name, self._nearest[name])
        return self._nearest[name]

    def nearest(self, name: str) -> Tuple[Optional[GeoPt], float]:
        """
        If already generated, returns the nearest location in that group,
            in the form of a point-distance pair.
        Else, warns the user.

        Args:
            name (str): group of locations to be queried.

        Returns:
            Tuple[Optional[GeoPt], float]: point-distance pair.
        """
        if name not in self._nearest:
            joined_keys = ', '.join([*self._nearest.keys()])
            print(f"Nearest '{name}' not defined. Available options: {joined_keys}.")
            return (None, float("inf"))
        return self._nearest[name]

    def nearest_location(self, name: str) -> Optional[GeoPt]:
        """
        Gets the point from the point-distance pair.

        Args:
            name (str): group of locations to be queried.

        Returns:
            Optional[GeoPt]: nearest point to location.
        """
        return self.nearest(name)[0]

    def nearest_distance(self, name: str) -> float:
        """
        Gets the distance from the point-distance pair.

        Args:
            name (str): group of locations to be queried.

        Returns:
            float: distance to nearest point to location.
        """
        return self.nearest(name)[1]

class Locations(ABC):
    """
    Object encapsulating a collection of locations.
    Facilitates the searching of nearest points (using KDTree).
    Enables filtering, sorting regex searching of locations.

    Fields:
        locations_kdtree (KDTree): KDTree representing the locations.
            This reduces the expected time complexity of searching nearest points to O(logN).
        locations (Dict[str, Location]): dictionary storing the locations of the group,
            indexed by name to make it easier to access them.
        name (str): the name assigned to this group of locations.
    """
    locations_kdtree: KDTree
    locations:        Dict[str, Location]
    name:             str

    _SHEET_ID = "1M9Ujc54yZZPlxOX3yxWuqcuJOxzIrDYz4TAFx8ifB8c"

    def __init__(self, *locations: Location, name: str):
        """
        Initialiser for the Locations object.

        Args:
            name (str): name to assign to the group of locations.
        """
        self.name = name
        self.locations_kdtree = KDTree()
        self.locations = {}
        for location in locations:
            self.locations_kdtree.add(location)
            self.locations[location.name] = location

    def __getitem__(self, search_term="") -> Optional[Location]:
        """
        Searches for a particular location in the group, using relaxed searching.
        If only one result exists, then return it.
        Elif more than one result exists, warn the user and return the first result.
        Else return None.

        Args:
            search_term (str, optional): the string to look for
                in the names of the locations. Defaults to "".

        Returns:
            Optional[Location]: a single location that matches the criteria.
        """
        if search_term in self.locations:
            return self.locations[search_term]
        search_results = dict(filter(lambda location: search_term in location[0],
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
        """
        The full process for obtaining data from a dataset.
        This may take varying amounts of time depending on the type of Location being processed.

        Args:
            blanks (bool): whether to allow blank fields in the final set.
            offline (bool): whether to process the offline (static) dataset,
                or the online (dynamic) dataset. The dynamic dataset will take a
                longer time to process.

        Returns:
            Locations: the group of locations after processing the data.
        """
        pass

    @staticmethod
    @abstractmethod
    def _get_data_handler(offline: bool) -> pd.DataFrame:
        """
        Process for extracting data from the dataset.

        Args:
            offline (bool): whether to process the static or dynamic dataset.

        Returns:
            pd.DataFrame: the dataframe containing the relevant information.
        """
        pass

    @staticmethod
    @abstractmethod
    def _get_data_cleaning(blanks: bool) -> Dict[str, Any]:
        """
        Process for cleaning data extracted from the dataset.

        Args:
            blanks (bool): whether to accept any blank fields.

        Returns:
            Dict[str, Any]: dictionary storing the name of the location,
                mapped to the supplementary information.
        """
        pass

    @staticmethod
    @abstractmethod
    def _get_data_compiling(data_dict: Dict) -> Locations:
        """
        Creates the Location objects based on the data processed earlier.

        Args:
            data_dict (Dict): data dictionary to be processed.

        Returns:
            Locations: group of locations in the final set.
        """
        pass

    @staticmethod
    def get_sheet(name: str) -> pd.DataFrame:
        """
        Extracts data from Google Sheets, given the name of the sheet.

        Args:
            name (str): name of the sheet to be downloaded.

        Returns:
            pd.DataFrame: data extracted from Google Sheets.
        """
        sheets: Union[models.SpreadSheet, List[object]] = Sheets.from_files('client_secrets.json','~/storage.json')[Locations._SHEET_ID]
        return sheets.find(name).to_frame() if isinstance(sheets, models.SpreadSheet) else pd.DataFrame()
        

    def get_with_regex(self, search_term: str="") -> Dict[str, Location]:
        """
        Gets locations whose names match the regex pattern.

        Args:
            search_term (str, optional): regex pattern to search for. Defaults to "".

        Returns:
            Dict[str, Location]: filtered dictionary based on the pattern matching.
        """
        search_results = dict(filter(lambda location: search_term in location[0],
                                     self.locations.items()))
        return search_results

    def get_nearest_to(self, point: GeoPt) -> Tuple[GeoPt, float]:
        """
        For an external point, find which of this group's locations is the closest.

        Args:
            point (GeoPt): external point to query.

        Returns:
            Tuple[GeoPt, float]: point-distance pair.
        """
        nearest_point, distance = self.locations_kdtree.nearest(point)
        return (nearest_point.as_geo_pt(), distance)

    def map_nearest_to(self, locations: Locations) -> List[Tuple[str, Tuple[Location, float]]]:
        """
        For each location in this set, apply the nearest method to each one of an external location.
        For example, malls.map_nearest_to(schools) will map each mall to its nearest school.

        Args:
            locations (Locations): group of destination locations to map to.

        Returns:
            List[Tuple[str, Tuple[Location, float]]]: the result of the mapping.
        """
        to_return = []
        for name, location in self.locations.items():
            location.map_nearest(locations.name, locations)
            to_return.append((name, location.nearest(locations.name)))
        return to_return

    def filter(self,
               location_filter: Callable[[Location], bool]=lambda location: True,
               name: str="") -> Locations:
        """
        Filters out locations based on certain criteria (lambda function).
        Returns another Locations object containing these new locations.
        Filters can be chained together like in locations.filter(f1).filter(f2)
        For example, lambda location: location.lat > 1.38.

        Args:
            location_filter (Callable, optional): lambda function to determine whether a locations passes the filter.
                Defaults to lambda location:True.
            name (str, optional): optional name to be given to this subset of locations. Defaults to "".

        Returns:
            Locations: subset of the original locations.
        """
        name_to_use = self.name if name == "" else name
        filtered_locations = list(filter(location_filter, self.locations.values()))
        locations = type(self)(*filtered_locations, name=name_to_use)
        return locations

    def show(self, attr: str="name") -> Dict[str, Any]:
        """
        Shows a particular attribute of all the locations.

        Args:
            attr (str, optional): the attribute to show. Defaults to "name".

        Returns:
            Dict[str, Any]: name-attribute pair.
        """
        return {name: getattr(value, attr) for name, value in self.locations.items()}
    
    def show_by_lambda(self,
                       getter: Callable[[Location], Any]=lambda location: location.name) -> Dict[str, Any]:
        """
        Instead of showing a particular attribute, this method allows the user to set up custom show functions.
        For example, lambda location: location.lat + location.lon.

        Args:
            getter (Callable[[Location], Any], optional): custom show function. Defaults to lambda location:location.name.

        Returns:
            Dict[str, Any]: name-value pair with the values being defined in the custom show function.
        """
        return {name: getter(value) for name, value in self.locations.items()}

    def sort(self,
             comparator: Callable[[Location], Any]=lambda location: location.name,
             reverse=False) -> Dict[str, Location]:
        """
        Sorts the locations based on a particular attribute, or custom function.
        For example, lambda location: location.lat will sort them by latitude.

        Args:
            comparator (Callable[[Location], Any], optional): the lambda function used to compare elements.
                Defaults to lambda location:location.name.
            reverse (bool, optional): whether to reverse the values. Defaults to False.

        Returns:
            Dict[str, Location]: name-value pair with the values being defined in the custom show function.
        """
        return {k: comparator(v) for k, v in sorted(self.locations.items(),
                                                    key=lambda item: comparator(item[1]),
                                                    reverse=reverse)}
