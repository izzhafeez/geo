from __future__ import annotations
from os.path import dirname, join
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from .location import Location, Locations
from ..geom.elevation import ElevationMap

class Halal(Location):
  """
  Object to encapsulate a Halal store in Singapore.

  Fields:
    store (str): the name of the franchise or store.
    unit (Optional[str]): the unit number of the halal store.
    food_types (str): the type of food they serve.
    cuisines (str): the cuisines of this store.
    foods (str): the food sold in this store.
    location (Optional[Location]): the location of this store.
  """
  store: str
  unit: Optional[str]
  food_types: str
  cuisines: str
  foods: str
  location: Optional[Location]

  def __init__(self, name: str, **kwargs):
    fields = ["lat", "lon", "shape", "store", "unit", "food_types", "cuisines", "foods", "location"]
    self._try_setter(fields, kwargs)
    super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)

class Halals(Locations):
  _FIELD_MAP = {
    "Latitude": "lat",
    "Longitude": "lon",
    "Unit": "unit",
    "Location": "location"
  }

  def __init__(self, *halals: Halal, name: str="halal"):
    super().__init__(*halals, name=name)

  @staticmethod
  def get(blanks: bool=False, offline: bool=True) -> Halals:
    raw_df = Halals._get_data_handler(offline)
    data_dict = Halals._get_data_cleaning(blanks)(raw_df)
    halals = Halals._get_data_compiling(data_dict)
    return Halals(*halals)

  @staticmethod
  def _get_data_handler(offline: bool) -> pd.DataFrame:
    if offline:
      return pd.read_csv(join(dirname(__file__), "assets/halals.csv"))
    print("Retrieving 'Halals' from Sheets...")
    raw_df = Locations.get_sheet("Halal")
    print("Retrieved.")
    return raw_df

  @staticmethod
  def _get_data_cleaning(blanks: bool=True) -> Callable[[pd.DataFrame], Dict[str, Any]]:
    def combined_name(df: pd.DataFrame) -> pd.DataFrame:
      df["store"] = df.Name
      df["Name"] = df.store + " (" + df.Location + ")"
      return df
    def drop(df: pd.DataFrame) -> pd.DataFrame:
      df = df.drop_duplicates(subset=["Name"], keep="first")
      return df
    if blanks:
      return lambda df: drop(combined_name(df))\
        .set_index("Name").to_dict("index")
    return lambda df: drop(combined_name(df))\
      .set_index("Name").to_dict("index")
      
  @staticmethod
  def _get_data_compiling(data_dict: Dict[str, Any]) -> List[Halal]:
    halals: List[Halal] = []
    for name, info in data_dict.items():
      search: List[str] = info["Search"].split(",")
      food_types: List[str] = []
      cuisines: List[str] = []
      foods: List[str] = []
      dummy = []
      
      list_to_add = food_types
      for i in range(1, len(search)):
        elem = search[i].strip()
        if elem == "Cuisine":
          list_to_add = cuisines
        elif elem == "Food":
          list_to_add = dummy
        elif elem == "Recommend food":
          list_to_add = foods
        else:
          list_to_add.append(elem)
        
      info["food_types"] = ", ".join(food_types)
      info["cuisines"] = ", ".join(cuisines)
      info["foods"] = ", ".join(foods)
      
      if ElevationMap.in_singapore(info["Latitude"], info["Longitude"]):
        halals.append(Halal(name, **Halals._field_map(info)))
    return halals

  @staticmethod
  def _field_map(d: Dict[str, Any]) -> Dict[str, Any]:
    for old_field, new_field in Halals._FIELD_MAP.items():
      d[new_field] = d.pop(old_field)
    return d
