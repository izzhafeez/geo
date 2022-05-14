# from enum import Enum, auto
from typing import List, Optional

from color.color import Color
from geom.geo_pt import GeoPt
from geom.line import Line

class MRTLine(Line):
    name: str
    color: Color
    
    def __init__(self, name: str, color: Color, line: Optional[List[GeoPt]]):
        super(Line, self).__init__(line)
        self.name = name
        self.color = color
        
    def __str__(self) -> str:
        return f"<MRTLine: {self.name}>"
    
    def __repr__(self) -> str:
        return f"<MRTLine: {self.name}>"
    
class MRTLines:
    _dict = {"EW": MRTLine("EW", Color.from_hex("009645"), None),
             "NS": MRTLine("NS", Color.from_hex("D42E12"), None),
             "NE": MRTLine("NE", Color.from_hex("9900AA"), None),
             "CC": MRTLine("CC", Color.from_hex("FA9E0D"), None),
             "DT": MRTLine("DT", Color.from_hex("005EC4"), None),
             "TE": MRTLine("TE", Color.from_hex("9D5B25"), None),
             "JR": MRTLine("JR", Color.from_hex("0099AA"), None),
             "CR": MRTLine("CR", Color.from_hex("97C616"), None),
             "LRT": MRTLine("LRT", Color.from_hex("748477"), None)}
    
    @staticmethod
    def get(line: str) -> Optional[MRTLine]:
        return MRTLines._dict.get(line)