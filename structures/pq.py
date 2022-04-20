from typing import Any, Generic, Optional, TypeVar

from .avltree import AVLTree
from .comparable import Comparable

T = TypeVar("T", bound=Comparable)

class PriorityQueue(Generic[T]):
    """
    Encapsulates a PriorityQueue to enq and deq items in O(logN) time.

    Fields:
        tree (AVLTree[T]): the tree to keep track of the items.
    """
    tree: AVLTree[T]
    
    def __init__(self):
        self.tree = AVLTree[T]()
        
    def is_empty(self) -> bool:
        return self.tree.root == None
    
    def enq(self, val: T) -> None:
        self.tree.insert(val)
        
    def deq(self) -> Optional[T]:
        min_val: Optional[T] = self.tree.get_min_value()
        self.tree.delete(min_val)
        return min_val