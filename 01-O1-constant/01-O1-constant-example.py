"""
example.py — O(1) Constant Time, benchmarked against O(n) Linear Time

Two benchmarks, both built around this folder's canonical structures:

  1. Membership check: hash table lookup (set) -- O(1) average -- vs. a list
     scan -- O(n) worst case -- for the exact same question: "is `target` in
     this collection?"

  2. Growth: dynamic array append (`list.append`, amortized O(1) per call --
     see space-complexity.md Section 2) vs. naive rebuild-by-concatenation
     (`result + [i]`, O(n) per call because it copies the whole list every
     time) -- building up the same list, n items, two different ways.

Run directly:
    python3 example.py
"""

import timeit


# ---------------------------------------------------------------------------
# Benchmark 1 -- membership check: hash table O(1) vs. list scan O(n)
# ---------------------------------------------------------------------------

def contains_hash(collection: set, target: int) -> bool:
    """O(1) average case -- hash `target` straight to a bucket and check it."""
    return target in collection


def contains_linear(collection: list, target: int) -> bool:
    """O(n) worst case -- scans element by element until found or exhausted."""
    return target in collection


def benchmark_membership(sizes: list[int]) -> None:
    print(f"{'n':>10} | {'set O(1) (ms)':>15} | {'list O(n) (ms)':>16} | {'speedup':>8}")
    print("-" * 62)
    for n in sizes:
        data_list = list(range(n))
        data_set = set(data_list)
        target = -1  # not present -- forces a full scan on the list side

        # scale repeat count down as n grows, so the list-scan case doesn't
        # dominate total run time while still giving a stable measurement
        reps = max(50, 200_000 // n)

        t_set = timeit.timeit(lambda: contains_hash(data_set, target), number=reps)
        t_list = timeit.timeit(lambda: contains_linear(data_list, target), number=reps)

        ms_set = (t_set / reps) * 1000
        ms_list = (t_list / reps) * 1000
        speedup = ms_list / ms_set if ms_set > 0 else float("inf")
        print(f"{n:>10,} | {ms_set:>15.5f} | {ms_list:>16.5f} | {speedup:>7.1f}x")


# ---------------------------------------------------------------------------
# Benchmark 2 -- growth: dynamic array append (amortized O(1)) vs.
# concatenation rebuild (O(n) per call)
# ---------------------------------------------------------------------------

def build_with_append(n: int) -> list:
    """Amortized O(1) per append. Occasional O(n) resize copies, but spaced
    out geometrically across n appends -> O(n) total -> O(1) each on average.
    See space-complexity.md Section 2 for the aggregate-method derivation."""
    result = []
    for i in range(n):
        result.append(i)
    return result


def build_with_concat(n: int) -> list:
    """O(n) per call -- `result + [i]` allocates a brand-new list and copies
    every existing element into it, every single time. Doing that n times is
    O(n) work performed n times -> O(n^2) total."""
    result = []
    for i in range(n):
        result = result + [i]
    return result


def benchmark_growth(sizes: list[int]) -> None:
    print(f"\n{'n':>10} | {'append (ms)':>13} | {'concat (ms)':>13} | {'speedup':>8}")
    print("-" * 55)
    for n in sizes:
        reps = 5
        t_append = timeit.timeit(lambda: build_with_append(n), number=reps) / reps
        t_concat = timeit.timeit(lambda: build_with_concat(n), number=reps) / reps

        ms_append = t_append * 1000
        ms_concat = t_concat * 1000
        speedup = ms_concat / ms_append if ms_append > 0 else float("inf")
        print(f"{n:>10,} | {ms_append:>13.4f} | {ms_concat:>13.4f} | {speedup:>7.1f}x")


if __name__ == "__main__":
    print("=== Benchmark 1: membership check -- hash table O(1) vs. list scan O(n) ===")
    benchmark_membership([1_000, 10_000, 100_000, 500_000])

    print("\n=== Benchmark 2: growth -- dynamic array append O(1) amortized vs. concat O(n) ===")
    benchmark_growth([500, 1_000, 2_000, 4_000])

    # -------------------------------------------------------------------
    # Takeaway:
    #
    # Benchmark 1 -- the set lookup time barely moves as n grows 500x
    # (1,000 -> 500,000). The list scan time grows roughly in step with n,
    # because a "not found" search has to walk the entire list. The gap is
    # invisible at n=1,000 (both sub-millisecond) but by n=500,000 the list
    # scan is dramatically slower. This is exactly why "have I seen this ID
    # before" should be backed by a set/dict, not a list, once n stops being
    # tiny -- a decision that shows up constantly in streaming dedup.
    #
    # Benchmark 2 -- build_with_concat is O(n) per call, so building a list
    # of size n by looping n times costs O(n^2) total (n calls, each an O(n)
    # copy). build_with_append pays an O(n) resize occasionally, but that
    # cost is amortized across all n appends -> O(1) each on average. Watch
    # the concat column: doubling n roughly quadruples its time (the n^2
    # signature), while append's time roughly doubles when n doubles (linear
    # overall, O(1) per call). This is the concrete version of the amortized
    # argument in space-complexity.md Section 2.
    # -------------------------------------------------------------------
