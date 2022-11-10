from __future__ import annotations
from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional

import numpy as np

# from .platform_code import PlatformCode
from . import connection, platform_code
from ...locations.location import Location

class Platform(Location):
    platform_code: platform_code.PlatformCode
    opening_year: Optional[int]
    closing_year: Optional[int]
    lower_connection: Optional[connection.Connection] = field(default=None, init=False)
    upper_connection: Optional[connection.Connection] = field(default=None, init=False)
    
    def __init__(self, name: str, **kwargs):
        fields = ["lat", "lon", "shape", "platform_code", "opening_year", "closing_year"]
        self._try_setter(fields, kwargs)
        self.lower_connection = None
        self.upper_connection = None
        super().__init__(name, lat=self.lat, lon=self.lon, shape=self.shape)
        
    def __eq__(self, other: Platform):
        return self.platform_code == other.platform_code
    
    def __lt__(self, other: Platform):
        return self.platform_code < other.platform_code
    
    def is_in_service(self, year: int) -> bool:
        return ((self.opening_year is None or np.isnan(self.opening_year) or self.opening_year <= year)
                and (self.closing_year is None or np.isnan(self.closing_year) or year <= self.closing_year))
    
    @property    
    def upper_neighbour(self) -> Optional[Platform]:
        if self.upper_connection is not None:
            return self.upper_connection.upper
        return None

    @property
    def lower_neighbour(self) -> Optional[Platform]:
        if self.lower_connection is not None:
            return self.lower_connection.lower
        return None