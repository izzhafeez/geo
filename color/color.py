class Color:
    def __init__(self, r: float, g: float, b: float):
        self.r = r
        self.g = g
        self.b = b

    def get_diff(self, r: float, g: float, b: float) -> float:
        return abs(r-self.r) + abs(g-self.g) + abs(b-self.b)