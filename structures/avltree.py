from __future__ import annotations
from typing import Any, List, Tuple

class AVLTree:
    class Node:
        val: Any
        left: AVLTree.Node
        right: AVLTree.Node
        height: int
        count: int
        weight: int

        def __init__(self, val: Any):
            self.val = val
            self.left = None
            self.right = None
            self.height = 1
            self.count = 1
            self.weight = 1
            
    def __init__(self):
        self.root = None
    
    def insert(self, key: Any) -> None:
        def insert_helper(node: AVLTree.Node, key: Any) -> AVLTree.Node:
            if not node:
                return AVLTree.Node(key)
            elif key < node.val:
                node.left = insert_helper(node.left, key)
            elif key > node.val:
                node.right = insert_helper(node.right, key)
            else:
                node.count += 1
            self.set_height(node)
            self.set_weight(node)
            
            balance = self.get_balance(node)

            if balance > 1 and key < node.left.val:
                return self.right_rotate(node)
            if balance < -1 and key > node.right.val:
                return self.left_rotate(node)
            if balance > 1 and key > node.left.val:
                node.left = self.left_rotate(node.left)
                return self.right_rotate(node)
            if balance < -1 and key < node.right.val:
                node.right = self.right_rotate(node.right)
                return self.left_rotate(node)

            return node
        self.root = insert_helper(self.root, key)

    def delete(self, key: Any) -> None:
        def delete_helper(node: AVLTree.Node, key: Any) -> AVLTree.Node:
            if not node:
                return None
            elif key < node.val:
                node.left = delete_helper(node.left, key)
            elif key > node.val:
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
                node.val = temp.val
                node.count = temp.count
                node.right = delete_helper(node.right, temp.val)
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
        self.root = delete_helper(self.root, key)
 
    def left_rotate(self, node: AVLTree.Node) -> AVLTree.Node:
        right = node.right
        right_left = right.left
        right.left = node
        node.right = right_left
 
        self.set_height(node)
        self.set_weight(node)
        self.set_height(right)
        self.set_weight(right)
        return right
 
    def right_rotate(self, node: AVLTree.Node) -> AVLTree.Node:
        left = node.left
        left_right = left.right
        left.right = node
        node.left = left_right
 
        self.set_height(node)
        self.set_weight(node)
        self.set_height(left)
        self.set_weight(left)
        return left
    
    def get_val(self, node: AVLTree.Node) -> Any:
        if not node:
            return None
        return node.val
 
    def get_height(self, node: AVLTree.Node) -> int:
        if not node:
            return 0
        return node.height
    
    def set_height(self, node: AVLTree.Node) -> None:
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        
    def get_weight(self, node: AVLTree.Node) -> int:
        if not node:
            return 0
        return node.weight
    
    def set_weight(self, node: AVLTree.Node) -> None:
        node.weight = node.count + self.get_weight(node.left) + self.get_weight(node.right)
 
    def get_balance(self, node: AVLTree.Node) -> int:
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)
    
    def get_min_value(self) -> Any:
        def get_min_value_helper(node: AVLTree.Node) -> Any:
            if not node:
                return None
            elif not node.left:
                return node.val
            return get_min_value_helper(node.left)
        return get_min_value_helper(self.root)
    
    def get_min_value_node(self, node: AVLTree.Node) -> AVLTree.Node:
        if node is None or node.left is None:
            return node
        return self.get_min_value_node(node.left)

    def in_order(self) -> List[Any]:
        L = []
        def in_order_helper(node: AVLTree.Node):
            if not node:
                return None
            in_order_helper(node.left)
            L.append(node.val)
            in_order_helper(node.right)
        in_order_helper(self.root)
        return L
    
    def pre_order(self) -> List[Tuple[Any, Any, Any]]:
        L = []
        def pre_order_helper(node: AVLTree.Node):
            if not node:
                return None
            else:
                L.append((self.get_val(node), self.get_val(node.left), self.get_val(node.right)))
                pre_order_helper(node.left)
                pre_order_helper(node.right)
        pre_order_helper(self.root)
        return L
    
    def get_rank(self, key: Any) -> int:
        def rank_helper(node: AVLTree.Node, key: Any) -> int:
            if not node:
                return 0
            else:
                if key < node.val:
                    return rank_helper(node.left, key)
                elif key > node.val:
                    return self.get_weight(node) - self.get_weight(node.right) + rank_helper(node.right, key)
                else:
                    return self.get_weight(node.left)
        return rank_helper(self.root, key) + 1
    