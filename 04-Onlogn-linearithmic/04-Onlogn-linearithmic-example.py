"""
O(n log n) vs O(n^2): merge sort vs insertion sort, benchmarked on the same problem
(sorting a list of random integers).

Run: python3 example.py
"""

import random
import time
from typing import List


# --- This complexity: merge sort, guaranteed Theta(n log n), see overview.md #1 ---

def merge_sort(arr: List[int]) -> List[int]:
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: List[int], right: List[int]) -> List[int]:
    merged: List[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


# --- Contrasting complexity: insertion sort, O(n^2) average/worst case ---

def insertion_sort(arr: List[int]) -> List[int]:
    result = arr.copy()
    for i in range(1, len(result)):
        key = result[i]
        j = i - 1
        while j >= 0 and result[j] > key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = key
    return result


def timed(fn, arr: List[int]) -> float:
    start = time.perf_counter()
    fn(arr)
    return time.perf_counter() - start


def main() -> None:
    # Correctness sanity check before timing anything.
    sample = [random.randint(0, 1000) for _ in range(500)]
    assert merge_sort(sample) == sorted(sample)
    assert insertion_sort(sample) == sorted(sample)

    sizes = [100, 500, 1000, 2000, 4000, 8000]

    print(f"{'n':>6} | {'merge sort (s)':>16} | {'insertion sort (s)':>19} | ratio")
    print("-" * 62)

    for n in sizes:
        data = [random.randint(0, 1_000_000) for _ in range(n)]
        t_merge = timed(merge_sort, data)
        t_insert = timed(insertion_sort, data)
        ratio = (t_insert / t_merge) if t_merge > 0 else float("inf")
        print(f"{n:>6} | {t_merge:>16.6f} | {t_insert:>19.6f} | {ratio:>5.1f}x")

    # Takeaway:
    # Merge sort's cost grows like n * log(n): doubling n roughly doubles the
    # time plus a small extra factor. Insertion sort's cost grows like n^2:
    # doubling n roughly quadruples the time. At n=100 the two are close enough
    # that insertion sort's lower constant overhead can even make it competitive
    # or faster - this is exactly why concept.md's napkin method warns that Big O
    # describes the shape of the curve, not where it sits for small n. By n=8000
    # the ratio column should show insertion sort taking many times longer than
    # merge sort, and that gap keeps widening for every doubling after this -
    # merge sort's Theta(n log n) guarantee (see overview.md #1) is what makes it
    # the safe default once n is large enough, or unpredictable enough, that you
    # can't assume it'll stay small.


if __name__ == "__main__":
    main()
