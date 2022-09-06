class InvalidHexError(ValueError):
    def __init__(self, value: str):
        super().__init__(f"{value} not accepted as a valid hex string.")