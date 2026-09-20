# O(n) — Algorithms

## 1. Algorithm Index

- **Linear Search** — scan a list or array for a target value, one comparison per
  element, stop early if found.
- **Single-Pass Hash-Set Deduplication** — detect duplicates or collapse a list down to
  distinct values in one pass, using a hash set for O(1) membership checks.
- **Kadane's Algorithm** — find the maximum-sum contiguous subarray in one pass, tracking
  a running best without ever looking backward.
- **Hash Join (build + probe)** — join two datasets on a key in O(n + m) by building a
  hash table over the smaller side and probing it with the larger.

## 2. Linear Search

**Background.** The simplest possible search: you don't know anything about the order
of the data, so there's no shortcut — you check elements one at a time until you find
what you're looking for or run out of elements. This is what `x in my_list` does under
the hood in Python for a plain list.

```python
def linear_search(items, target):
    for i, item in enumerate(items):
        if item == target:
            return i          # early exit on a hit
    return -1                 # exhausted the list, no match
```

**Walkthrough.** The loop visits `items[0]`, `items[1]`, ... in order. The moment
`item == target`, it returns immediately — this is the Ω(1) best case from
`overview.md` §1 (a lucky early hit). If the target is absent or at the very end, the
loop runs all `n` iterations — the Θ(n) worst case. There's no way to do better than this
*without* extra structure (sorting the data first, or building an index) — which is
exactly why `02-Ologn-logarithmic`'s binary search requires the data to already be
sorted.

**Reference.** [Linear search — Wikipedia](https://en.wikipedia.org/wiki/Linear_search)

## 3. Single-Pass Hash-Set Deduplication

**Background.** A very common real task: "does this list have any duplicates?" or "give
me the distinct values." The naive way is to compare every pair of elements — O(n²)
(see `05-On2-quadratic`). The linear way trades a bit of memory for a lot of time: keep
a hash set of everything you've seen so far, and check membership in it as you go.

```python
def has_duplicate(items):
    seen = set()
    for item in items:
        if item in seen:       # O(1) average hash lookup
            return True
        seen.add(item)         # O(1) amortized insert
    return False
```

**Walkthrough.** One pass over `items` — n iterations. Each iteration does an O(1)
average-case hash lookup (`item in seen`) and, if it's a new value, an O(1) amortized
insert (`concept.md` §5). Total: O(n) time, O(n) auxiliary space for `seen` in the worst
case (all distinct values) — the classic time-for-space trade discussed in
`space-complexity.md` §3.

**Reference.** [Python `set` — time complexity, Python docs](https://docs.python.org/3/library/stdtypes.html#set)

## 4. Kadane's Algorithm

**Background.** Given an array of numbers (positive and negative), find the contiguous
subarray with the largest sum — a classic problem that looks like it needs comparing
every possible subarray (there are O(n²) of them) but actually has a clean O(n)
solution. The trick: at each position, decide whether to extend the current subarray or
start a new one from here, keeping only a running "best subarray ending here" and a
running "best seen overall."

```python
def max_subarray_sum(nums):
    best_ending_here = nums[0]
    best_overall = nums[0]
    for x in nums[1:]:
        # either extend the previous subarray, or start fresh at x
        best_ending_here = max(x, best_ending_here + x)
        best_overall = max(best_overall, best_ending_here)
    return best_overall
```

**Walkthrough.** One pass, one comparison-and-update per element — no nested loop, no
looking backward past the previous iteration's two running values. That's the whole
trick: instead of re-examining every possible subarray, the algorithm carries forward
just enough state (`best_ending_here`) to make each new decision in O(1), so the total
work across all n elements is O(n).

**Reference.** [Maximum subarray problem — Wikipedia](https://en.wikipedia.org/wiki/Maximum_subarray_problem)

## 5. Hash Join (Build + Probe)

**Background.** Joining two datasets on a matching key is one of the most common
operations in data engineering — and the naive nested-loop approach (compare every row
of A against every row of B) is O(n·m), which falls apart once both sides get large
(see `concept.md` §6 and `05-On2-quadratic`). The hash join fixes this by building a
hash table over whichever side is smaller, then streaming through the larger side and
doing an O(1) average lookup per row instead of a full inner scan.

```python
def hash_join(table_a, table_b, key="key"):
    # always build the hash table over the smaller side
    if len(table_a) > len(table_b):
        table_a, table_b = table_b, table_a

    build_side = {}
    for row in table_a:                       # O(n): build phase
        build_side.setdefault(row[key], []).append(row)

    results = []
    for row in table_b:                       # O(m): probe phase
        for match in build_side.get(row[key], ()):
            results.append((match, row))
    return results
```

**Walkthrough.** Build phase: n insertions into a dict, each O(1) amortized — O(n)
total. Probe phase: m lookups into that dict, each O(1) average — O(m) total. Combined:
O(n + m), additive rather than multiplicative — the exact multi-variable linear case
flagged in `overview.md` §1 and `concept.md` §6. Real query engines (Spark, Postgres,
DuckDB) implement this same idea, just with more machinery around spilling to disk when
the build side doesn't fit in memory.

**Reference.** [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)

## 6. LeetCode Pattern Callout

**Pattern: single-pass / linear scan** (sometimes called the "running state" pattern,
closely related to fixed-size sliding window and simple two-pointer).

**How to recognize it:** the problem can be phrased as "process each element once,
left to right, keeping track of a small amount of state (a running sum, a best-so-far,
a seen-set, a count) — no sorting required, no comparing every pair, and no need to
revisit earlier elements once you've moved past them." If the answer can be computed
by "scan once, update O(1) state per step," it's this pattern, not a nested-loop or
divide-and-conquer one.

**Example problems:**
- **Two Sum** (LeetCode 1) — single pass with a hash map of value → index, O(n).
- **Best Time to Buy and Sell Stock** (LeetCode 121) — a Kadane's-style running
  min/max-profit scan, O(n).
- **Contains Duplicate** (LeetCode 217) — single-pass hash-set membership check, O(n).
- **Majority Element** (LeetCode 169) — Boyer-Moore voting, one pass, O(1) extra space.
