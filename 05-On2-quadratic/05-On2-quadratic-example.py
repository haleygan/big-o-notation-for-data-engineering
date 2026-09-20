"""
example.py -- O(n^2) worst-case quicksort vs. O(n log n) randomized-pivot quicksort

Demonstrates the exact claim from overview.md Section 2: quicksort's average case is
Theta(n log n), but naive pivot selection (always the last element) on already-sorted
input degrades it to Theta(n^2). Randomizing the pivot choice fixes it -- same
algorithm, same input, wildly different growth curve. See space-complexity.md Section 5
for why the same adversarial input also blows up the recursion-stack space, not just
the time.
"""

import random
import sys
import time

# Worst-case naive-pivot quicksort recurses to a depth of n on sorted input
# (space-complexity.md Section 5), so we need enough headroom for the largest n below.
sys.setrecursionlimit(20000)


def quicksort_naive_pivot(arr, lo=0, hi=None):
    """Quicksort using the last element as the pivot, every time.

    On random input this behaves like an average-case O(n log n) sort. On
    already-sorted (or reverse-sorted) input, the pivot is always the max (or min) of
    the current subarray, so every partition splits n elements into (n-1, 0) --
    maximally unbalanced. Recursion depth becomes O(n) and total comparisons become
    n + (n-1) + ... + 1 = O(n^2), derived step by step in overview.md Section 3.
    """
    if hi is None:
        hi = len(arr) - 1
    if lo >= hi:
        return arr

    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    p = i + 1

    quicksort_naive_pivot(arr, lo, p - 1)
    quicksort_naive_pivot(arr, p + 1, hi)
    return arr


def quicksort_randomized_pivot(arr, lo=0, hi=None):
    """Same algorithm, one change: the pivot is picked uniformly at random.

    Randomizing the pivot means no fixed input shape (sorted, reverse-sorted,
    all-duplicates) can reliably force the worst case -- the *expected* running time
    stays Theta(n log n) regardless of input order, because an adversary would need to
    predict the random choices to defeat it. This is the "fix" described in
    de-application.md Section 4.
    """
    if hi is None:
        hi = len(arr) - 1
    if lo >= hi:
        return arr

    pivot_idx = random.randint(lo, hi)
    arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]

    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    p = i + 1

    quicksort_randomized_pivot(arr, lo, p - 1)
    quicksort_randomized_pivot(arr, p + 1, hi)
    return arr


def timed(fn, arr):
    """Run fn on a private copy of arr (both sorts mutate in place) and time it."""
    working_copy = arr[:]
    start = time.perf_counter()
    fn(working_copy)
    return time.perf_counter() - start


def main():
    sizes = [200, 400, 800, 1600]

    print(f"{'n':>6} | {'naive-pivot (s)':>16} | {'randomized-pivot (s)':>20} | ratio")
    print("-" * 62)

    for n in sizes:
        # Already-sorted input: the exact adversarial shape from overview.md Section 2.
        sorted_input = list(range(n))

        naive_time = timed(quicksort_naive_pivot, sorted_input)
        random_time = timed(quicksort_randomized_pivot, sorted_input)

        ratio = naive_time / random_time if random_time > 0 else float("inf")
        print(f"{n:>6} | {naive_time:>16.6f} | {random_time:>20.6f} | {ratio:>5.1f}x")


if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------------------
# Takeaway:
#
# On already-sorted input, quicksort with a naive last-element pivot hits its O(n^2)
# worst case: doubling n roughly quadruples the naive-pivot time (200 -> 400 -> 800 ->
# 1600 should show each step costing ~4x the previous one). The randomized-pivot
# version -- running the *identical* partition logic on the *identical* input -- stays
# close to O(n log n): doubling n roughly doubles its time (times a small log factor)
# instead of quadrupling it.
#
# The ratio column widens as n grows. That's the point: the same algorithm can look
# perfectly fine in a quick test against random sample data and then fall over in
# production the day it receives data that happens to already be sorted -- timestamps,
# an auto-incrementing ID column, an already-ordered export. See de-application.md
# Section 4 for the fix (randomized or median-of-three pivot selection) and
# space-complexity.md Section 5 for why the same adversarial input also blows up the
# recursion-stack space (O(log n) average -> O(n) worst case), not just the time.
# ---------------------------------------------------------------------------------
