from bs4 import BeautifulSoup
from os.path import dirname, join
from spiderman import Website
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import geopandas as gpd
import logging
import pandas as pd
import re

"""
PURPOSE (NO LONGER WORKS FULLY)

I made this code to extract all the kinds of data you'd want to know about MRT and LRT stations.
More specific information will be given in comments below but as of now, here is the link: https://docs.google.com/spreadsheets/d/e/2PACX-1vQIXKejfbHe2FuPKp0qvdS6OfLDceHGO2WvxGgJtyuoD6HyAmd9Qxj8NZsJA4JItvPcqRKyMJUdDVF-/pub?gid=1134364680&single=true&output=pdf
Do note that this is not the full version of the dataset, as I wanted to only keep the essentials in there.

Download data for train station exits: TrainStationExit_Jan2020/TrainStationExit06032020.shp
Download data for train stations: TrainStation_Jan2020/MRTLRTStnPtt.shp
Download data for OriginDestinationTrain: origin_destination_train_202103.csv
"""

logging.basicConfig(level = logging.DEBUG)

Chinese = str
LinksGetter = Callable[[str], pd.Series[str]]
StationDetails = Dict[str, Optional[Union[float, str]]]

path_to_destination_train = join(dirname(__file__), "assets/origin_destination_train_202103.csv")
path_to_train_station_exits = join(dirname(__file__), "assets/TrainStationExit06032020.shp")
path_to_train_stations = join(dirname(__file__), "assets/MRTLRTStnPtt.shp")

link_to_mrt_list = "https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations"
link_to_lrt_list = "https://en.wikipedia.org/wiki/List_of_Singapore_LRT_stations"
links_to_uncovered_mrt_stations = [
  "https://en.wikipedia.org/wiki/Changi_Airport_MRT_station",
	"https://en.wikipedia.org/wiki/Expo_MRT_station",
	"https://en.wikipedia.org/wiki/Tanah_Merah_MRT_station"
]
links_to_uncovered_lrt_stations = [
  "https://en.wikipedia.org/wiki/Damai_LRT_station_(Singapore)"
]

def extract_links_from_full_list(link_to_station_list: str,
                                 links_getter: LinksGetter) -> List[str]:
  """
	PURPOSE

	DOES NOT WORK NOW BECAUSE WIKIPEDIA CHANGED THE FORMAT OF THE PAGE.
	But what this section does is extract the links to all the Wikipedia pages of the respective MRT and LRT stations.
	Changi Airport, Expo, Tanah Merah and Damai LRT were added manually because they were not found anywhere within the landing page.
	"""
  links_series: pd.Series[str] = links_getter(link_to_station_list)
  list_of_links: List[str] = links_series.apply(lambda x: x.split("\n")).tolist()
  n_filter: Callable[[str], bool] = lambda x: ("a" + x)[-1] == "n"
  return list(filter(n_filter, list_of_links))

def get_all_links() -> List[str]:
  mrt_getter: Callable[[str], LinksGetter] = lambda x: Website(x).getTables().tables[1]["Links"]
  mrt_links = extract_links_from_full_list(link_to_mrt_list, mrt_getter)
  lrt_getter: Callable[[str], LinksGetter] = lambda x: Website(x).getTables().tables[0]["Links"]
  lrt_links = extract_links_from_full_list(link_to_lrt_list, lrt_getter)
  return list(set(
    mrt_links +
    lrt_links +
    links_to_uncovered_mrt_stations +
    links_to_uncovered_lrt_stations
  ))

def get_station_name_from_soup(soup: BeautifulSoup,
                               logger: Callable[[str, Exception], None]) -> Optional[str]:
  try:
    title: str = soup("title")[0].string
    return title.split(" MRT")[0]
  except Exception as e:
    logger("Station Name", e)
    return None
  
def get_chinese_index_from_station_details(details: List[str]) -> int:
  chinese_index = 0
  for detail in details:
    if re.compile("[\u4e00-\u9fff]+").search(detail):
      chinese_index = details.index(detail)
  return chinese_index
  
def get_station_details_from_soup(soup: BeautifulSoup,
                                  logger: Callable[[str, Exception], None]) -> Tuple[Optional[Chinese], Optional[str]]:
  try:
    fn_org = soup.find(class_="fn org")
    if not fn_org:
      raise Exception
    station_details = list(fn_org.stripped_strings)
    chinese_index = get_chinese_index_from_station_details(station_details)
    station_chinese: Chinese = station_details[chinese_index]
    station_labels = ", ".join(station_details[:chinese_index-1])
    return (station_chinese, station_labels)
  except Exception as e:
    logger("Station Details", e)
    return (None, None)
  
