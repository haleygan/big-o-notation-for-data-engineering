"""
O(log n) vs O(n): binary search vs linear search over the same sorted list.

Same problem in both functions: "does target exist in this sorted list, and if so
where?" Binary search exploits the fact that the list is sorted to throw away half the
remaining candidates per comparison (see overview.md); linear search ignores that and
checks every element in order. Both return the correct index (or -1), so this is an
apples-to-apples correctness-preserving comparison, not just two different problems.

Worst case is used deliberately for both searches (target = value that is NOT in the
list), so the timing reflects each algorithm's worst-case behavior rather than a lucky
early hit -- see overview.md section 1 on why binary search's best case (O(1), lucky
first guess) is not representative of its typical behavior.
"""

import time
import bisect


def linear_search(sorted_list, target):
    """O(n): check every element in order until found or exhausted."""
    for i, value in enumerate(sorted_list):
        if value == target:
            return i
        if value > target:
            # list is sorted, so we can stop early once we've passed where
            # target would be -- still O(n) worst case (target absent / at the end)
            return -1
    return -1


def binary_search(sorted_list, target):
    """O(log n): halve the remaining search range each comparison."""
    low, high = 0, len(sorted_list) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_list[mid]
        if mid_val == target:
            return mid
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def time_search(search_fn, sorted_list, target, repeats=200):
    """Run search_fn `repeats` times and return average time in microseconds."""
    start = time.perf_counter()
    for _ in range(repeats):
        search_fn(sorted_list, target)
    elapsed = time.perf_counter() - start
    return (elapsed / repeats) * 1_000_000  # microseconds per call


def main():
    sizes = [1_000, 10_000, 100_000, 1_000_000, 5_000_000]

    print(f"{'n':>10} | {'linear O(n) (us)':>18} | {'binary O(log n) (us)':>22} | {'speedup':>10}")
    print("-" * 68)

    for n in sizes:
        sorted_list = list(range(0, n * 2, 2))  # sorted even numbers: 0, 2, 4, ...
        # target is deliberately NOT in the list (odd number, worst case for both:
        # linear search must scan past every element, binary search must halve
        # all the way down to an empty range).
        target = (n * 2) - 1

        # fewer repeats for very large n so the benchmark still finishes quickly
        repeats = 50 if n >= 1_000_000 else 200

        linear_us = time_search(linear_search, sorted_list, target, repeats)
        binary_us = time_search(binary_search, sorted_list, target, repeats)

        speedup = linear_us / binary_us if binary_us > 0 else float("inf")
        print(f"{n:>10} | {linear_us:>18.2f} | {binary_us:>22.4f} | {speedup:>9.1f}x")

    # sanity check: confirm bisect (stdlib) agrees with our hand-rolled binary search
    # on a small case, so we know the implementation above is actually correct and
    # not just fast-but-wrong.
    sample = list(range(0, 20, 2))
    assert binary_search(sample, 8) == bisect.bisect_left(sample, 8) == 4
    assert binary_search(sample, 7) == -1

    print(
        "\n"
        "Takeaway: at n=1,000 the gap barely registers -- both finish in microseconds\n"
        "and constant-factor overhead (Python loop/function call cost) can dominate.\n"
        "By n=1,000,000+ linear search is doing hundreds of thousands of comparisons\n"
        "per call while binary search is still doing ~20-23 (log2(n)). The speedup\n"
        "column should grow roughly in proportion to n / log2(n) as n increases --\n"
        "that ratio is exactly why databases build indexes instead of scanning tables."
    )


if __name__ == "__main__":
    main()
