class Color():
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def get_diff(self, r, g, b):
        return abs(r-self.r) + abs(g-self.g) + abs(b-self.b)