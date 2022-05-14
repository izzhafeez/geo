from __future__ import annotations
from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional

import numpy as np

from .mrt_line import MRTLine
from .station_code import StationCode
import locations.mrt.connection

@dataclass
class Platform:
    platform_code: StationCode
    opening_year: Optional[int]
    closing_year: Optional[int]
    lower_connection: Optional[locations.mrt.connection.Connection] = field(default=None, init=False)
    upper_connection: Optional[locations.mrt.connection.Connection] = field(default=None, init=False)
    
    def __str__(self) -> str:
        lower = self.lower_neighbour.platform_code.code if self.lower_neighbour else None
        upper = self.upper_neighbour.platform_code.code if self.upper_neighbour else None
        return f"<Platform: {self.platform_code.code}, Neighbours: ({lower}, {upper})>"
    
    def __repr__(self) -> str:
        return f"<Platform: {self.platform_code.code}>"
    
    def is_in_service(self, year: int) -> bool:
        return ((self.opening_year is None or np.isnan(self.opening_year) or self.opening_year <= year)
                and (self.closing_year is None or np.isnan(self.closing_year) or year <= self.closing_year))
    
    @cached_property
    def line(self) -> MRTLine:
        return self.platform_code.line
    
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