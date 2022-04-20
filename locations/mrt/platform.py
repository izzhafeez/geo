from dataclasses import dataclass, field
from typing import Optional

from .connection import Connection
from .station_code import StationCode

@dataclass
class Platform:
    station_code: StationCode
    lower_connection: Optional[Connection] = field(default=None, init=False)
    upper_connection: Optional[Connection] = field(default=None, init=False)