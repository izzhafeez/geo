from __future__ import annotations
from abc import abstractmethod
from typing import Any, Protocol

class Comparable(Protocol):
    @abstractmethod
    def __lt__(self: Any, other: Any) -> bool:
        pass