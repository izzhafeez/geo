from __future__ import annotations
from os.path import dirname, join
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd
import pickle

from geom.elevation import ElevationMap
from geom.shape import Shape
from .location import Location, Locations

class BusStop(Location):
  """
  Object to encapsulate a Bus Stop in Singapore.

  Fields:
    services (List[str]): The bus services that go to this Bus Stop.
    road_name (str): The name of the road that this bus stop is on.
  """
  services: List[str]
  road_name: str

  def __init__(self, name: str, **kwargs):
    fields = ["lat", "lon", "shape", "services", "road_name"]
    self._try_setter(fields, kwargs)
    super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)

class BusStops(Locations):
  _FIELD_MAP = {
    
  }

  def __init__(self, *bus_stops: BusStop, name: str="busstop"):
    super().__init__(*bus_stops, name=name)

  @staticmethod
  def get(blanks: bool=False, offline: bool=True) -> BusStops:
    raw_df = BusStops._get_data_handler(offline)
    data_dict = BusStops._get_data_cleaning(blanks)(raw_df)
    bus_stops = BusStops._get_data_compiling(data_dict)
    return BusStops(*bus_stops)

  @staticmethod
  def _get_data_handler(offline: bool) -> pd.DataFrame:
    if offline:
      return pd.read_csv(join(dirname(__file__), "assets/bus.csv"))
    print("Retrieving 'Bus' from Sheets...")
    raw_df = Locations.get_sheet("Bus")
    print("Retrieved.")
    return raw_df

  @staticmethod
  def _get_data_cleaning(blanks: bool=True) -> Callable[[pd.DataFrame], Dict[str, Any]]:
    def convert_into_dict(df: pd.DataFrame) -> Dict[str, Any]:
      buses_dict = {}
      for bus_stop, frame in df.groupby("BusStopCode"):
        buses_dict[bus_stop] = {
          "lat": frame.Latitude.to_list()[0],
          "lon": frame.Longitude.to_list()[0],
          "road_name": frame.RoadName.to_list()[0],
          "services": list(set(frame.ServiceNo.to_list()))
        }
      return buses_dict
    return convert_into_dict
      
  @staticmethod
  def _get_data_compiling(data_dict: Dict[str, Any]) -> List[BusStop]:
    bus_stops: List[BusStop] = []
    for name, info in data_dict.items():
      if ElevationMap.in_singapore(info["lat"], info["lon"]):
        bus_stops.append(BusStop(name, **BusStops._field_map(info)))
    return bus_stops

  @staticmethod
  def _field_map(d: Dict[str, Any]) -> Dict[str, Any]:
    for old_field, new_field in BusStops._FIELD_MAP.items():
      d[new_field] = d.pop(old_field)
    return d
