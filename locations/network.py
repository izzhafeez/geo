from typing import Any, Dict, Optional, List

from geom.geo_pt import GeoPt
from geom.line import Line
from .mrt.connection import Connection
from .mrt.platform import Platform
from .mrt.mrt_line import MRTLine, get_mrt_lines
from .mrt.platform_code import PlatformCode
from .mrt.station import Station, Stations

class Network:
    year: int
    station_dict: Dict[PlatformCode, Station]
    platform_dict: Dict[PlatformCode, Platform]
    stations: Stations
    lines: Dict[str, MRTLine]
    
    def __init__(self, year: int=2022):
        self.year = year
        self.stations = Stations.get()
        self.lines = get_mrt_lines()
        self._map_station_dict()
        self._connect_lines()
        
    def _map_station_dict(self) -> None:
        self.station_dict = {}
        self.platform_dict = {}
        for _, station in self.stations.locations.items():
            if isinstance(station, Station):
                for platform in station.platforms:
                    if platform.is_in_service(self.year):
                        self.station_dict[platform.platform_code] = station
                        self.platform_dict[platform.platform_code] = platform
                        prefix = platform.platform_code.prefix
                        if prefix in self.lines:
                            self.lines[prefix].platforms.append(platform)
                        
    def _get_segments(self, line_name):
        line = self.lines[line_name]
        platforms = sorted(line.platforms)

        # Get the closest projections onto the line
        projections: List[GeoPt] = [GeoPt(1,2)]
        for platform in platforms:
            nearest_point = line.get_nearest(platform)[0]
            if nearest_point:
                projections.append(nearest_point)

        segments = []
        curr_start = 0
        for i in range(len(projections)-1):
            lower_proj = projections[i]
            upper_proj = projections[i+1]
            curr_segment = [lower_proj]

            for j in range(curr_start, len(line.coords)-1):
                p1 = line.coords[j]
                p2 = line.coords[j+1]
                min_lat = min(p1[1], p2[1])
                min_lon = min(p1[0], p2[0])
                max_lat = max(p1[1], p2[1])
                max_lon = max(p1[0], p2[0])
                curr_segment.append(GeoPt(p1[1], p1[0]))
                if min_lat <= upper_proj.lat <= max_lat and min_lon <= upper_proj.lon <= max_lon:
                    curr_start = j+1
                    break

            curr_segment.append(upper_proj)

            if i != 0:
                segments.append(curr_segment)
        
        return segments
    
    def _connect_lines(self) -> None:
        for line_name, line in self.lines.items():
            segments = self._get_segments(line_name)
            platforms = sorted(line.platforms)
            for i in range(len(platforms) - 1):
                lower = platforms[i]
                upper = platforms[i+1]
                segment = segments[i]
                connection = Connection(lower, upper, line, segment)
                lower.upper_connection = connection
                upper.lower_connection = connection
    
    @property
    def platforms(self) -> List[Platform]:
        return list(self.platform_dict.values())
            
    def neighbours(self, station: Station) -> List[Station]:
        _list: List[Station] = []
        for platform in station.platforms:
            if platform.upper_neighbour:
                upper_code = platform.upper_neighbour.platform_code
                _list.append(self.station_dict[upper_code])
            if platform.lower_neighbour:
                lower_code = platform.lower_neighbour.platform_code
                _list.append(self.station_dict[lower_code])
        return _list