from __future__ import annotations
from dataclasses import dataclass

from ..error.value_error.invalid_hex_error import InvalidHexError

@dataclass(frozen=True)
class Color:
    r: float
    g: float
    b: float

    def get_diff(self, r: float, g: float, b: float) -> float:
        return abs(r-self.r) + abs(g-self.g) + abs(b-self.b)
    
    def get_diff_from_color(self, color: Color) -> float:
        return self.get_diff(color.r, color.g, color.b)
    
    @staticmethod
    def from_hex(hex: str) -> Color:
        if len(hex) != 6:
            raise InvalidHexError(hex)
        r = int(hex[0:2], 16)
        g = int(hex[2:4], 16)
        b = int(hex[4:6], 16)
        return Color(r, g, b)
    
    def to_hex(self) -> str:
        r_hex = hex(int(self.r))[2:]
        if len(r_hex) == 1:
            r_hex = "0" + r_hex
            
        g_hex = hex(int(self.g))[2:]
        if len(g_hex) == 1:
            g_hex = "0" + g_hex
            
        b_hex = hex(int(self.b))[2:]
        if len(b_hex) == 1:
            b_hex = "0" + b_hex
            
        return r_hex + g_hex + b_hex