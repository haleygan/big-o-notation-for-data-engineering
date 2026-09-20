# O(n²) — In Data Engineering

## 2. DE Technology Examples

| Technology | Operation | Why this complexity | Minimal code sample |
|---|---|---|---|
| pandas | Row-wise cross-lookup via `.apply` instead of `.merge` | For every row, scanning the whole other frame is a nested loop in disguise | `df1.apply(lambda r: df2[df2.key == r.key].val.sum(), axis=1)` |
| PostgreSQL | Nested-loop join, no usable index on the join column | Planner falls back to comparing every row of A against every row of B | `SELECT * FROM orders o, customers c WHERE o.cust_name = c.name;` (no index on `name`) |
| Apache Spark | `crossJoin` between two non-trivial DataFrames | Materializes every (row_A, row_B) pair — literally `n·m` output rows | `df1.crossJoin(df2)` |
| Plain Python | Naive duplicate/near-duplicate detection | Compare every record against every other record, no index or hash | `for i in range(n):`<br>`    for j in range(i+1, n):`<br>`        if a[i] == a[j]: ...` |
| C's classic `qsort` (pre-introsort libraries) | Sorting an already-sorted or reverse-sorted array | Naive pivot rule (first/last element) degenerates on sorted input — the overview.md §2 scenario, in a real library | `qsort(arr, n, sizeof(int), cmp);` on a pre-sorted `arr` |
| Entity resolution / fuzzy matching tools | All-pairs string-similarity scoring | Comparing every candidate record to every other candidate record before any blocking/indexing step | `for a, b in itertools.combinations(records, 2): score(a, b)` |

## 3. Where It Naturally Emerges

- **Unindexed joins.** A join column missing an index (or with stale statistics) makes
  the query planner fall back to a nested-loop join. This is the single most common way
  O(n²) shows up silently in production SQL — nobody wrote a nested loop on purpose, the
  planner picked it because it had no better option.
- **Naive entity resolution / dedup.** Comparing every record against every other record
  to find duplicates or near-duplicates, with no blocking key, hashing, or index to cut
  down the candidate pairs first. Scales fine on a 500-row test file, falls over on a
  5-million-row production table.
- **Row-wise lookups instead of vectorized merges.** Iterating a DataFrame row by row and
  looking something up in another DataFrame per row (`.apply` with an inner filter)
  instead of a single `.merge()` call — pandas' `.merge` uses a hash join internally
  (O(n+m)); the row-wise version is a nested loop wearing pandas syntax.
  See 03-On-linear/03-On-linear-de-application.md and 04-Onlogn-linearithmic/04-Onlogn-linearithmic-de-application.md for
  what the O(n+m) and O(n log n) join strategies actually look like.
- **Building a full pairwise similarity/distance matrix** for clustering or
  recommendation prep, before any approximate-nearest-neighbor or blocking technique cuts
  the candidate set down.
- **Sorting data that's already (or nearly) sorted with a naive quicksort** — timestamp
  columns, auto-incrementing IDs, or re-sorting an already-ordered export — hitting
  exactly the overview.md §2 worst case.

## 4. Common Mistakes → Exceptions

**The mistake:** naive pivot selection — always picking the first element or the last
element as the quicksort pivot — combined with input that's already sorted, reverse-sorted,
or has large runs of duplicate keys. This is the overview.md §2 / space-complexity.md §5
scenario: the naive rule guarantees maximally unbalanced partitions on exactly the kind of
data data engineers see constantly (timestamp-ordered logs, ID columns, pre-sorted
exports), silently turning an expected Θ(n log n) sort into Θ(n²) time and O(n)
recursion-stack space.

**The fix:**

- **Randomized pivot selection** — pick a pivot index uniformly at random on each
  partition call. No fixed input shape can reliably trigger the worst case anymore,
  because the adversary would need to predict the random draws. Expected time stays
  Θ(n log n) regardless of whether the input arrives sorted, reverse-sorted, or random.
- **Median-of-three pivot selection** — take the median of the first, middle, and last
  elements as the pivot. Cheaper than full randomization and specifically defeats the
  sorted/reverse-sorted case, which is the most common real-world trigger. This is what
  most production `qsort`/introsort implementations actually do.

**The exception — when O(n²) is still fine:** small, bounded `n`. Real-world quicksort
implementations (including the ones behind `qsort` and Python's old sort internals)
switch to insertion sort below some threshold (often `n < 10–20`) precisely because
insertion sort's O(n²) is faster in practice at that size — the constant factors of
quicksort's recursion overhead lose to insertion sort's simplicity when there's barely
anything to sort. More generally: a one-off batch script over a table you know will
never exceed a few hundred rows doesn't need the randomized-pivot fix — the risk that
matters is *unbounded or unpredictable* `n`, not quadratic time itself. The same logic
applies to nested-loop joins: joining a large table against a 5-row config/lookup table
is technically O(n·m), but with `m = 5` fixed and tiny, it behaves like O(n) in practice
and isn't worth an index or a hash-join rewrite.
