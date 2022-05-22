from .avltree import AVLTree
from typing import Any, Callable, Dict, Generic, List, Optional, Set, Tuple, TypeVar

from .comparable import Comparable

T = TypeVar("T", bound=Comparable)
U = TypeVar("U")

class PriorityQueue(Generic[U, T]):
    """
    Encapsulates a PriorityQueue to enq and deq items in O(logN) time.

    Fields:
        tree (AVLTree[T]): the tree to keep track of the items.
    """
    tree: AVLTree[T]
    keys: Dict[T, List[U]]
    reverse_keys: Dict[U, T]
    comparator: Callable[[U], T]
    
    def __init__(self, comparator: Callable[[U], T]):
        self.tree = AVLTree[T]()
        self.keys = {}
        self.reverse_keys = {}
        self.comparator = comparator
        
    def is_empty(self) -> bool:
        return self.tree.root is None
    
    def enq(self, value: U) -> None:
        key = self.comparator(value)
        if key not in self.keys:
            self.keys[key] = [value]
        else:
            self.keys[key].append(value)
        self.tree.insert(key)
        self.reverse_keys[value] = key
    
    def deq(self) -> Optional[U]:
        key = self.tree.get_min_value()
        if key is None:
            return
        self.tree.delete(key)
        return self.keys[key].pop()
    
    def update(self, value: U) -> None:
        key = self.comparator(value)
        if value in self.reverse_keys:
            old_key = self.reverse_keys[value]
            self.keys[old_key].remove(value)
            self.reverse_keys[value] = key
            self.tree.delete(key)
        self.enq(value)
        
            