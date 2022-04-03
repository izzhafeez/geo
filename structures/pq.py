from .avltree import AVLTree
from typing import Any

class PriorityQueue:
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