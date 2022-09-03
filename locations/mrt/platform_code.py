from __future__ import annotations
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, Optional, Set, Tuple
import re

from .mrt_line import MRTLine, get_mrt_lines

class PlatformCode:
    code: str
    
    _lower_terminuses: Set[str] = {"EW1", "CG0",
                                   "NS1", "BP1",
                                   "NE1", "PW0", "PE0", "SE0", "SW0",
                                   "CC1", "CE0",
                                   "DT0",
                                   "TE1",
                                   "JE0", "JS1", "JW0",
                                   "CR1", "CP1",}
    _upper_terminuses: Set[str] = {"EW33", "CG2",
                                   "NS28", "BP14",
                                   "NE18", "PW8", "PE8", "SE6", "SW9",
                                   "CC35", "CE2",
                                   "DT37",
                                   "TE31",
                                   "JE7", "JS12", "JW5",
                                   "CR13", "CP4",}
    _exceptions: Dict[str, Tuple[str, str]] = {"NS3": ("NS2", "NS3A"),
                                               "NS4": ("NS3A", "NS5"),
                                               "NS3A": ("NS3", "NS4"),
                                               "TE22": ("TE21", "TE22A"),
                                               "TE23": ("TE22A", "TE24"),
                                               "TE22A": ("TE22", "TE23"),}
    _line_mapping: Dict[str, str] = {"CP": "CR",
                                     "CE": "CC",
                                     "CG": "EW",}
    
    MRT_LINES = get_mrt_lines()
    
    def __init__(self, code: str):
        self.code = code
    
    def __eq__(self, other: PlatformCode) -> bool:
        return self.code == other.code
    
    def __lt__(self, other: PlatformCode) -> bool:
        return self.number < other.number
    
    def __hash__(self) -> int:
        return hash(self.code)
    
    def __str__(self) -> str:
        return f"<PlatformCode: {self.code}>"

    def __repr__(self) -> str:
        return f"<PlatformCode: {self.code}>"
    
    @cached_property
    def prefix(self) -> str:
        return re.findall(r"[A-Z]+", self.code)[0]
    
    @cached_property
    def number(self) -> int:
        regex_search_result = re.findall(r"\d+", self.code)
        if len(regex_search_result) == 0:
            return 0
        return int(regex_search_result[0])
    
    @cached_property
    def suffix(self) -> Optional[str]:
        regex_search_result = re.findall(r"[A-Z]+", self.code)
        if len(regex_search_result) < 2:
            return None
        return regex_search_result[1]
    
    @cached_property
    def is_lower_terminus(self) -> bool:
        return self.code in PlatformCode._lower_terminuses
    
    @cached_property
    def is_higher_terminus(self) -> bool:
        return self.code in PlatformCode._upper_terminuses
    
    @cached_property
    def next_code(self) -> Optional[PlatformCode]:
        if self.is_higher_terminus:
            return None
        if self.code in PlatformCode._exceptions:
            return PlatformCode(PlatformCode._exceptions[self.code][1])
        return PlatformCode(self.prefix + str(self.number + 1))
    
    @cached_property
    def prev_code(self) -> Optional[PlatformCode]:
        if self.is_lower_terminus:
            return None
        if self.code in PlatformCode._exceptions:
            return PlatformCode(PlatformCode._exceptions[self.code][0])
        return PlatformCode(self.prefix + str(self.number - 1))
        
    @cached_property
    def line(self) -> MRTLine:
        if self.prefix in PlatformCode._line_mapping:
            new_prefix = PlatformCode._line_mapping[self.prefix]
            line = PlatformCode.MRT_LINES[new_prefix]
            if line is not None:
                return line
        line = PlatformCode.MRT_LINES[self.prefix]
        if line is not None:
            return line
        raise ValueError(self.prefix)