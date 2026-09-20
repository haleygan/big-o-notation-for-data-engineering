# O(n²) — Space Complexity

## 2. Typical Space Cost

Quadratic *time* does not imply quadratic *space* — that's the first thing to untangle,
because the two get conflated constantly. Split this class into two distinct groups:

**Group A — in-place, O(1) or O(log n) auxiliary space.** Quicksort, bubble sort,
insertion sort, and selection sort all sort *within* the input array. They swap elements
around but never allocate a second array proportional to `n`. The only extra memory
quicksort needs is the recursion call stack (covered in §5 below) — the data itself
never gets duplicated. A naive nested-loop duplicate check (`for i in range(n): for j in
range(i+1, n): compare a[i], a[j]`) is the same story: two index variables, no extra
structure, O(1) auxiliary space, even though it's O(n²) time.

**Group B — algorithms in this class that genuinely do cost O(n²) space.** The moment
you *materialize* the result of an all-pairs comparison instead of just computing it and
discarding it, you're paying quadratic space. Two concrete DE-relevant examples:

- Building a full pairwise distance/similarity matrix between `n` records (common in
  naive fuzzy-dedup or clustering prep) — an `n × n` matrix stored explicitly is O(n²)
  space by construction, not just O(n²) time to fill it.
- A naive cross join (`df1.crossJoin(df2)` or an unindexed nested-loop SQL join)
  materialized into a result set — if both sides have `n` rows, the output itself has up
  to `n²` rows sitting in memory or on disk.

So the rule of thumb: **if the O(n²) algorithm only ever looks at one pair of elements at
a time and moves on, it's O(1) auxiliary space. If it stores every pair's result, it's
O(n²) space.** Quicksort is squarely in the first group.

## 4. Local Time/Space Tradeoff

Within this class, the interesting tradeoff isn't really about *reducing* time (that
would move you into a different complexity class entirely) — it's about how much extra
memory a variant spends to get simpler code or safer recursion behavior:

- **In-place quicksort** (swaps within the array, partitions by index) vs. a
  **"functional-style" quicksort** that builds brand-new `left`/`right` lists at every
  partition step (`left = [x for x in arr if x < pivot]`). Same O(n²) worst-case time,
  but the functional version spends O(n) extra space *per level of recursion* on the new
  lists it builds, instead of O(1) extra space per level. Easier to read, worse on
  memory — a real tradeoff people make deliberately for the readability win in
  non-performance-critical code.
- **Naive pairwise dedup** (O(1) extra space, compare pairs on the fly, discard each
  comparison result immediately) vs. **materializing the full similarity matrix** (O(n²)
  space, per Group B above) — the tradeoff is: computing on the fly is cheaper on memory
  but you recompute if you need the same comparison twice; materializing costs O(n²)
  space but every pairwise result is available instantly afterward for downstream
  analysis or debugging.

## 5. Worst-Case Space Deviation

This is the piece that matters most for this class, and it mirrors the worst-case time
story in overview.md §2 almost exactly.

**Quicksort's recursion-stack space is O(log n) in the average case.** Each recursive
call adds one stack frame; with balanced partitioning (the typical case), the recursion
tree has depth `log n`, so at most `log n` stack frames are ever active at once.

**But on the same adversarial input that causes the O(n²) time blowup — already-sorted
or reverse-sorted data combined with a naive first-or-last-element pivot — the recursion
stack degrades to O(n) worst-case depth.** Walk through why: the pivot is always the
max (or min) of the current subarray, so every partition splits `n` elements into
`(n-1, 0)` instead of two roughly equal halves. Recursion depth grows by exactly one
level per element instead of halving each time, so instead of `log n` stack frames you
get `n` stack frames — one per recursive call, all the way down.

**This is the same root cause showing up as two symptoms, not two separate problems.**
Degenerate partitioning is the one thing that goes wrong; O(n²) time and O(n) stack
depth are both direct consequences of it. Average case: Θ(n log n) time, O(log n)
recursion-stack space. Worst case, same adversarial input: Θ(n²) time, O(n) recursion-stack
space. If you've fixed the pivot-selection mistake (randomized or median-of-three — see
de-application.md §4), you've fixed both symptoms at once, because you removed the one
cause behind them.

## 6. Cross-Link

The root `capstone.md`'s time/space tradeoff section uses this exact degradation as its
"in-place sort" example — quicksort's average-case O(log n) stack space vs. its
worst-case O(n) stack space (same cause as the O(n²) worst-case time above), contrasted
against merge sort's guaranteed O(n) space regardless of input shape. See `capstone.md`
§3 for how that comparison plays out against the other 6 complexity classes.
