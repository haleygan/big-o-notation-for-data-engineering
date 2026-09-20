"""
O(2^n) vs O(n) -- Naive Recursive Fibonacci vs Memoized Fibonacci
===================================================================

Same problem (the nth Fibonacci number), two implementations, two different
time-complexity classes. This is the "spend O(n) space to drop a whole time
complexity class" trade-off walked through in space-complexity.md.

Run it directly:
    python3 example.py
"""

import time
from functools import lru_cache


# ---------------------------------------------------------------------------
# 1. THIS complexity: O(2^n) time / O(n) space -- naive recursive Fibonacci
# ---------------------------------------------------------------------------
def fib_naive(n: int) -> int:
    """Textbook exponential-time Fibonacci.

    No memory of past calls, so overlapping sub-problems (fib(n-2), fib(n-3),
    ...) get recomputed from scratch every time they're reached, no matter how
    many times before. Total calls made is Theta(phi^n), phi ~= 1.618 (the
    golden ratio) -- upper-bounded by, and commonly just called, O(2^n).
    Recursion depth (and therefore call-stack space) is only O(n): at any
    instant only one root-to-leaf path is on the stack.
    """
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


# ---------------------------------------------------------------------------
# 2. CONTRASTING/better complexity: O(n) time / O(n) space -- memoized
# ---------------------------------------------------------------------------
def fib_memo(n: int, cache: dict) -> int:
    """Same recursive shape as fib_naive, but a dict cache means every one of
    the n distinct sub-problems (fib(0) .. fib(n)) gets solved exactly once.
    n distinct sub-problems, O(1) marginal work each -> O(n) time overall.
    The cache costs O(n) space -- memory deliberately spent to buy back a
    whole time-complexity class (see space-complexity.md).
    """
    if n <= 1:
        return n
    if n in cache:
        return cache[n]
    result = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)
    cache[n] = result
    return result


@lru_cache(maxsize=None)
def fib_lru(n: int) -> int:
    """Identical idea to fib_memo, using functools.lru_cache as the cache
    instead of a hand-rolled dict -- included to show the standard-library
    shortcut for the same trade-off."""
    if n <= 1:
        return n
    return fib_lru(n - 1) + fib_lru(n - 2)


# ---------------------------------------------------------------------------
# 3. Benchmark across increasing n
# ---------------------------------------------------------------------------
def time_call(fn, *args) -> float:
    start = time.perf_counter()
    fn(*args)
    return time.perf_counter() - start


def main():
    ns = [10, 15, 20, 25, 28, 30]

    header = f"{'n':>4} | {'naive O(2^n) (s)':>18} | {'memoized O(n) (s)':>18} | {'speedup':>10}"
    print(header)
    print("-" * len(header))

    for n in ns:
        naive_time = time_call(fib_naive, n)

        # fresh cache each n so the memoized timing isn't "free" from a
        # previous n's warmed-up cache -- we want a fair, independent measure
        # of fib_memo's own cost at this n.
        memo_time = time_call(fib_memo, n, {})

        speedup = naive_time / memo_time if memo_time > 0 else float("inf")
        print(f"{n:>4} | {naive_time:>18.6f} | {memo_time:>18.8f} | {speedup:>9.1f}x")

    # Sanity check: both approaches must agree on the actual answer.
    for n in ns:
        assert fib_naive(n) == fib_memo(n, {}) == fib_lru(n)
    fib_lru.cache_clear()
    print("\nAll results verified equal across fib_naive, fib_memo, fib_lru.")


if __name__ == "__main__":
    main()


# -----------------------------------------------------------------------------
# Takeaway
# -----------------------------------------------------------------------------
# At n=10 or n=15, naive recursion looks totally fine -- microseconds either
# way, the exponential curve hasn't taken off yet. By n=25-30 the gap becomes
# impossible to ignore: naive recursion is redoing exponentially many
# repeated sub-calculations, while the memoized version does exactly n new
# units of work no matter how large n gets, because every distinct
# sub-problem is solved once and reused. The crossover point where this
# starts to matter isn't "huge n" -- it's usually already happening by the
# time n reaches the low 20s to low 30s. That's the general lesson of this
# whole complexity class: exponential algorithms don't degrade gracefully,
# they degrade suddenly, right around the n you thought was still "small."
