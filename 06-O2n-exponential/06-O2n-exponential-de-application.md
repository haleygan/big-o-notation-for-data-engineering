# O(2ⁿ) — In Data Engineering

Most DE tools work hard to *avoid* landing here — this is the class where "it works on my
laptop with 10 rows" turns into "it never returns" the moment n crosses into the twenties or
thirties. But it does show up, usually in one of two shapes: (1) a tool deliberately enumerates
every combination of something small and bounded (grouping sets, feature subsets, flag
combinations), or (2) someone wrote a recursive solution to a problem with overlapping
sub-problems and forgot to cache.

## DE Technology Examples

| Technology | Operation | Why this complexity | Minimal code sample |
|---|---|---|---|
| SQL `GROUP BY CUBE` (Postgres, Spark SQL, Snowflake, BigQuery) | Generating all grouping-set combinations across n columns | `CUBE(c1..cn)` is *defined* as every subset of the n columns being its own grouping set — 2ⁿ subsets, by design | `SELECT region, product, SUM(sales) FROM orders GROUP BY CUBE(region, product);` — 2 columns → 4 grouping sets: `(region,product)`, `(region)`, `(product)`, `()` |
| Postgres query planner | Join-order search for a multi-table query | Naive dynamic programming over "which subset of tables have I joined so far" — `2ⁿ` subsets of n tables, each considered as a possible join state | Above `geqo_threshold` (default 12 tables), Postgres switches from exhaustive DP search to a genetic algorithm specifically to dodge this blow-up: `SHOW geqo_threshold;` |
| Spark Catalyst optimizer | Cost-based join reordering for n-way joins | Same shape as above — exploring subsets of relations to find the cheapest join order before falling back to greedy heuristics on large joins | `spark.sql.cbo.enabled=true` plus `spark.sql.cbo.joinReorder.dp.threshold` — the config name literally says "dynamic programming" and caps it for exactly this reason |
| `mlxtend.feature_selection.ExhaustiveFeatureSelector` | Brute-force feature selection for a model | Tries every subset of the n candidate features and fits a model on each, to find the best-scoring subset | `from mlxtend.feature_selection import ExhaustiveFeatureSelector as EFS; efs = EFS(model, min_features=1, max_features=n)` |
| Feature-flag / config QA tooling (e.g. combinatorial test suites before a release) | Testing every on/off combination of n flags | Power set of flags — each flag independently on or off, `2ⁿ` configurations to validate | `from itertools import product; all_configs = list(product([True, False], repeat=n))` |

## Where It Naturally Emerges

- **Unmemoized recursive definitions with overlapping sub-problems.** Anything that recurses
  the way Fibonacci does — where a sub-problem gets asked for more than once along different
  branches — lands here by default unless someone deliberately caches. Recursive rollups,
  naive recursive edit-distance/similarity scoring, and naive recursive dynamic-programming
  problems written *without* the DP part (i.e., without the memo table) are all the same
  mistake wearing different clothes.
- **"Give me every combination" requirements.** Any spec that says "test/generate/check every
  possible combination of these n things" is asking for a power set, whether or not anyone
  says the words "power set." Feature-flag QA, exhaustive A/B config sweeps, and brute-force
  hyperparameter grids over binary choices all land here structurally, not by accident.
  `GROUP BY CUBE` is this same shape turned into a first-class SQL feature.
- **Cost-based query and plan optimizers, before their exponential blow-up point.** Any planner
  that tries to find the *optimal* order for combining n things (join order, execution plan
  ordering) by exploring subsets is doing `O(2ⁿ)`-shaped search under the hood. That's exactly
  why real planners cap it (Postgres's `geqo_threshold`, Spark's `joinReorder.dp.threshold`)
  and fall back to a cheaper heuristic once n crosses that line — they're not solving the
  problem "better," they're refusing to keep paying the exponential price past a point where
  it stops being worth it.

## Common Mistakes → Exceptions

**The mistake:** writing a recursive solution to a problem with overlapping sub-problems and
not memoizing it — the single most common way a pipeline accidentally lands in this class.
Someone writes a clean, "obviously correct" recursive definition (a rollup, a recursive
lineage/dependency check, a naive recursive similarity score), it works fine in a unit test
with n=5, and then it's asked to run on n=25 in production and either takes minutes or never
returns. The fix is almost always `space-complexity.md`'s trade: add a cache, drop a
complexity class, done — this is the single highest-leverage fix available in this entire
class, more impactful than almost any other optimization you could reach for instead.

**When it's still an acceptable tradeoff:**
- **n is small and hard-bounded, permanently.** `GROUP BY CUBE` over 4-5 dimensions is 16-32
  grouping sets — trivial, and nobody's cube has 30 dimensions. Feature-flag combinatorial QA
  over 10-15 flags (1,024-32,768 configs) is annoying but survivable as a nightly CI job, not
  a real-time path.
- **The exhaustive search is explicitly bounded by policy, not by hope.** Postgres's
  `geqo_threshold=12` and Spark's DP join-reorder threshold are exactly this: "exhaustive is
  fine below this line, and we refuse to do it above the line." That's the class handled
  correctly — not avoided everywhere, just fenced off from the n values where it would hurt.
- **One-off exploratory or brute-force scripts where n is guaranteed small forever** (a
  feature-selection sweep over a fixed, small candidate feature list; a one-time data-quality
  audit over a handful of columns). If n will never realistically grow, the exponential label
  is technically true and practically irrelevant.
