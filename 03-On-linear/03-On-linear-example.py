"""
O(n) — Linear Time: benchmark.

Same problem, two strategies: join two tables of records on a matching integer key.

  - nested_loop_join : O(n * m)  -- compare every row of A against every row of B
  - hash_join        : O(n + m)  -- build a hash table on the smaller side, probe
                                    with the larger (concept.md section 6:
                                    multi-variable linear time)

Run directly:
    python3 example.py
"""

import time
import random


# ---------------------------------------------------------------------------
# 1. Imports + timing utility (above): `time` for wall-clock measurement.
# ---------------------------------------------------------------------------

def time_it(fn, *args):
    """Run fn(*args) once, return (result, elapsed_seconds)."""
    start = time.perf_counter()
    result = fn(*args)
    elapsed = time.perf_counter() - start
    return result, elapsed


# ---------------------------------------------------------------------------
# 2. The O(n * m) approach: nested-loop join.
#    For every row in A, scan every row in B looking for a matching key.
# ---------------------------------------------------------------------------

def nested_loop_join(table_a, table_b, key="key"):
    results = []
    for row_a in table_a:              # n iterations
        for row_b in table_b:          # m iterations each -> n * m total
            if row_a[key] == row_b[key]:
                results.append((row_a, row_b))
    return results


# ---------------------------------------------------------------------------
# 3. The O(n + m) approach: hash join.
#    Build a hash table over the smaller side once (O(n) amortized inserts),
#    then probe it with every row of the larger side (O(m) average lookups).
# ---------------------------------------------------------------------------

def hash_join(table_a, table_b, key="key"):
    # Always build the hash table on the smaller side -- keeps build-side
    # memory at O(min(n, m)), per space-complexity.md section 3.
    if len(table_a) > len(table_b):
        table_a, table_b = table_b, table_a

    build_side = {}
    for row in table_a:                          # O(n): build phase
        build_side.setdefault(row[key], []).append(row)

    results = []
    for row in table_b:                          # O(m): probe phase
        for match in build_side.get(row[key], ()):
            results.append((match, row))
    return results


def make_table(n, key_space, seed):
    rng = random.Random(seed)
    return [{"key": rng.randint(0, key_space - 1), "value": i} for i in range(n)]


# ---------------------------------------------------------------------------
# 4. Benchmark loop across increasing n, printing a timing comparison table.
# ---------------------------------------------------------------------------

def run_benchmark():
    sizes = [50, 100, 250, 500, 1000, 2000, 3000]

    header = f"{'n (rows/side)':>15} | {'nested-loop O(n*m)':>20} | {'hash join O(n+m)':>18} | {'speedup':>9}"
    print(header)
    print("-" * len(header))

    for n in sizes:
        # A modest key space so there are real matches to find on both sides,
        # without every row colliding into one giant bucket.
        key_space = max(n // 10, 1)
        table_a = make_table(n, key_space, seed=1)
        table_b = make_table(n, key_space, seed=2)

        _, t_nested = time_it(nested_loop_join, table_a, table_b)
        _, t_hash = time_it(hash_join, table_a, table_b)

        speedup = t_nested / t_hash if t_hash > 0 else float("inf")
        print(f"{n:>15} | {t_nested:>17.5f}s | {t_hash:>15.5f}s | {speedup:>8.1f}x")


if __name__ == "__main__":
    # Sanity check first: both strategies must agree on *what* they find,
    # they should only differ in *how long it takes* to find it.
    sample_a = make_table(30, key_space=5, seed=1)
    sample_b = make_table(30, key_space=5, seed=2)
    nested_result = sorted(
        (a["value"], b["value"]) for a, b in nested_loop_join(sample_a, sample_b)
    )
    hash_result = sorted(
        (a["value"], b["value"]) for a, b in hash_join(sample_a, sample_b)
    )
    assert nested_result == hash_result, "join strategies disagree on results!"

    run_benchmark()

    # -------------------------------------------------------------------
    # 5. Takeaway
    #
    # Both strategies solve the exact same join. nested_loop_join compares
    # every row of A against every row of B: n * m comparisons -- doubling
    # either table roughly doubles (or quadruples, if both grow) the work.
    # hash_join builds a hash table over one side once, then does a single
    # O(1)-average lookup per row of the other side: n + m work total.
    #
    # At n = 50 the gap is barely visible -- a few thousand comparisons
    # either way runs in microseconds. By n = 1000, nested-loop is doing
    # ~1,000,000 comparisons per join versus hash join's ~2,000 lookups,
    # and the speedup column above should already be in the hundreds.
    # By n = 3000 the nested-loop version is doing ~9,000,000 comparisons
    # and visibly takes seconds, while hash join barely moves. This is
    # exactly why query planners (Spark, Postgres, DuckDB) switch to a
    # hash join whenever one side of a join can fit in memory -- O(n + m)
    # beats O(n * m) by a widening margin as both sides grow.
    # -------------------------------------------------------------------
