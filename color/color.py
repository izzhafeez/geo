from __future__ import annotations
from dataclasses import dataclass

from error.value_error.invalid_hex_error import InvalidHexError

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