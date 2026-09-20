# O(n!) — In Data Engineering

Factorial time almost never shows up *on purpose* at real scale in data engineering —
nobody ships a pipeline that brute-forces a 10,000-item permutation search. Where it
actually shows up is (a) as a real cost hiding inside a query planner that a DE relies on
every day without noticing, and (b) as an accidental trap when someone hand-rolls a
"try every ordering" script instead of reaching for the domain-appropriate algorithm.

## 1. DE Technology Examples

| Technology | Operation | Why this complexity | Minimal code sample |
|---|---|---|---|
| Postgres query planner | Choosing a join order for a multi-table query | Naive exhaustive search over join orders for `n` tables is `O(n!)`; Postgres runs this exhaustively only below `join_collapse_limit` (default 8) | `SET join_collapse_limit = 8;` — above this, Postgres switches strategy (see row below) |
| Postgres GEQO (Genetic Query Optimizer) | Join order search once table count passes `geqo_threshold` | Explicitly exists *because* exhaustive join-order search is factorial — Postgres's own docs describe switching to a genetic-algorithm heuristic to avoid it | `SET geqo_threshold = 12;` — queries joining 12+ tables use GEQO instead of exhaustive search |
| Spark Catalyst optimizer | Cost-based multi-way join reordering | Same join-order-explosion problem as Postgres; Catalyst uses dynamic-programming-based join reordering (`spark.sql.cbo.joinReorder.enabled`) with a table-count cap rather than trying every order | `spark.conf.set("spark.sql.cbo.joinReorder.dpThreshold", 12)` |
| Logistics / delivery ETL (Python + `itertools`) | Computing an optimal multi-stop delivery route from a `stops` table pulled each morning | A junior engineer implements "find best route" as "try every ordering of stops" | `min(itertools.permutations(stops), key=route_cost)` |
| Ad-hoc migration/script runner | Applying `n` schema migration or seed scripts whose real dependency order wasn't recorded | Trial-and-error: run every permutation of script order until one completes without a foreign-key error | `for order in itertools.permutations(scripts): try_run(order)` |

## 2. Where It Naturally Emerges

Factorial time shows up in DE work in two shapes:

- **Buried inside infrastructure you already use.** Every SQL join across more than a
  handful of tables is secretly a combinatorial optimization problem — "which order
  should I join these tables in to minimize intermediate result size?" Query planners
  exist specifically to *not* brute-force this, which is exactly why `join_collapse_limit`
  and `geqo_threshold` exist as tunables: past a certain table count, exhaustive search
  becomes too slow even for a query planner running once per query, so the planner itself
  downgrades to a cheaper (but not necessarily optimal) strategy.
- **Hand-rolled "try every ordering/assignment" scripts.** Route optimization for
  delivery/logistics data pipelines, scheduling `n` interdependent jobs when the real
  dependency graph wasn't captured, assigning `n` workers to `n` tasks by brute force
  instead of the Hungarian algorithm, or exhaustively testing every execution order of a
  flaky test suite to find a race condition. All of these are legitimate problems; the
  factorial-time version is almost always someone reaching for `itertools.permutations`
  before checking whether a purpose-built algorithm already exists for the shape of the
  problem.

## 3. Common Mistakes → Exceptions

**The mistake:** brute-forcing a combinatorial optimization problem that already has a
well-known, much better algorithmic approach. TSP is the canonical case — a data
engineer building a route-optimization step for a logistics pipeline reaches for
"generate every permutation of stops, pick the cheapest," when:

- An **exact** DP solution (Held-Karp, `O(n² · 2ⁿ)`, see `space-complexity.md` §3) already
  solves the same problem correctly with dramatically fewer operations, usable up to
  roughly `n ≈ 20–25`.
- An **approximation** (nearest-neighbor, `2-opt` local search, Christofides' algorithm)
  gets within a few percent of optimal in polynomial time and scales to thousands of
  stops — this is what `example.py`'s nearest-neighbor function demonstrates.
- A **production solver** (Google OR-Tools, Concorde) already implements all of the above
  plus decades of tuning, and is almost always the right call over hand-rolled code the
  moment the route-optimization step matters enough to be a "pipeline" rather than a
  one-off script.

The same mistake pattern shows up outside routing too: brute-force join order instead of
a query planner's DP/heuristic approach, brute-force task assignment instead of the
Hungarian algorithm (`O(n³)`), or brute-force script ordering instead of just reading the
dependency graph and topologically sorting it (`O(n + e)`, see `overview.md` §4's ETL
scripts example). In every case, the fix isn't "optimize the brute force" — it's
recognizing the *shape* of the problem (shortest path over permutations, bipartite
matching, dependency ordering) and reaching for the algorithm built for that shape.

**The exception:** genuinely tiny, *bounded* `n` — think `n ≤ 10`, sometimes up to
`n ≈ 12` if the job runs rarely and isn't latency-sensitive. At `n = 10`,
`9! = 362,880` permutations (fixing the start city) is a few hundred milliseconds of
work, as `example.py`'s benchmark shows directly — genuinely fine for a batch job that
runs once a day. The exception holds only while two things stay true:

1. **`n` is contractually or physically bounded**, not just "small today." A business
   rule like "this warehouse only ever routes to at most 8 loading docks" is a real bound.
   "We only have 9 customers right now" is not — it's a number that grows, and factorial
   growth punishes optimism about that more harshly than any other complexity class in
   this path (`n=12` is already ~20x slower than `n=10`; `n=15` is ~1,000x slower).
2. **Exact optimality matters enough to justify it.** If nearest-neighbor's ~5-15% gap
   (visible in `example.py`'s "nn gap" column) is acceptable, there's rarely a reason to
   pay for brute force even at small `n` — the only real justification for choosing
   factorial time on purpose is needing the provably optimal answer on an input small
   enough that "provably optimal" is affordable.

Outside of that narrow window, factorial time in a data pipeline is a bug waiting for
someone to increase `n`.