def convert_coords(d: float, m: float, s: float) -> float:
  return d + m/60 + s/3600
  
def get_latlong_from_soup(soup: BeautifulSoup,
                          logger: Callable[[str, Exception], None]) -> Tuple[Optional[float], Optional[float]]:
  try:
    lat: float = convert_coords(*re.findall("[0-9.]+", soup(class_="latitude")[0].text))
    lon: float = convert_coords(*re.findall("[0-9.]+", soup(class_="longitude")[0].text))
    return (lat, lon)
  except Exception as e:
    logger("Lat Long", e)
    return (None, None)
  
def get_full_address_from_soup(soup: BeautifulSoup,
                               logger: Callable[[str, Exception], None]) -> Tuple[Optional[str], Optional[str]]:
  try:
    infobox = soup(class_="infobox-data")
    if not infobox:
      raise Exception
    full_address = list(infobox[0].strings)
    address = full_address[0]
    postcode = re.findall(r"\d{6}", full_address[1])[0]
    return (address, postcode)
  except Exception as e:
    logger("Full Address", e)
    return (None, None)

def get_station_info_from_link(link: str) -> StationDetails:
  """
  PURPOSE

  Each page within the links has many key information scattered in various places.
  It was a challenge to make sure all the information from every page was captured, even if the data is inconsistently placed.
  The whole section below is to extract:
    Station Labels (NS26, EW14)
    Station Name (Raffles Place)
    Chinese Translation (莱佛士坊)
    Address (5 Raffles Place)
    Postal Code (048618)
    Latitude (Derived from 1°17′1.97″)
    Longitude (Derived from 103°51′5.52″)
  """
  site: BeautifulSoup = Website(link).html
  logger: Callable[[str, Exception], None] = \
    lambda name, e: logging.debug(f"{name} gave the error: {str(e)}\n{link}")
  station_name: Optional[str] = get_station_name_from_soup(site, logger)
  station_chinese, station_labels = get_station_details_from_soup(site, logger)
  lat, lon = get_latlong_from_soup(site, logger)
  address, postcode = get_full_address_from_soup(site, logger)
  
  return {
    "Label": station_labels,
    "Name": station_name,
    "Chinese": station_chinese,
    "Address": address,
    "Postcode": postcode,
    "Lat": lat,
    "Lon": lon,
    "Link": link
  }
  
def get_abbr_map() -> Dict[str, str]:
  soup: BeautifulSoup = Website(link_to_mrt_list).html
  abbr_mapping = {}
  for t in soup("td", text=re.compile("^[A-Z]{3}$")):
    if t.text != "TBA":
      abbr_mapping[t.find_previous("a", href=True).text.strip()]
  return abbr_mapping

def map_abbr(details: List[StationDetails], abbr_map: Dict[str, str]) -> List[StationDetails]:
  for detail in details:
    if detail["name"] in abbr_map:
      detail["Abbreviation"] = abbr_map[detail["name"]]
  return details

def get_exits_data() -> gpd.GeoDataFrame:
  exits = gpd.read_file(path_to_train_station_exits)
  exits["STN_NAME"] = exits["STN_NAME"].str.replace(" .RT STATION","").str.replace(" STATION","")
  exits = exits[["STN_NAME","EXIT_CODE","geometry"]]
  exits.columns = ["Name","Exit","geometry"]
  return exits

def get_station_geometries() -> gpd.GeoDataFrame:
  stations = gpd.read_file(path_to_train_stations)
  stations["geometry"] = stations.geometry.to_crs(epsg=4326)
  stations["STN_NAME"] = stations["STN_NAME"].str.replace(" .RT STATION","").str.replace(" STATION","")
  stations = stations[["STN_NAME","STN_NO","geometry"]]
  stations.columns = ["Name","Exit","geometry"]
  return stations

def get_passengers_data() -> pd.DataFrame:
  passengers = pd.read_csv(path_to_destination_train)
  passengers.ORIGIN_PT_CODE = passengers.ORIGIN_PT_CODE.str.split("/")
  passengers.DESTINATION_PT_CODE = passengers.DESTINATION_PT_CODE.str.split("/")
  passengers = passengers.explode("ORIGIN_PT_CODE")
  passengers = passengers.explode("DESTINATION_PT_CODE")
  passengers.ORIGIN_PT_CODE = passengers.ORIGIN_PT_CODE.str.strip()
  passengers.DESTINATION_PT_CODE = passengers.DESTINATION_PT_CODE.str.strip()
  return passengers

