from __future__ import annotations
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
import json

from gsheets import models, Sheets
from tqdm import tqdm
# import contextily as ctx
import geopandas as gpd
import numpy as np
import pandas as pd
import requests
import shapely.geometry

from ..error.value_error.out_of_bounds_error import OutOfBoundsError
from ..geom.elevation import ElevationMap
from ..geom.geo_pt import GeoPt
from ..geom.shape import Shape
from ..structures.bound import Bound
from ..structures.kdtree import KDTree
from ..utils.float import is_float

class Location(GeoPt, ABC):
  """
  Object to encapsulate a location in Singapore.
  
  Fields:
    name (str): the name of the location.
    lat (Optional[float]): the latitude coordinate of the location.
    lon (Optional[float]): the longitude coordinate of the location.
    shape (Optional[Shape]): the shape representing the location, if available.
    _nearest (Dict[str, Tuple[Location, float]]): the dictionary storing
      the nearest (malls, schools etc.) to that particular location.
  """
  name:   str
  lat:    Optional[float]
  lon:    Optional[float]
  shape:  Optional[Shape] = None
  _nearest: Dict[str, Tuple[Optional[GeoPt], float]]
  _within: Dict[str, List[GeoPt]]

  def __init__(self, name: str, lat: Optional[float]=None, lon: Optional[float]=None, shape: Optional[Shape]=None):
    self.name = name
    self.shape = shape
    lat, lon = self._get_coords(lat, lon)
    self._nearest = {}
    self._within = {}
    if lat and lon:
      super().__init__(lat=lat, lon=lon)
    else:
      super().__init__(lat=float("inf"), lon=float("inf"))

  def __str__(self) -> str:
    type_ = str(type(self)).split(".")[-1].split("'")[0]
    return f"<{type_}: {self.name}, ({self.lat}, {self.lon})>"

  def __repr__(self) -> str:
    type_ = str(type(self)).split(".")[-1].split("'")[0]
    return f"<{type_}: {self.name}>"
  
  def _get_coords(self, lat: Optional[float], lon: Optional[float]) -> Tuple[Optional[float], Optional[float]]:
    """
    If latitude or longitude are not available, first check whether the shape is available.
    If shape is available, then compute the center of the shape.
    Otherwise, query developers.onemap.sg to obtain the lat long based on its name.

    Args:
      lat (Optional[float]): latitude.
      lon (Optional[float]): longitude.

    Returns:
      Tuple[Optional[float], Optional[float]]: new lat long values.
    """
    if lat and lon and is_float(lat) and is_float(lon):
      return lat, lon
    if self.shape is not None:
      return GeoPt.from_bound(Bound.get_bound_from_shape(self.shape)).coords_as_tuple_latlong()
    try:
      return self._get_coords_from_api(self.name)
    except IndexError:
      print(self.name, "could not be found.")
      return None, None

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
      if field in items and items[field] is not None:
        setattr(self, field, items[field])
      else:
        setattr(self, field, None)
  
  @cached_property
  def elevation(self) -> Optional[float]:
    """
    Lazily gets elevation value of the location.

    Returns:
      Optional[float]: elevation at the location.
    """
    if self.lat and self.lon:
      return ElevationMap.get_elevation(lat=self.lat, lon=self.lon)
    return None

  def get_distance(self, point: Location, base: bool=True) -> float:
    """
    Gets distance from the location to another point on Earth.

    Args:
      point (Location): the destination point to query.

    Returns:
      float: distance in km.
    """
    if self.shape is not None:
      if self.shape.contains(point):
        return 0
      if base:
        if point.shape and self.shape.exterior and point.shape.exterior:
          distance = (self.shape.exterior.distance(point) * 111.33
                + point.shape.exterior.distance(self) * 111.33
                - super().get_distance(point))
          return max(round(distance, 4), 0)
      return self.shape.get_nearest(point)[1]
    return super().get_distance(point)

  def map_nearby(self, locations: Locations, threshold: float, name: str="") -> List[GeoPt]:
    """
    Gets all the locations within a certain radius around self.
    
    Args:
      locations (Locations): target locations to fall within the circle.
      threshold (float): maximum distance permitted for the circle.
      name (str): name to assign to this group of locations (malls etc.)
      
    Returns:
      List[GeoPt]: points that fall within the range.
    """
    within: List[GeoPt] = []
    for location in locations:
      if self.get_distance(location) <= threshold:
        within.append(location)
    self._within[name] = within
    setattr(self, "nearby_"+name, within)
    return within

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

  def nearest_distance(self, name: str) -> float:
    """
    Gets the distance from the point-distance pair.

    Args:
      name (str): group of locations to be queried.

    Returns:
      float: distance to nearest point to location.
    """
    return self.nearest(name)[1]

  def nearest_location(self, name: str) -> Optional[GeoPt]:
    """
    Gets the point from the point-distance pair.

    Args:
      name (str): group of locations to be queried.

    Returns:
      Optional[GeoPt]: nearest point to location.
    """
    return self.nearest(name)[0]

  def map_nearest(self,
          locations: Locations,
          name: str="") -> Tuple[Optional[GeoPt], float]:
    """
    From a set of locations, get the nearest one to this location.

    Args:
      name (str): name to assign to this group of locations (malls etc.)
      locations (Locations): collection of locations to search from.

    Returns:
      Tuple[GeoPt, float]: pair of point and distance to point.
    """
    name = name if name != "" else locations.name
    nearest_point, nearest_distance = locations.get_nearest_to(self)
    self._nearest[name] = (nearest_point, nearest_distance) if nearest_point else (None, float("inf"))
    setattr(self, name, self._nearest[name])
    setattr(self, "nearest_"+name, self._nearest[name][0])
    setattr(self, "distance_to_"+name, self._nearest[name][1])
    return self._nearest[name]

