from typing import Any, Callable, Generic, Optional, TypeVar

from .avltree_v2 import AVLTree
from .comparable import Comparable

T = TypeVar("T", bound=Comparable)
U = TypeVar("U")

class PriorityQueue(Generic[U, T]):
    """
    Encapsulates a PriorityQueue to enq and deq items in O(logN) time.

    Fields:
        tree (AVLTree[T]): the tree to keep track of the items.
    """
    tree: AVLTree[U, T]
    
    def __init__(self, comparator: Callable[[U], T]):
        self.tree = AVLTree[U, T](comparator)
        
    def is_empty(self) -> bool:
        return self.tree.root == None
    
    def enq(self, val: U) -> None:
        self.tree.insert(val)
        
    def deq(self) -> Optional[U]:
        min_val: Optional[U] = self.tree.get_min_value()
        self.tree.delete(min_val)
        return min_val