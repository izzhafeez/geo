from __future__ import annotations
from typing import Any, Generic, List, Optional, Tuple, TypeVar

from .comparable import Comparable

T = TypeVar("T", bound=Comparable)

class Node(Generic[T]):
    """
    Encapsulates a Node of the AVLTree.
    
    Fields:
        key (U): the value to be assigned to the node.
        left (Optional[Node[T]]): the left child of the node.
        right (Optional[Node[T]]): the right child of the node.
        height (int): the height of the tree rooted at the node.
        count (int): duplicate values are captured here, so we can have nodes with >1 counts.
        weight (int): the number of nodes on the tree rooted at the node.
    """
    key:    T
    left:   Optional[Node[T]]
    right:  Optional[Node[T]]
    height: int
    count:  int
    weight: int

    def __init__(self, key: T):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1
        self.count = 1
        self.weight = 1

class AVLTree(Generic[T]):
    """
    Encapsulates an AVLTree capable of performing rotations, insertions and deletions.

    Fields:
        root (Optional[Node[T]]): the root of the tree.
    """
    root: Optional[Node[T]]
            
    def __init__(self):
        self.root = None
    
    def insert(self, key: T) -> None:
        """
        Inserts a key to the tree, triggering rotations.
        If the key already exists, then increment the key's count.
        Must be comparable or else the < > operators won't work.

        Args:
            key (T): key to be added.
        """
        def insert_helper(node: Optional[Node[T]], key: T) -> Optional[Node[T]]:
            if not node:
                return Node[T](key)
            elif key < node.key:
                node.left = insert_helper(node.left, key)
            elif key > node.key:
                node.right = insert_helper(node.right, key)
            else:
                node.count += 1
            self.set_height(node)
            self.set_weight(node)
            
            balance = self.get_balance(node)
            
            left_key = self.get_key(node.left)
            right_key = self.get_key(node.right)

            if balance > 1 and key < left_key:
                return self.right_rotate(node)
            if balance < -1 and right_key and key > right_key:
                return self.left_rotate(node)
            if balance > 1 and left_key and key > left_key:
                node.left = self.left_rotate(node.left)
                return self.right_rotate(node)
            if balance < -1 and key < right_key:
                node.right = self.right_rotate(node.right)
                return self.left_rotate(node)

            return node
        self.root = insert_helper(self.root, key)

    def delete(self, key: Optional[T]) -> None:
        """
        Deletes a key from the tree, triggering rotations.
        If the key has onle one count, then remove it from the tree.
        Otherwise, just decrement its count and update weights along the way.

        Args:
            key (T): key to be deleted.
        """
        def delete_helper(node: Optional[Node[T]], key: T) -> Optional[Node[T]]:
            if not node:
                return None
            elif key < node.key:
                node.left = delete_helper(node.left, key)
            elif key > node.key:
                node.right = delete_helper(node.right, key)
            elif node.count > 1:
                node.count -= 1
            else:
                if node.left is None:
                    temp = node.right
                    node = None
                    return temp
                elif node.right is None:
                    temp = node.left
                    node = None
                    return temp
                temp = self.get_min_value_node(node.right)
                node.key = temp.key
                node.count = temp.count
                node.right = delete_helper(node.right, temp.key)
            if not node:
                return node
            self.set_height(node)
            self.set_weight(node)
            balance = self.get_balance(node)

            if balance > 1 and self.get_balance(node.left) >= 0:
                return self.right_rotate(node)
            if balance < -1 and self.get_balance(node.right) <= 0:
                return self.left_rotate(node)
            if balance > 1 and self.get_balance(node.left) < 0:
                node.left = self.left_rotate(node.left)
                return self.right_rotate(node)
            if balance < -1 and self.get_balance(node.right) > 0:
                node.right = self.right_rotate(node.right)
                return self.left_rotate(node)
            return node
        if key is not None:
            self.root = delete_helper(self.root, key)
 
    def left_rotate(self, node: Optional[Node[T]]) -> Optional[Node[T]]:
        """
        Rotates the node left.

        Args:
            node (Optional[Node[T]]): node to be rotated.

        Returns:
            Optional[Node[T]]: the resulting root node.
        """
        if not node or not node.right:
            return node
        right = node.right
        right_left = right.left
        right.left = node
        node.right = right_left
 
        self.set_height(node)
        self.set_weight(node)
        self.set_height(right)
        self.set_weight(right)
        return right
 
    def right_rotate(self, node: Optional[Node[T]]) -> Optional[Node[T]]:
        """
        Rotates the node right.

        Args:
            node (Optional[Node[T]]): node to be rotated.

        Returns:
            Optional[Node[T]]: the resulting root node.
        """
        if not node or not node.left:
            return node
        left = node.left
        left_right = left.right
        left.right = node
        node.left = left_right
 
        self.set_height(node)
        self.set_weight(node)
        self.set_height(left)
        self.set_weight(left)
        return left
    
    def get_key(self, node: Optional[Node[T]]) -> Optional[T]:
        if not node:
            return None
        return node.key
 
    def get_height(self, node: Optional[Node[T]]) -> int:
        if not node:
            return 0
        return node.height
    
    def set_height(self, node: Node[T]) -> None:
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        
    def get_weight(self, node: Optional[Node[T]]) -> int:
        if not node:
            return 0
        return node.weight
    
    def set_weight(self, node: Node[T]) -> None:
        node.weight = node.count + self.get_weight(node.left) + self.get_weight(node.right)
 
    def get_balance(self, node: Optional[Node[T]]) -> int:
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)
    
    def get_min_value(self) -> Optional[T]:
        """
        Gets the minimum value of the tree.

        Returns:
            T: the minimum value.
        """
        def get_min_value_helper(node: Optional[Node[T]]) -> Optional[T]:
            if not node:
                return None
            elif not node.left:
                return node.key
            return get_min_value_helper(node.left)
        return get_min_value_helper(self.root)
    
    def get_min_value_node(self, node: Node[T]) -> Node[T]:
        """
        Get the node containing the minimum value in the tree rooted at this node.

        Args:
            node (Node[T]): node to be queried.

        Returns:
            Node: node containing the minimum value.
        """
        if node is None or node.left is None:
            return node
        return self.get_min_value_node(node.left)

    def in_order(self) -> List[T]:
        """
        In order traversal of the tree done by recursion.

        Returns:
            List[T]: a list of keys in the tree in ascending order.
        """
        L = []
        def in_order_helper(node: Optional[Node[T]]) -> None:
            if not node:
                return
            in_order_helper(node.left)
            L.append(node.key)
            in_order_helper(node.right)
        in_order_helper(self.root)
        return L
    
    def pre_order(self) -> List[T]:
        """
        Pre order traversal of the tree done by recursion.

        Returns:
            List[T]: a list of keys in the tree in pre order.
        """
        L = []
        def pre_order_helper(node: Optional[Node[T]]) -> None:
            if not node:
                return
            L.append(node.key)
            pre_order_helper(node.left)
            pre_order_helper(node.right)
        pre_order_helper(self.root)
        return L
    
    def get_rank(self, key: T) -> int:
        """
        Gets the rank of a particular key in the tree.
        Does take into account duplicate values.

        Args:
            key (T): key to be queried.

        Returns:
            int: its rank, starting from 1.
        """
        def rank_helper(node: Optional[Node[T]], key: T) -> int:
            if not node:
                return 0
            elif key < node.key:
                return rank_helper(node.left, key)
            elif key > node.key:
                return self.get_weight(node) - self.get_weight(node.right) + rank_helper(node.right, key)
            return self.get_weight(node.left)
        return rank_helper(self.root, key) + 1
    