def merge_mrt_data(partial_data: pd.DataFrame,
                   station_geometries: pd.DataFrame,
                   exits_data: pd.DataFrame,
                   passengers_data: pd.DataFrame,
                   color_map: Dict[str, str]) -> pd.DataFrame:
  mrt_full: pd.DataFrame = partial_data.copy()
  mrt_full["Name"] = mrt_full["Name"].str.upper().str.replace(" .RT STATION.*$","")
  mrt_full = pd.concat([mrt_full.merge(station_geometries, how="left"),
                        mrt_full.merge(exits_data, how="left")])

  # If the official exit name doesn't exist, then use the label by default
  mrt_full["Exit"] = mrt_full[["Exit","Label"]].apply(lambda x: x[1] if pd.isna(x[0]) else x[0], axis=1)
  mrt_full["Labels"] = mrt_full.Label.copy()
  mrt_full["Label"] = mrt_full["Exit"]
  mrt_full = mrt_full.drop("Exit",axis=1)

  mrt_full_column_names = [
    "Label",
    "Name",
    "Chinese",
    "Address",
    "Postcode",
    "Lat",
    "Long",
    "Labels",
    "geometry",
    "Link"
  ]
  mrt_full = mrt_full[mrt_full_column_names]
  
  mrt_full["Name"] = mrt_full["Name"].str.replace(" LRT.*?$","")
  mrt_full["Long"] = mrt_full[["geometry","Long"]].apply(lambda x: x[1] if pd.isna(x[0]) else x[0].x, axis=1)
  mrt_full["Lat"] = mrt_full[["geometry","Lat"]].apply(lambda x: x[1] if pd.isna(x[0]) else x[0].y, axis=1)

  # Splits labels like [EW8, CC9] into two separate rows
  mrt_full["Label"] = mrt_full["Label"].str.split("[,/]")
  mrt_full = gpd.GeoDataFrame(pd.DataFrame(mrt_full).explode("Label"))
  mrt_full["Label"] = mrt_full["Label"].str.strip()
  mrt_full["line"] = mrt_full["Label"].str.extract(r"(\D+)").astype(int).fillna(0)
  mrt_full = mrt_full.query('line != 0')
  
  mrt_full = mrt_full.merge(
    pd.DataFrame(passengers_data\
      .groupby("ORIGIN_PT_CODE")\
      .pipe(lambda x: x.TOTAL_TRIPS.sum())),
    left_on="Label", right_on="ORIGIN_PT_CODE", how="left"
  )
  mrt_full = mrt_full.merge(
    pd.DataFrame(passengers_data\
      .groupby("DESTINATION_PT_CODE")\
      .pipe(lambda x: x.TOTAL_TRIPS.sum())),
    left_on="Label", right_on="DESTINATION_PT_CODE", how="left"
  )
  mrt_full = mrt_full.rename(columns={
    "TOTAL_TRIPS_x": "Origin",
    "TOTAL_TRIPS_y": "Destination"
  })
  
  return mrt_full
  
def get_all_station_info() -> pd.DataFrame:
  all_links: List[str] = get_all_links()
  all_details = list(map(get_station_info_from_link, all_links))
  partial_mrt_data = pd.DataFrame(map_abbr(all_details, get_abbr_map()))
  
  """
	PURPOSE

	As of this point, the information gathered is more than enough for my purposes.
	However, just to finish things off, the following steps take things a whole step further.
	With the help of a couple of datasets from LTA Data Mall, we can now know:
		The locations of the exits to the existing MRT and LRT stations.
		The number of passengers to and from stations.

	I also did a mapping from the labels of the staitons (NS26, EW14) into their respective colors.
	"""
  
  color_map = {
    "EW":"#009645",
    "CG":"#009645",
    "NS":"#D42E12",
    "NE":"#9900AA",
    "CC":"#FA9E0D",
    "CE":"#FA9E0D",
    "DT":"#005EC4",
    "TE":"#9D5B25",
    "JE":"#0099AA",
    "JS":"#0099AA",
    "JW":"#0099AA",
    "CR":"#97C616",
    "CP":"#97C616",
    "PE":"#748477",
    "PW":"#748477",
    "PT":"#748477",
    "ST":"#748477",
    "SE":"#748477",
    "SW":"#748477",
    "BP":"#748477",
    "RT":"#86CEEB"
  }
  
  mrt_full = merge_mrt_data(
    partial_mrt_data,
    get_station_geometries(),
    get_exits_data(),
    get_passengers_data(),
    color_map
  )
  
  return mrt_full
  