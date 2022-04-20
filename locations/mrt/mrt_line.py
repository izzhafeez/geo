from enum import Enum, auto
from typing import List, Optional

from color.color import Color
from geom.geo_pt import GeoPt
from geom.line import Line

class MRTLine(Line):
    name: str
    color: Color
    
    def __init__(self, color: Color, line: Optional[List[GeoPt]]):
        super(Line, self).__init__(line)
        self.color = color
    
class MRTLines(Enum):
    EW = MRTLine(Color.from_hex("009645"), None)
    NS = MRTLine(Color.from_hex("D42E12"), None)
    NE = MRTLine(Color.from_hex("9900AA"), None)
    CC = MRTLine(Color.from_hex("FA9E0D"), None)
    DT = MRTLine(Color.from_hex("005EC4"), None)
    TE = MRTLine(Color.from_hex("9D5B25"), None)
    JR = MRTLine(Color.from_hex("0099AA"), None)
    CR = MRTLine(Color.from_hex("97C616"), None)
    LRT = MRTLine(Color.from_hex("748477"), None)