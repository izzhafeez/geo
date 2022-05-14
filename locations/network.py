from typing import Dict, Optional, List

from .mrt.connection import Connection
from .mrt.platform import Platform
from .mrt.station import Station, Stations
from .mrt.station_code import StationCode

class Network:
    year: int
    station_dict: Dict[StationCode, Station]
    platform_dict: Dict[StationCode, Platform]
    stations: Stations
    
    def __init__(self, year: int=2022):
        self.year = year
        self.stations = Stations.get()
        self._map_station_dict()
        self._connect_stations()
        
    def _map_station_dict(self) -> None:
        self.station_dict = {}
        self.platform_dict = {}
        for _, station in self.stations.locations.items():
            if isinstance(station, Station):
                for platform in station.platforms:
                    self.station_dict[platform.platform_code] = station
                    self.platform_dict[platform.platform_code] = platform
    
    def _connect_stations(self) -> None:
        for _, station in self.stations.locations.items():
            if isinstance(station, Station):
                self._connect_platforms(station)
    
    def _connect_platforms(self, station: Station) -> None:
        for platform in station.platforms:
            if platform.is_in_service(self.year):
                self._map_upper_platform(platform)
                self._map_lower_platform(platform)
    
    def _map_upper_platform(self, platform: Platform) -> None:
        curr_platform: Platform = platform
        curr_code: StationCode = curr_platform.platform_code
        while True:
            next_code = curr_code.next_code
            if next_code is None:
                platform.upper_connection = None
                return
            next_platform = self.platform_dict.get(next_code)
            curr_code = next_code
            if next_platform is not None and next_platform.is_in_service(self.year):
                curr_platform = next_platform
                connection = Connection(platform, curr_platform, next_code.line)
                platform.upper_connection = connection
                curr_platform.lower_connection = connection
                break
    
    def _map_lower_platform(self, platform: Platform) -> None:
        curr_platform: Platform = platform
        curr_code: StationCode = curr_platform.platform_code
        while True:
            prev_code = curr_code.prev_code
            if prev_code is None:
                platform.lower_connection = None
                return
            prev_platform = self.platform_dict.get(prev_code)
            curr_code = prev_code
            if prev_platform is not None and prev_platform.is_in_service(self.year):
                curr_platform = prev_platform
                connection = Connection(curr_platform, platform, prev_code.line)
                platform.lower_connection = connection
                curr_platform.upper_connection = connection
                break
            
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