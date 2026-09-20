# O(n log n) — In Data Engineering

## 1. DE technology examples

| Technology | Operation | Why this complexity | Minimal code sample |
|---|---|---|---|
| Python `sorted()` / `list.sort()` | Sorting any list, or a DataFrame column via `.sort_values()` on object dtype | Both use Timsort, a merge-sort/insertion-sort hybrid with a guaranteed `O(n log n)` worst case | `rows.sort(key=lambda r: r["ts"])` |
| pandas `.sort_values()` | Sorting a DataFrame by column | Default `kind="quicksort"` (really introsort) is average `O(n log n)`; pass `kind="mergesort"` when you need a *guaranteed* bound and stability | `df.sort_values("ts", kind="mergesort")` |
| Apache Spark | Sort-merge join (`SortMergeJoinExec`) | Both sides get sorted on the join key — `O(n log n + m log m)` — then merged in one linear pass; Spark's default strategy when a broadcast/hash join won't fit in executor memory | `df1.join(df2, "id")` (planner picks sort-merge automatically for large-large joins) |
| PostgreSQL | `ORDER BY`, and the external sort used when a result set exceeds `work_mem` | In-memory sorts use quicksort variants; once the data spills to disk, Postgres switches to an external **merge** sort — sorted runs written to disk, then merged | `EXPLAIN (ANALYZE) SELECT * FROM events ORDER BY ts;` |
| Hadoop MapReduce | Shuffle-and-sort phase | Each mapper sorts its own output by key, then the shuffle phase merges the sorted per-mapper outputs — sort-merge at cluster scale, the reason reducers receive keys in sorted order for free | (framework-managed; no user code — configured via `mapreduce.task.io.sort.mb`) |
| Java `Collections.sort()` / `Arrays.sort(Object[])` | Sorting a `List<T>` or object array | Uses a Timsort-derived algorithm — same guarantee as Python's, stable, worst case `O(n log n)` | `Collections.sort(records, Comparator.comparing(Record::getTs));` |

## 2. Where it naturally emerges

- **Any explicit sort in a pipeline** — `ORDER BY`, `.sort_values()`, `sorted()` — is
  linearithmic by default; it's the single most common way this complexity class shows
  up in day-to-day DE work.
- **Sort-merge joins** — when joining dataset `A` (size `n`) against `B` (size `m`) and a
  hash join's build side doesn't fit in memory, the fallback is sort both sides
  (`O(n log n + m log m)`) then merge (`O(n + m)`). This is exactly the multi-variable
  case flagged in `concept.md` §6 — worth checking which variable is which before
  assuming a join is "just O(n)."
- **Dedup via sort-then-scan** — sort the data (`O(n log n)`), then a single linear pass
  dropping consecutive duplicates. Not the fastest option (a hash set dedupes in
  average `O(n)`), but it's the one to reach for when the hash set's memory footprint is
  the actual constraint — sorting needs no auxiliary lookup structure sized to the
  distinct-value count.
- **Building sorted indexes** — bulk-loading a B-tree index (Postgres, most LSM-tree
  stores) sorts the input key set first so the tree can be built bottom-up in a single
  pass, rather than inserting one key at a time.
- **External sort for out-of-core data** — MapReduce's shuffle sort, and any sort or
  sort-merge join that spills to disk once the working set exceeds available memory,
  are literally running external merge sort at scale: sort what fits, spill sorted runs,
  merge the runs.
- **Top-k queries** — when `k` is a meaningful fraction of `n`, a full sort (`O(n log n)`)
  is often simpler and fast enough; when `k` is small relative to `n`, a heap-based
  top-k (`O(n log k)`) beats it, which is still in this same complexity family whenever
  `k` scales with `n`.
