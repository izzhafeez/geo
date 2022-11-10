class OutOfBoundsError(ValueError):
    def __init__(self, v, min_v, max_v):
        super().__init__(f"value given was {v}, but should be between {min_v} and {max_v}")