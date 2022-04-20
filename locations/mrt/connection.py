from __future__ import annotations
from dataclasses import dataclass

from .mrt_line import MRTLine
from .platform import Platform

@dataclass
class Connection:
    lower: Platform
    upper: Platform
    line: MRTLine
    
    def split_on(self, mid: Platform) -> None:
        lower_connection = Connection(self.lower, mid, self.line)
        upper_connection = Connection(mid, self.upper, self.line)
        self.lower.upper_connection = lower_connection
        self.upper.lower_connection = upper_connection
        mid.lower_connection = lower_connection
        mid.upper_connection = upper_connection