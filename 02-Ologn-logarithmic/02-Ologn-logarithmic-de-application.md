# O(log n) — In Data Engineering

## 1. DE Technology Examples

| Technology | Operation | Why this complexity | Minimal code sample |
|---|---|---|---|
| Postgres / MySQL | B-tree index lookup (`WHERE id = ?`) | Index is a balanced tree; each level eliminates most of the remaining rows, height is `O(log n)` for `n` rows | `SELECT * FROM orders WHERE order_id = 48291;` (index scan if `order_id` is indexed/PK) |
| Python `bisect` | `bisect.bisect_left(sorted_list, x)` | Standard-library binary search over a pre-sorted sequence | `bisect.bisect_left(sorted_ids, 48291)` |
| Redis | Sorted set range query (`ZRANGEBYSCORE`) | Backed by a skip list — probabilistic balanced structure, expected `O(log n)` per lookup | `r.zrangebyscore("leaderboard", 1000, 2000)` |
| Java / Scala collections | `TreeMap.get(key)` | Red-black tree (self-balancing BST) guarantees `O(log n)` worst case, not just average | `new TreeMap<Integer,String>().get(48291)` |
| Elasticsearch / Lucene | Term dictionary lookup during a query | Term dictionary uses a finite-state-transducer / block-tree structure that resolves a term to its postings list in effectively `O(log n)` over the term count | `{"query":{"term":{"order_id":"48291"}}}` |

The throughline across every row: **something is kept sorted or tree-shaped ahead of
time, and that upfront structure is what buys the `log n` lookup later.** None of these
are free — building the index/tree costs time upfront (usually `O(n log n)`, see
`04-Onlogn-linearithmic`) — you're trading a one-time cost for cheap repeated lookups.

## 2. Where It Naturally Emerges

- **Primary/foreign key lookups in OLTP databases.** Any `WHERE column = value` on an
  indexed column becomes a B-tree traversal instead of a table scan — this is the single
  most common place a data engineer touches O(log n) without thinking about it, every
  time a query planner picks an index scan over a sequential scan.
- **Point lookups against a partitioned/sorted dataset.** Parquet files with sorted row
  groups plus min/max "zone maps" let a query engine binary-search which row groups
  could possibly contain a value, skipping the rest entirely — same halving idea applied
  at the file/row-group level instead of the row level.
- **Range queries on time-series data.** Finding "first log line after timestamp T" in a
  file sorted by time is a textbook binary search, whether you're doing it by hand with
  `bisect` or letting a time-series DB's index do it.
- **Autoscaling / bucketing decisions.** Picking which bucket a value falls into from a
  sorted list of thresholds (e.g. routing a request to the right shard by hashing then
  binary-searching a sorted list of shard boundaries) is the same pattern again.
- **LSM-tree structures (Cassandra, RocksDB, LevelDB).** A lookup checks a bloom filter
  first (O(1)-ish), then does a search within an SSTable's sparse index — that sparse
  index search is O(log n) over the number of index entries in that file.

**Tying to concept.md §6 (multi-variable complexity):** a single index probe is
`O(log n)` where `n` is the size of the index — but a *query* rarely does just one probe.
Say you're doing an **index nested-loop join**: for each of `n` rows in the outer table,
probe an index on the inner table (size `m`) to find matches. Per-row cost is
`O(log m)`, but total query cost across all `n` outer rows is `O(n log m)` — the `log`
only shrinks the *per-probe* cost, it doesn't make the total query cost independent of
`n`. This is exactly why query planners switch strategies as `n` grows: for a small outer
table, `n` index probes at `O(log m)` each beats a full hash join's `O(n + m)` setup cost;
once `n` gets large enough, the constant-ish overhead of `n` separate index probes loses
to paying `O(n + m)` once for a hash join. The `log` doesn't mean "always fast" — it
means "fast *per lookup*," and multiplying that by how many lookups you're doing is the
part that determines whether the strategy actually wins. Compare against the join
strategy table in concept.md §6 directly.
