import json
import pandas as pd
import requests

path_to_origin_destination_bus = "../Geospatial/GEOSPATIAL/origin_destination_bus_202103.csv"

def get_all_bus_info(account_key: str) -> pd.DataFrame:
  """
	PURPOSE

	I made this code to extract all the kinds of data you'd want to know about bus services and stations:
		Service No
		Operator
		BusStopCode
		Distance to next stop
		Road Name
		Description
		Latitude
		Longitude
		Altitude
		Passenger Inflow
		Passenger Outflow

	Here is the link: https://docs.google.com/spreadsheets/d/e/2PACX-1vQIXKejfbHe2FuPKp0qvdS6OfLDceHGO2WvxGgJtyuoD6HyAmd9Qxj8NZsJA4JItvPcqRKyMJUdDVF-/pub?gid=1421914910&single=true&output=pdf

	Download data for OriginDestinationBus: origin_destination_train_202103.csv
	"""
  bus_routes = []
  starting = 0
  while True:
    try:
      headers = {'AccountKey': account_key}
      results = requests.get('http://datamall2.mytransport.sg/ltaodataservice/BusRoutes?$skip=' + str(starting),headers=headers).text
      results = json.loads(results)
      if len(results['value']) == 0:
        break
      bus_routes.extend(results['value'])
      starting += 500
    except: break

  bus_stops = []
  starting = 0
  while True:
    try:
      headers = {'AccountKey': account_key}
      results = requests.get('http://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip=' + str(starting),headers=headers).text
      results = json.loads(results)
      if len(results['value']) == 0:
        break
      bus_stops.extend(results['value'])
      starting += 500
    except: break

  bus = pd.DataFrame(bus_routes).merge(pd.DataFrame(bus_stops))

  passengers = pd.read_csv(path_to_origin_destination_bus)
  tap_in = passengers.groupby("PT_CODE").pipe(lambda x: x.TOTAL_TAP_IN_VOLUME.sum())
  tap_out = passengers.groupby("PT_CODE").pipe(lambda x: x.TOTAL_TAP_OUT_VOLUME.sum())
  passengers = pd.DataFrame([tap_in, tap_out]).T
  passengers = passengers.reset_index()
  passengers.columns = ['BusStopCode', 'In', 'Out']

  return bus.merge(passengers)