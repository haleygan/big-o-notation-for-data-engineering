# O(n log n) — Algorithms

## 1. Algorithm index

- **Merge sort** — the canonical algorithm for this folder: divide-and-conquer sort with
  a *guaranteed* `Θ(n log n)` time and `O(n)` space, no adversarial input shape.
- **Heapsort** — in-place `O(n log n)` sort using a binary heap; same time guarantee as
  merge sort, `O(1)` auxiliary space instead of `O(n)`.
- **Timsort** — the hybrid merge-sort/insertion-sort actually running under Python's
  `sorted()` and Java's `Collections.sort()`; adaptive to already-sorted runs in real data.
- **Quicksort** (brief mention) — average `Θ(n log n)`, worst-case `Θ(n²)`; the full
  degradation story belongs to `05-On2-quadratic`, not here.
- **Sort-merge join / external merge sort** — the DE-scale application of merge sort's
  merge step, used when data doesn't fit in memory or a hash join's build side is too big.

## 2. Each algorithm

### Merge sort

**Background.** Invented by John von Neumann in 1945, merge sort is the original
divide-and-conquer sorting algorithm: split the array in half, recursively sort each
half, then merge the two sorted halves back together in one linear pass. It exists
because it guarantees `Θ(n log n)` regardless of input — the tradeoff, covered in
`space-complexity.md`, is `O(n)` auxiliary space for the merge buffer.

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left, right):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])   # drain whichever side has leftovers
    merged.extend(right[j:])
    return merged
```

Walkthrough: `merge_sort` recurses until it hits a base case of length 0 or 1 (trivially
sorted), then `_merge` walks both sorted halves with two pointers (`i`, `j`), always
taking the smaller of the two current elements — that's the linear-time combine step
from `overview.md` §2. The two `extend` calls at the end handle the case where one side
empties out before the other; whatever's left is already sorted, so it's just appended.

Reference: [Merge sort — Wikipedia](https://en.wikipedia.org/wiki/Merge_sort)

### Heapsort

**Background.** Heapsort gets `O(n log n)` time out of a binary heap instead of
recursive splitting: build a max-heap from the array in `O(n)`, then repeatedly swap the
root (the max) to the end of the unsorted region and sift the new root down (`O(log n)`
per extraction, `n` extractions). Because the heap lives inside the original array via
index arithmetic, no second buffer is needed — `O(1)` auxiliary space, the direct
contrast to merge sort's `O(n)` (see `space-complexity.md` §3).

```python
import heapq

def heapsort(arr):
    heap = arr.copy()
    heapq.heapify(heap)          # O(n) build, in place
    return [heapq.heappop(heap) for _ in range(len(heap))]   # O(log n) each, n times
```

(This version uses `heapq` and isn't strictly in-place in Python since `heapify` operates
on a list but `heappop` allocates; a hand-rolled sift-down against the original array is
what gets you the true `O(1)` auxiliary space in a lower-level language.)

Reference: [Heapsort — Wikipedia](https://en.wikipedia.org/wiki/Heapsort)

### Timsort

**Background.** Timsort, written by Tim Peters in 2002, is what actually runs when you
call Python's `sorted()`/`list.sort()` or Java's `Collections.sort()` on objects. It's a
hybrid: it scans for naturally-occurring sorted "runs" in the real data (very common in
production — mostly-sorted timestamps, log files with a few late arrivals), extends short
runs using insertion sort, then merges runs together using merge sort's merge step. Worst
case is still `Θ(n log n)`, but best case on already/nearly-sorted input is `O(n)` — a
practical adaptiveness merge sort's textbook form doesn't have.

```python
rows = [{"id": 3, "ts": 30}, {"id": 1, "ts": 10}, {"id": 2, "ts": 20}]
rows.sort(key=lambda r: r["ts"])   # Timsort under the hood, guaranteed O(n log n) worst case
```

There's no reason to hand-roll Timsort (it's genuinely intricate); the point is
recognizing that the sort you call every day already gives you merge sort's guarantee.

Reference: [Timsort — Wikipedia](https://en.wikipedia.org/wiki/Timsort)

### Quicksort (brief)

**Background.** Also divide-and-conquer, but instead of blindly splitting in half,
quicksort partitions the array around a chosen pivot so everything smaller ends up on
one side and everything larger on the other. Average case is `Θ(n log n)` with smaller
constants than merge sort in practice (in-place, more cache-friendly) — but the worst
case is `Θ(n²)` when pivot choice repeatedly produces unbalanced partitions. That
degradation, and how real implementations defend against it, is the entire subject of
`05-On2-quadratic` — not repeated here.

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    less = [x for x in arr if x < pivot]
    equal = [x for x in arr if x == pivot]
    greater = [x for x in arr if x > pivot]
    return quicksort(less) + equal + quicksort(greater)
```

Reference: [Quicksort — Wikipedia](https://en.wikipedia.org/wiki/Quicksort)

### Sort-merge join / external merge sort (DE pattern)

**Background.** A relational join strategy: sort both input relations on the join key
(`O(n log n + m log m)`), then walk the two sorted streams together in a single linear
merge pass, emitting matches. Used when a hash join's build side won't fit in memory, or
when the inputs are already sorted (e.g. reading off a sorted index), making the sort
step free. The same "sort chunks, merge sorted chunks" pattern, run when the whole
dataset doesn't fit in RAM, is external merge sort — spill sorted chunks to disk, merge
them in one or more passes (see `space-complexity.md` §3).

```python
def sort_merge_join(a, b, key):
    a_sorted = sorted(a, key=key)
    b_sorted = sorted(b, key=key)
    i = j = 0
    result = []
    while i < len(a_sorted) and j < len(b_sorted):
        ka, kb = key(a_sorted[i]), key(b_sorted[j])
        if ka == kb:
            result.append((a_sorted[i], b_sorted[j]))
            j += 1
        elif ka < kb:
            i += 1
        else:
            j += 1
    return result
```

Reference: [PostgreSQL merge join docs](https://www.postgresql.org/docs/current/planner-stats.html),
[Spark SortMergeJoin](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

## 3. LeetCode pattern callout

**Pattern: divide-and-conquer / "sort, then linear scan."** Recognize it when a problem
gives you an array and asks for something order-dependent across the *whole* array that
would cost `O(n²)` checked pairwise, but collapses to a single pass once the data is
sorted first — or when the problem explicitly asks you to implement or apply merge
sort's mechanics.

- **LeetCode 148, "Sort List"** — implement merge sort directly on a linked list.
- **LeetCode 315, "Count of Smaller Numbers After Self"** — merge sort with a counter
  threaded through the merge step (classic "count inversions" pattern).
- **LeetCode 56, "Merge Intervals"** — sort by start time (`O(n log n)`), then a single
  linear scan to merge overlaps.
- **LeetCode 973, "K Closest Points to Origin"** — full sort or heap-based `O(n log k)`,
  depending on how `k` compares to `n`.
