from __future__ import annotations
from typing import List

from .mrt_line import MRTLine
from ...geom.geo_pt import GeoPt
from ...geom.line import Line
from . import platform

class Connection(Line):
    lower: platform.Platform
    upper: platform.Platform
    line: MRTLine
    
    def __init__(self,
                 lower: platform.Platform,
                 upper: platform.Platform,
                 line: MRTLine,
                 segment: List[GeoPt]):
        super().__init__(segment)
        self.lower = lower
        self.upper = upper
        self.line = line
    
    # def split_on(self, mid: locations.mrt.platform.Platform) -> None:
    #     lower_connection = Connection(self.lower, mid, self.line)
    #     upper_connection = Connection(mid, self.upper, self.line)
    #     self.lower.upper_connection = lower_connection
    #     self.upper.lower_connection = upper_connection
    #     mid.lower_connection = lower_connection
    #     mid.upper_connection = upper_connection