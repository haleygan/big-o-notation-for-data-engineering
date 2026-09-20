# O(n!) — Algorithms

## 1. Algorithm Index

- **Permutation generation (recursive / Heap's algorithm)** — produce every possible
  ordering of `n` distinct items; the purest `O(n!)` algorithm, and the building block
  every other algorithm on this page uses.
- **Brute-force Traveling Salesman Problem (TSP)** — try every permutation of a route to
  find the minimum-cost tour visiting all `n` cities exactly once.
- **Brute-force N-Queens (permutation-checking variant)** — place `n` queens on an `n×n`
  board, one per row and one per column, by trying every column-permutation and checking
  for diagonal conflicts.
- **Held-Karp dynamic programming** — not itself `O(n!)`, but included here as *the*
  escape hatch: it solves the exact same TSP problem in `O(n² · 2ⁿ)`, and every DE who
  hits factorial time on a real routing problem needs to know this exists.

## 2. Permutation Generation (Heap's Algorithm)

**Background/context.** Every algorithm below needs to enumerate orderings. The naive
way — pick any unused item, recurse on the rest — works (it's what `overview.md` §2
walks through), but it rebuilds a new list at every recursive call. Heap's algorithm
(B. R. Heap, 1963) generates the same `n!` permutations using a single array and one
swap per step, which is why it's the standard reference implementation in most
textbooks and why Python's `itertools.permutations` uses a variant of it internally.

**Code sample:**

```python
def heaps_algorithm(arr, n=None, results=None):
    if n is None:
        n = len(arr)
        results = []
    if n == 1:
        results.append(arr[:])
        return results

    for i in range(n):
        heaps_algorithm(arr, n - 1, results)
        if n % 2 == 0:
            arr[i], arr[n - 1] = arr[n - 1], arr[i]
        else:
            arr[0], arr[n - 1] = arr[n - 1], arr[0]
    return results
```

**Walkthrough.** The function recurses down to a base case of a single-element
sub-array (`n == 1`), at which point the current arrangement of `arr` is one complete
permutation, so it gets copied into `results`. Coming back up each recursion level, it
swaps exactly one pair of elements before trying the next arrangement — which element
gets swapped depends on whether the current sub-problem size `n` is even or odd, and
that alternation is the trick that guarantees every permutation is hit exactly once
with only a single swap between them. The recursion tree has exactly `n!` leaves (same
counting argument as `overview.md` §2), and each internal node does `O(1)` swap work, so
total work is `O(n!)`.

**Reference:** [Heap's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Heap%27s_algorithm)

## 3. Brute-Force Traveling Salesman Problem

**Background/context.** TSP asks for the shortest closed loop visiting every one of `n`
locations exactly once — routing, circuit board drilling, DNA sequencing fragment
assembly, and (per `de-application.md`) real logistics/delivery pipelines all reduce to
this. It's the canonical NP-hard combinatorial optimization problem: no known algorithm
solves it exactly in polynomial time, and brute force is the "obviously correct, but
does not scale" baseline every smarter approach is measured against.

**Code sample** (full working version lives in `example.py`; core logic below):

```python
import itertools

def brute_force_tsp(dist):
    n = len(dist)
    best_tour, best_length = None, float("inf")
    for perm in itertools.permutations(range(1, n)):
        candidate = (0,) + perm
        length = sum(
            dist[candidate[i]][candidate[(i + 1) % n]]
            for i in range(n)
        )
        if length < best_length:
            best_tour, best_length = candidate, length
    return best_tour, best_length
```

**Walkthrough.** City `0` is fixed as the start — a tour and its rotations describe the
same physical loop, so fixing one city removes redundant rotations without changing the
growth class (still `(n-1)!`, still factorial). `itertools.permutations` streams every
ordering of the remaining cities one at a time (see `space-complexity.md` §1 for why
that streaming matters for memory). Each candidate ordering is scored by summing `n`
edge distances, including the wrap-around edge back to city 0, and the minimum across
all `(n-1)!` candidates is kept. This is exactly the algorithm benchmarked in
`example.py` against the nearest-neighbor heuristic.

**Reference:** [Travelling salesman problem — Wikipedia](https://en.wikipedia.org/wiki/Travelling_salesman_problem)

## 4. Brute-Force N-Queens (Permutation-Checking Variant)

**Background/context.** Place `n` chess queens on an `n×n` board so none attacks another
— no shared row, column, or diagonal. Representing "one queen per row, one queen per
column" as a permutation (`perm[row] = column`) automatically satisfies the row/column
constraints, shrinking the search from `n^n` (every cell combination) down to `n!`
(every column-permutation) — you only need to check diagonals against every permutation.

**Code sample:**

```python
def n_queens_brute_force(n):
    solutions = []
    for perm in itertools.permutations(range(n)):
        if all(
            abs(perm[i] - perm[j]) != abs(i - j)
            for i in range(n)
            for j in range(i + 1, n)
        ):
            solutions.append(perm)
    return solutions
```

**Walkthrough.** `perm[row] = column` means row/column collisions are impossible by
construction (permutations don't repeat values), so the only thing left to check is
diagonal attacks: two queens share a diagonal exactly when the difference in their
columns equals the difference in their rows (`abs(perm[i] - perm[j]) == abs(i - j)`).
The check itself is `O(n²)` per permutation, run across `n!` permutations — `O(n² · n!)`
total, still dominated by the factorial term. (Production N-Queens solvers use
backtracking with early pruning instead, cutting off a branch the moment a partial
placement conflicts — average-case much faster, worst-case still exponential-ish, a
similar space/time story to the branch-and-bound TSP note in `overview.md` §1.)

**Reference:** [Eight queens puzzle — Wikipedia](https://en.wikipedia.org/wiki/Eight_queens_puzzle)

## 5. Held-Karp — The Way Out

**Background/context.** Included here even though it isn't `O(n!)`, because
"what do I do instead" is the single most useful thing to walk away from this folder
knowing. Held-Karp reframes TSP's state as `(set of cities already visited, current
city)` instead of "which full permutation am I building," and memoizes the best cost
for each state — collapsing the time complexity from `O(n!)` to `O(n² · 2ⁿ)` at the cost
of `O(n · 2ⁿ)` memo-table space (full mechanics and the space tradeoff are in
`space-complexity.md` §3, and the algorithm itself belongs to and is detailed in
`06-O2n-exponential/06-O2n-exponential-algorithms.md`, since `2ⁿ` is its actual complexity class).

**Reference:** [Held–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm)

## 6. LeetCode Pattern Callout

**Pattern: Permutations / backtracking over orderings.** Recognize it in a problem
statement by phrasing like "return all possible orderings/arrangements," "find an
arrangement such that...," or "try every ordering to find the best one" — anything where
the *order* of elements is the thing being searched over, not just which elements are
included (that's the subset/combination pattern from `06-O2n-exponential`, a different
`O(2ⁿ)` shape). The standard implementation is backtracking with a `used[]` boolean array
(or swap-in-place, like Heap's algorithm above) to avoid reusing an element twice in the
same partial ordering.

Example problems at this complexity:
- **LeetCode 46 — Permutations** (distinct integers, return all orderings)
- **LeetCode 47 — Permutations II** (with duplicates — same pattern, plus a dedup check)
- **LeetCode 51 — N-Queens** (the permutation-checking framing above, dressed up as
  backtracking-with-pruning)
- **LeetCode 996 — Number of Squareful Arrays** (permutation search with an extra
  adjacency constraint, same backtracking skeleton)

If an interview question follows up with "how would you make this scale to a much larger
`n`?" — that's the interviewer pointing you toward exactly the DP/heuristic escape hatch
in `de-application.md` §3 and `space-complexity.md` §3, not a cleverer way to brute force.
