from .out_of_bounds_error import OutOfBoundsError

class OutOfSingaporeError(OutOfBoundsError):
    MIN_LAT = 1.23776
    MIN_LON = 103.61751
    MAX_LAT = 1.47066
    MAX_LON = 104.04360
    def __init__(self, lat, lon):
        if lat < OutOfSingaporeError.MIN_LAT or lat > OutOfSingaporeError.MAX_LAT:
            super().__init__(lat, OutOfSingaporeError.MIN_LAT, OutOfSingaporeError.MAX_LAT)
        elif lon < OutOfSingaporeError.MIN_LON or lon > OutOfSingaporeError.MAX_LON:
            super().__init__(lon, OutOfSingaporeError.MIN_LON, OutOfSingaporeError.MAX_LON)
        else:
            pass