# O(2ⁿ) — Algorithms

## Algorithm Index

- **Naive recursive Fibonacci** — recomputes overlapping sub-problems with no memory of past
  calls; `Θ(φⁿ)` calls, upper-bounded by `O(2ⁿ)`
- **Power set / subset generation** — every element independently in or out of a subset;
  exactly `Θ(2ⁿ)` subsets
- **Tower of Hanoi** — the textbook *exactly*-`2ⁿ` algorithm; moving n disks takes precisely
  `2ⁿ - 1` moves, no upper/tight-bound gap at all
- **Held-Karp / bitmask DP over subsets** (callout, not a full worked example) — a *smarter*
  exponential algorithm for TSP-shaped problems: still `O(2ⁿ)`-family, but strictly better than
  the `O(n!)` brute force it replaces (07-Onfactorial-factorial)

---

## Naive Recursive Fibonacci

**Background.** Fibonacci numbers (`F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)`) are the canonical
teaching example for "a mathematically clean recursive definition that is a performance trap
if implemented literally." It shows up constantly as the first example of recursion in CS
courses — and just as constantly as the first example of *why naive recursion isn't free*.

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

**Walkthrough.** Each call either hits a base case (`n <= 1`, O(1) work) or fans out into two
more calls. There's no cache, so `fib(n-2)` gets independently re-derived from scratch both as
a direct call from `fib(n)` *and* buried inside the recursive expansion of `fib(n-1)` — that
duplicated work is the entire source of the exponential blow-up (full derivation in
`overview.md`). See `space-complexity.md` for the memoized fix that collapses this to `O(n)`
time for the identical output.

**Reference:** [Fibonacci number — Wikipedia](https://en.wikipedia.org/wiki/Fibonacci_sequence)

---

## Power Set / Subset Generation

**Background.** Given a set of n elements, the power set is the set of *all* possible subsets,
including the empty set and the full set itself. It's the direct algorithmic embodiment of
"every element has 2 states (in / out), independently" — which is why its size is exactly `2ⁿ`,
not approximately, not on average: exactly. It underlies brute-force subset-sum, brute-force
knapsack, and the `GROUP BY CUBE` SQL feature covered in `de-application.md`.

```python
def subsets(elements):
    if not elements:
        return [[]]
    first, rest = elements[0], elements[1:]
    without_first = subsets(rest)
    with_first = [[first] + s for s in without_first]
    return without_first + with_first
```

**Walkthrough.** Base case: the empty list has exactly one subset (the empty subset itself).
Otherwise, take every subset of the *remaining* elements (`without_first`) and produce a second
copy of each with `first` added to it (`with_first`) — union the two halves. Every recursive
call doubles the count coming back up, bottoming out at exactly `2ⁿ` total subsets. An
equivalent, non-recursive way to generate the same `2ⁿ` subsets is bitmasking — treat each
integer from `0` to `2ⁿ - 1` as an n-bit mask of "which elements are included":

```python
def subsets_bitmask(elements):
    n = len(elements)
    for mask in range(1 << n):  # 0 .. 2^n - 1
        yield [elements[i] for i in range(n) if mask & (1 << i)]
```

This version streams one subset at a time (see `space-complexity.md`'s note on materialization)
and is the same pattern that shows up inside bitmask dynamic programming (below).

**Reference:** [Power set — Wikipedia](https://en.wikipedia.org/wiki/Power_set)

---

## Tower of Hanoi

**Background.** The oldest, purest teaching example of exactly-exponential behavior. Move n
disks from one peg to another, one at a time, never placing a larger disk on a smaller one,
using a spare peg. It's not "upper-bounded by 2ⁿ" the way Fibonacci is — the minimum number of
moves for n disks is **exactly** `2ⁿ - 1`, provably optimal.

```python
def hanoi(n, source, target, spare, moves):
    if n == 0:
        return
    hanoi(n - 1, source, spare, target, moves)
    moves.append((source, target))
    hanoi(n - 1, spare, target, source, moves)
```

**Walkthrough.** To move n disks from `source` to `target`: first move the top `n-1` disks out
of the way onto `spare` (recursively), then move the single largest disk directly to `target`,
then move those `n-1` disks from `spare` onto `target` (recursively, again). Recurrence:
`T(n) = 2·T(n-1) + 1`, which solves exactly to `T(n) = 2ⁿ - 1`. It's the cleanest possible
illustration of "the recursive structure itself doubles the work at every level" — no
data-dependent branching, no best/worst case gap, just the pure shape of the recursion.

**Reference:** [Tower of Hanoi — Wikipedia](https://en.wikipedia.org/wiki/Tower_of_Hanoi)

---

## LeetCode Pattern Callout

**Pattern: Subsets / Power-Set Backtracking (and its bitmask-DP cousin)**

**How to recognize it:** the problem statement asks for "all subsets," "all combinations,"
"every possible way to choose/partition/select," or "the power set of." Any time the answer is
a *collection of subsets themselves* (not just a count, and not just one best subset), you're
almost certainly looking at `2ⁿ`-shaped backtracking: at each element, branch into
include/exclude, and only prune if the problem gives you an explicit reason to stop early
(a sum limit, a duplicate to skip).

A closely related sub-pattern is **bitmask dynamic programming** — instead of generating each
subset explicitly, you use an n-bit integer to *represent* a subset as DP state (`dp[mask]` =
best answer using exactly the elements marked in `mask`). This is the technique behind
Held-Karp for the Traveling Salesman Problem: it's still exponential (`O(2ⁿ · n²)`), but it's a
massive improvement over the `O(n!)` brute-force permutation search it replaces
(07-Onfactorial-factorial) — the DP-over-subsets trick reuses overlapping "best route through
this subset of cities" answers instead of recomputing them per permutation, the same
memoization instinct as Fibonacci, applied to a harder problem.

**Example problems using this pattern:**
- LeetCode 78 — Subsets
- LeetCode 90 — Subsets II (with duplicates, needs a pruning rule)
- LeetCode 1125 — Smallest Sufficient Team (bitmask DP over "which skills are covered")
- LeetCode 698 — Partition to K Equal Sum Subsets (backtracking with pruning on partial sums)
