from typing import Any, Callable, List, Optional, Tuple, TypeVar

from .comparable import Comparable

T = TypeVar("T")

def swap(arr: List, i: int, j: int) -> None:
    """
    Swaps two entries in a list.

    Args:
        arr (List): array to be swapped.
        i (int): first index to be swapped.
        j (int): second index to be swapped.
    """
    arr[i], arr[j] = arr[j], arr[i]

def partition(arr: List[T], low: int, high: int, comparator: Callable[[T], Any]=lambda x: x) -> int:
    """
    Partition method to assist with Quick Select and Quick Sort algorithms.
    Partition will segment the array based on its last element (pivot).
    Values smaller than the pivot are to its left and
        values greater than the pivot are to its right.
    Comparator can be called for more custom comparisons.

    Args:
        arr (List[T]): array to be partitioned.
        low (int): start index of the subarray to be partitioned.
        high (int): end index of the subarray to be partitioned.
        comparator (T, optional): basis of comparison. Defaults to lambda x: x.

    Returns:
        T: the index of the pivot after everything is shifted.
    """
    i = low - 1
    pivot = arr[high]
 
    for j in range(low, high):
        if not comparator(arr[j]) > comparator(pivot):
            i += 1
            swap(arr, i, j)
 
    swap(arr, i+1, high)
    return i + 1

def quick_sort(arr: List[T],
               comparator: Callable[[T], Any]=lambda x: x
               ) -> List[T]:
    """
    Implementation of the Quick Sort algorithm, accomodating a custom comparator.

    Args:
        arr (List[T]): array to be sorted.
        comparator (T, optional): basis of comparison. Defaults to lambda x: x.

    Returns:
        List[T]: sorted list.
    """
    def quick_sort_helper(low: int, high: int) -> None:
        """
        Helper function for the Quick Sort algorithm.

        Args:
            low (int): start index of the subarray to be sorted.
            high (int): end index of the subarray to be sorted.
        """
        if low >= high:
            return
        p = partition(arr, low, high, comparator)
        quick_sort_helper(low, p-1)
        quick_sort_helper(p+1, high)
    quick_sort_helper(0, len(arr)-1)
    return arr

def quick_select(arr: List[T],
                 n: int,
                 comparator: Callable[[T], Any]=lambda x: x
                 ) -> Optional[T]:
    """
    Implementation of the Quick Select algorithm,
        used to find the nth smallest element in the array.

    Args:
        arr (List[T]): array to be queried.
        n (int): finds the nth smallest element in the array.
        comparator (T, optional): basis of comparison. Defaults to lambda x: x.

    Returns:
        Optional[T]: returns None if array is empty. Otherwise, returns nth smallest element.
    """
    n -= 1
    def quick_select_helper(low: int, high: int) -> Optional[T]:
        """
        Helper function for the Quick Select algorithm.

        Args:
            low (int): start index for the subarray to be queried.
            high (int): end index for the subarray to be queried.

        Returns:
            Optional[T]: recursively calls function on a smaller subarray
                if required element is still not found.
        """
        if low == high == n:
            return arr[n]
        if low > high:
            return None
        p = partition(arr, low, high, comparator)
        if p == n:
            return arr[p]
        elif p > n:
            return quick_select_helper(low, p-1)
        else:
            return quick_select_helper(p+1, high)
    return quick_select_helper(0, len(arr)-1)

def median(arr: List[T],
           comparator: Callable[[T], Any]=lambda x: x
           ) -> Optional[T]:
    """
    Finds the median value of an array.

    Args:
        arr (List[T]): array to be queried.
        comparator (T, optional): basis of comparison. Defaults to lambda x: x.

    Returns:
        Optional[T]: median value, if available.
    """
    return quick_select(arr, int(len(arr)/2)+1, comparator)

def median_with_left_right(arr: List[T],
                           comparator: Callable[[T], T]=lambda x: x
                           ) -> Tuple[List[T], Optional[T], List[T]]:
    """
    Finds the median value, as well as the left and right
        subarrays created after runnning Quick Select.

    Args:
        arr (List[T]): array to be queried.
        comparator (T, optional): basis of comparison. Defaults to lambda x: x.

    Returns:
        Tuple[List[T], Optional[T], List[T]]: median, with left and right subarrays.
    """
    if len(arr) == 0:
        return ([], None, [])
    med = median(arr, comparator)
    mid = int(len(arr)/2)
    return (arr[:mid], med, arr[mid+1:])