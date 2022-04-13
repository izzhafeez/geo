from typing import Any, Optional

def is_float(x: Optional[Any]):
    if not x:
        return False
    try:
        y = float(x)
        return True
    except ValueError:
        return False