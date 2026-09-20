# O(n²) — Algorithms

## 1. Algorithm Index

- **Quicksort (worst case)** — divide-and-conquer sort; average Θ(n log n), degrades to
  Θ(n²) on adversarial pivots. The canonical algorithm for this whole folder.
- **Bubble sort** — repeatedly swap adjacent out-of-order elements until nothing moves.
- **Insertion sort** — build a sorted prefix one element at a time, shifting larger
  elements right to make room.
- **Selection sort** — repeatedly find the minimum of the unsorted remainder and swap it
  into place.
- **Naive nested-loop pairwise comparison** — compare every element against every other
  element directly; underlies naive duplicate detection and unindexed joins.

## 2. Quicksort (Worst Case)

**Background.** Quicksort is a divide-and-conquer sort: pick a pivot, partition the
array so everything smaller than the pivot ends up on its left and everything larger
ends up on its right, then recurse on each side. When partitions stay roughly balanced,
this is one of the fastest general-purpose sorts in practice — it's what most standard
library sorts were historically built on (see overview.md and space-complexity.md for
the full average-vs-worst-case story). It exists because merge sort's guaranteed O(n log n)
comes with mandatory O(n) extra space, and for large in-memory arrays, an in-place sort
that's *usually* just as fast is a better default — as long as you protect it from its
one failure mode.

**Code + walkthrough** (naive last-element pivot — the version that hits the O(n²)
worst case on sorted input):

```python
def quicksort_naive(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo >= hi:
        return arr

    pivot = arr[hi]           # naive rule: always the last element
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    p = i + 1                 # pivot's final resting index

    quicksort_naive(arr, lo, p - 1)
    quicksort_naive(arr, p + 1, hi)
    return arr
```

- The `for` loop is the partition step: walk the subarray once, and every time you find
  an element `<=` pivot, swap it into the "small" side (tracked by `i`).
- After the loop, one final swap drops the pivot into its correct sorted position `p`.
- The two recursive calls handle everything left of `p` and everything right of `p`.
- On random input, `p` lands roughly in the middle each time → `log n` recursion depth.
  On sorted input with this pivot rule, `p` always lands at `hi` (the pivot never moves,
  everything is smaller) → `n` recursion depth, `O(n²)` total comparisons (derived in
  overview.md §3).

Reference: [Quicksort — Wikipedia](https://en.wikipedia.org/wiki/Quicksort)

## 3. Bubble Sort

**Background.** The simplest possible comparison sort: repeatedly step through the
array, swap adjacent elements that are out of order, and repeat until a full pass makes
no swaps. Nobody uses this in production — it's here because it's the clearest possible
illustration of "nested loop → O(n²)," with zero cleverness hiding the mechanics.

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break   # already sorted — best case O(n), not relevant to the O(n²) count
    return arr
```

- Outer loop runs up to `n` times; inner loop runs up to `n` times — the textbook nested
  loop from concept.md §3 ("a loop over n items, each doing a loop over n items → O(n²)").
- The `swapped` flag gives it a best case of O(n) on already-sorted input (the opposite
  situation from quicksort, where already-sorted input is the *worst* case — worth
  noticing that "which input shape is bad" depends entirely on the algorithm).

Reference: [Bubble sort — Wikipedia](https://en.wikipedia.org/wiki/Bubble_sort)

## 4. Insertion Sort

**Background.** Builds up a sorted region at the front of the array one element at a
time: take the next unsorted element, shift everything in the sorted region that's
bigger than it one slot to the right, drop the element into the gap. Real production
sorts (including quicksort/introsort implementations) switch to insertion sort for small
subarrays because its low constant overhead beats quicksort's recursion overhead once
`n` is small enough — see de-application.md §4's "acceptable O(n²)" exception.

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
```

- Outer loop: one pass per element being inserted.
- Inner `while`: shifts elements right, worst case scanning all the way back to the
  start of the sorted region — that's the nested-loop cost, worst case on
  reverse-sorted input.
- Best case is already-sorted input: the `while` condition fails immediately every time,
  giving O(n) — insertion sort and quicksort have exactly opposite "friendly" input
  shapes, a useful contrast to notice.

Reference: [Insertion sort — Wikipedia](https://en.wikipedia.org/wiki/Insertion_sort)

## 5. Selection Sort

**Background.** Repeatedly scan the unsorted remainder for its minimum element and swap
it to the front. Its one notable property: unlike the other three, its comparison count
is *always* `n(n-1)/2` regardless of input order — there's no best-case shortcut,
because it always scans the entire remainder to find the minimum even if the array is
already sorted.

```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
```

- Outer loop fixes the position being filled; inner loop scans the remainder for the
  minimum — nested loop, same shape as bubble sort, but with only one swap per outer
  iteration instead of potentially many.

Reference: [Selection sort — Wikipedia](https://en.wikipedia.org/wiki/Selection_sort)

## 6. Naive Nested-Loop Pairwise Comparison

**Background.** Not a named textbook algorithm so much as a pattern: whenever you need
to compare every element against every other element — duplicate detection, an
unindexed join, all-pairs similarity — and you do it with two nested loops instead of a
hash structure or an index, you get O(n²) by construction.

```python
def has_duplicate_pair(items):
    n = len(items)
    for i in range(n):
        for j in range(i + 1, n):
            if items[i] == items[j]:
                return True
    return False
```

- Contrast with the O(n) fix: a `set()` built in one pass catches duplicates in O(n)
  time (see 03-On-linear/03-On-linear-algorithms.md) — this pattern exists in this folder specifically
  as the "what you get if you don't reach for the hash structure" baseline.

## 7. LeetCode Pattern Callout

**Pattern: brute force / nested loop.** Recognize it in a problem statement whenever you
see phrasing like "for every pair," "check all pairs," "compare each element to every
other element," or when the naive first idea is literally two `for` loops with no early
exit. It's usually presented as the starting point, with the real question being "now
optimize it" (typically down to O(n) via a hash map, or O(n log n) via sorting +
two-pointer).

Example problems that start here:

- **Two Sum** — brute-force nested-loop solution is O(n²); the expected optimization is
  a hash map for O(n) (see 03-On-linear/03-On-linear-algorithms.md).
- **3Sum** — brute-force triple-nested loop is O(n³); the standard accepted solution
  sorts first (O(n log n)) then uses two-pointer per fixed element for O(n²) overall —
  itself a case of *accepting* O(n²) because it's the best known general approach for
  this problem shape.
- **Contains Duplicate** — brute-force pairwise comparison (shown above) is O(n²); the
  set-based fix is O(n).
- **Container With Most Water** — brute-force checks every pair of lines (O(n²)); the
  accepted solution uses a two-pointer sweep for O(n).
