from typing import Any

from .avltree import AVLTree

class PriorityQueue:
    """
    Encapsulates a PriorityQueue to enq and deq items in O(logN) time.

    Fields:
        tree (AVLTree): the tree to keep track of the items.
    """
    tree: AVLTree

    def __init__(self):
        self.tree = AVLTree()
        
    def is_empty(self) -> bool:
        return self.tree.root == None
    
    def enq(self, val: Any) -> None:
        self.tree.insert(val)
        
    def deq(self) -> Any:
        min_val = self.tree.get_min_value()
        self.tree.delete(min_val)
        return min_val