class Locations(ABC):
  """
  Object encapsulating a collection of locations.
  Facilitates the searching of nearest points (using KDTree).
  Enables filtering, sorting regex searching of locations.

  Fields:
    kdtree (KDTree[Dict]): KDTree representing the locations.
      This reduces the expected time complexity of searching nearest points to O(logN).
    locations (Dict[str, Location]): dictionary storing the locations of the group,
      indexed by name to make it easier to access them.
    name (str): the name assigned to this group of locations.
  """
  kdtree:  KDTree[GeoPt]
  locations: Dict[str, Location]
  name:    str

  _SHEET_ID = "1M9Ujc54yZZPlxOX3yxWuqcuJOxzIrDYz4TAFx8ifB8c"

  def __init__(self, *locations: Location, name: str):
    """
    Initialiser for the Locations object.

    Args:
      name (str): name to assign to the group of locations.
    """
    self.name = name
    self.kdtree = KDTree[GeoPt]()
    self.locations = {}
    self.kdtree.add_all(*locations)
    for location in locations:
      if location.lat == float("inf"):
        continue
      if location.name not in self.locations:
        self.locations[location.name] = location
      else:
        self.locations[location.name+" "+type(location).__name__] = location

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

  def __iter__(self) -> LocationIterator:
    return LocationIterator(self.locations)
  
  def insert(self,
        to_insert: List[Location],
        name: str="") -> Locations:
    """
    Adds locations to the existing set of locations.
    Returns another Locations object containing these new locations.
    Inserts can be chained together like in locations.insert(i1).insert(i2)
    For example, [L1, L2].

    Args:
      to_insert (List[Location]): list of locations to add to the existing set.
      name (str, optional): optional name to be given to this subset of locations. Defaults to "".

    Returns:
      Locations: superset of the original locations.
    """
    name_to_use = self.name if name == "" else name
    appended_locations = list(self.locations.values()) + to_insert
    locations = type(self)(*appended_locations, name=name_to_use)
    return locations

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
  
  @cached_property
  def count(self):
    return len(self.locations.keys())
  
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
  
  def get_by_regex(self, search_term: str="") -> Dict[str, Location]:
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

  def get_nearest_to(self, point: GeoPt) -> Tuple[Optional[GeoPt], float]:
    """
    For an external point, find which of this group's locations is the closest.

    Args:
      point (GeoPt): external point to query.

    Returns:
      Tuple[GeoPt, float]: point-distance pair.
    """
    nearest_point, distance = self.kdtree.nearest(point)
    return (nearest_point, distance) if nearest_point else (None, float("inf"))
  
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

  def group_by(self,
         comparator: Callable[[Location], str]=lambda location: location.name) -> Dict[str, Locations]:
    locations_dict: Dict[str, List[Location]] = {}
    for _, location in self.locations.items():
      to_compare = comparator(location)
      if to_compare not in locations_dict:
        locations_dict[to_compare] = []
      locations_dict[to_compare].append(location)
    
    return {k: type(self)(*v, name=k) for k, v in locations_dict.items()}
      
  def map_nearby_to(self,
										locations: Locations,
										threshold: float,
										locations_name: str="",
										progress_bar: bool=False) -> Dict[str, List[GeoPt]]:
    """
    For each location in this set, apply the nearby method to each one of an external location.
    For example, malls.map_nearby_to(schools) will map each mall to schools that are near to the mall.

    Args:
      locations (Locations): group of destination locations to map to.
      locations_name (str): what to name the group of locations.
      threshold (float): maximum distance permitted to quality for this set.

    Returns:
      List[Tuple[str, Tuple[Location, float]]]: the result of the mapping.
    """
    to_return: Dict[str, List[GeoPt]] = {}
    iterable = tqdm(self.locations.items()) if progress_bar else self.locations.items()
    for name, location in iterable:
      locations_name = locations.name if locations.name != "" else locations.name
      nearby = location.map_nearby(locations, threshold, locations_name)
      to_return[name] = nearby
    return to_return    
      
  def map_nearest_to(self,
             				 locations: Locations,
                     locations_name: str="",
                     progress_bar: bool=False,
                     dist: bool=True) -> Dict[str, Tuple[Location, float]]:
    """
    For each location in this set, apply the nearest method to each one of an external location.
    For example, malls.map_nearest_to(schools) will map each mall to its nearest school.

    Args:
      locations (Locations): group of destination locations to map to.
      locations_name (str): what to name the group of locations.
      prefix (str): what to put in front of the name.

    Returns:
      List[Tuple[str, Tuple[Location, float]]]: the result of the mapping.
    """
    to_return = {}
    iterable = tqdm(self.locations.items()) if progress_bar else self.locations.items()
    for name, location in iterable:
      locations_name = locations.name if locations.name != "" else locations.name
      location.map_nearest(locations, locations_name)
      to_return[name] = location.nearest(locations_name)
    return to_return
   
  # def plot(self, zoom: int=13, figsize=(20, 20), alpha=0.4, color="red") -> None:
  #   if not 12 <= zoom <= 19:
  #     raise OutOfBoundsError(zoom, 12, 19)
  #   gdf = gpd.GeoDataFrame([location.shape if hasattr(location, "shape") else location for location in self.locations.values()], columns=["geometry"])
  #   ax = gdf.geometry.plot(figsize=figsize, alpha=alpha, color=color)
  #   ctx.add_basemap(ax, zoom=zoom, crs="EPSG:4326", source=ctx.providers.OneMapSG.Night)

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
       attr: str="name",
       show: str="",
       reverse=False) -> Dict[str, Location]:
    """
    Sorts the locations based on a particular attribute, or custom function.
    For example, lambda location: location.lat will sort them by latitude.

    Args:
      attr: the attribute to sort by. Defaults to name.
      show: the attribute to show in the end result. Defaults to be the same as attr.
      reverse (bool, optional): whether to reverse the values. Defaults to False.

    Returns:
      Dict[str, Location]: name-value pair with the values being defined in the custom show function.
    """
    if show == "":
      show = attr
    return {k: getattr(v, show) for k, v in sorted(self.locations.items(),
                             key=lambda pair: getattr(pair[1], attr),
                             reverse=reverse)}
  
  def sort_by_lambda(self,
             comparator: Callable[[Location], Any]=lambda location: location.name,
             show: Optional[Callable[[Location], Any]]=None,
             reverse=False) -> Dict[str, Location]:
    """
    Sorts the locations based on a particular attribute, or custom function.
    For example, lambda location: location.lat will sort them by latitude.

    Args:
      comparator (Callable[[Location], Any], optional): the lambda function used to compare elements.
        Defaults to lambda location: location.name.
      show (Callable[[Location], Any], optional): the lambda function used to show information contained
        within the location. Defaults to be the same as the comparator.
      reverse (bool, optional): whether to reverse the values. Defaults to False.

    Returns:
      Dict[str, Location]: name-value pair with the values being defined in the custom show function.
    """
    if not show:
      show = comparator
    return {k: show(v) for k, v in sorted(self.locations.items(),
                        key=lambda item: comparator(item[1]),
                        reverse=reverse)}

  def to_dict(self, subset: List[str]=[]) -> Dict[str, Dict[str, Any]]:
    return {
      k: {
        key: getattr(v, key) for key in subset
      } for k, v in self.locations.items()
    }

  def to_df(self, subset: List[str]=[]) -> pd.DataFrame:
    return pd.DataFrame.from_dict(self.to_dict(subset)).T

class LocationIterator:
  """
  Iterator object for the locations in Locations.
  """
  def __init__(self, locations: Dict[str, Location]):
    self._locations = list(locations.items())
    self._index = 0
    self._len = len(locations)
  
  def __next__(self) -> Location:
    if self._index < self._len:
      to_return = self._locations[self._index][1]
      self._index += 1
      return to_return
    raise StopIteration