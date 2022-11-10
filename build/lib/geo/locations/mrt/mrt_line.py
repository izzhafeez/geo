from __future__ import annotations
from os.path import join, dirname
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from shapely import geometry
import fiona
import geopandas as gpd

from ...color.color import Color
from ...geom.geo_pt import GeoPt
from ...geom.line import Line

if TYPE_CHECKING:
    from . import platform

class MRTLine(Line):
    name: str
    color: Color
    platforms: List[platform.Platform]
    
    def __init__(self, name: str, color: Color, line: Optional[List[GeoPt]]):
        super(Line, self).__init__(line)
        self.name = name
        self.color = color
        self.platforms = []
        
    def __str__(self) -> str:
        return f"<MRTLine: {self.name}>"
    
    def __repr__(self) -> str:
        return f"<MRTLine: {self.name}>"
    
def get_mrt_lines() -> Dict[str, MRTLine]:
    MRT_LINES = {}
    
    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    lines = gpd.read_file(join(dirname(__file__), "assets/mrt-line.kml"))
    lines.loc[5:8,"geometry"] = lines.loc[5:8, "geometry"].boundary
    lines.drop(columns=["Description"], inplace=True)
    lines.Name = lines.Name.str.extract("([^L]+)")
    lines_dict = lines.set_index("Name").to_dict("index")
    lines_dict["CE"] = {}
    lines_dict["CE"]["geometry"] = geometry.LineString(list(GeoPt(x[1], x[0]) for x in lines_dict["CC"]["geometry"].coords[346:][::-1]))
    
    color_mapping = {
        "EW": "009645",
        "CG": "009645",
        "NS": "D42E12",
        "NE": "9900AA",
        "CC": "FA9E0D",
        "CE": "FA9E0D",
        "DT": "005EC4",
        "TE": "9D5B25",
        "JS": "0099AA",
        "JE": "0099AA",
        "JW": "0099AA",
        "CR": "97C616",
        "CP": "97C616",
        "SE": "748477",
        "SW": "748477",
        "PE": "748477",
        "PW": "748477",
        "BP": "748477",
    }
    
    for name, data in lines_dict.items():
        MRT_LINES[name] = MRTLine(name,
                                  Color.from_hex(color_mapping[name]),
                                  [GeoPt(x[1], x[0]) for x in data["geometry"].coords])
    return MRT_LINES
    