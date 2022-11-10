from os.path import dirname, join
from tqdm import tqdm

import geopandas as gpd

def get_all_roads_info():
  """
  PURPOSE

  I made this code to extract combine road data with planning area data.
  It is used to find roads within any particular planning area.

  Download data for road network: master-plan-2019-road-name-layer/road-network.kml
  Download data for planning areas: subzone-census-2010/Subzone_Census2010.kml
  """
  path_to_road_network = join(dirname(__file__), "assets/road-network.kml")
  path_to_planning_areas = join(dirname(__file__), "assets/Subzone_Census2010.kml")


  gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw' # type: ignore [no-redef]
  roads = gpd.read_file(path_to_road_network, driver='KML')
  roads["Name"] = roads.Description.str.extract("<td>(.*?)</td>")
  roads["Type"] = roads.Description.str.extract("RD_TYP_CD</th>.*?<td>(.*?)</td>")
  roads = roads.drop("Description",axis=1)

  planning = gpd.read_file(path_to_planning_areas, driver='KML')
  planning["SubzoneCode"] = planning.Description.str.extract("Subzone Code.*?<td>(.*?)</td>")
  planning["Planning"] = planning.Description.str.extract("Planning Area Name.*?<td>(.*?)</td>")
  planning["PlanningCode"] = planning.Description.str.extract("Planning Area Code.*?<td>(.*?)</td>")
  planning["Region"] = planning.Description.str.extract("Region Name.*?<td>(.*?)</td>")
  planning["RegionCode"] = planning.Description.str.extract("Region Code.*?<td>(.*?)</td>")
  planning = planning.rename(columns={"Name":"Subzone"})
  planning = planning.drop("Description",axis=1)
  planning = planning[['Region', 'RegionCode', 'Planning', 'PlanningCode', 'Subzone', 'SubzoneCode', 'geometry']]

  roadsm = roads.values.tolist()
  planningm = planning.values.tolist()

  roads = []
  for road, line, rType in tqdm(roadsm):
    appeared = False
    for *details, shape in planningm:
      if line.within(shape) or line.intersects(shape):
        roads.append((road, rType, line) + tuple(details))
        appeared = True
    if not appeared:
      roads.append((road, rType, line) + ("",)*6)

  roads = gpd.GeoDataFrame(roads)
  roads.columns = ["Road", "Type", "geometry", "Region", "RegionCode", "Planning", "PlanningCode", "Subzone", "SubzoneCode"]

  return roads