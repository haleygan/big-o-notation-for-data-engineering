# O(n!) — Space Complexity

## 1. Typical Space Cost

There are two very different numbers here, and mixing them up is the single most common
factorial-space mistake:

- **Generating permutations one at a time** (a recursive generator, Heap's algorithm, or
  Python's `itertools.permutations`, which is itself a generator): auxiliary space is
  just the recursion stack plus the buffer holding the *current* permutation, both of
  which are `O(n)` — the depth of "pick item 1, then item 2, ... then item n" is `n`
  frames deep, no more.
- **Materializing every permutation into a list at once** (e.g. `list(itertools.permutations(items))`):
  now you're holding all `n!` permutations, each of length `n`, in memory
  simultaneously — `O(n · n!)` auxiliary space. At `n = 10` that's 3,628,800 lists of 10
  items each: tens of millions of integers sitting in RAM at once, for a computation that
  never needed them all alive at the same time.

Brute-force TSP as written in `example.py` does the frugal version: it streams through
`itertools.permutations(remaining)` one tour at a time, checks its length, and discards
it — the running best tour is the only thing kept around, so *that* part of the algorithm
is `O(n)` auxiliary space even though it's `O(n!)` *time*. The failure mode is reaching
for `sorted(itertools.permutations(...), key=tour_length)` instead — that materializes
every permutation just to sort them, spending `O(n · n!)` space to answer a question that
only needed the single minimum.

## 2. Amortized Behavior

Not much applies here, and that's worth noting explicitly rather than forcing a fit.
Amortized analysis (concept.md §5) is about a *sequence of operations on the same
structure*, where occasional expensive operations average out over many cheap ones — the
dynatmic array/hash table story that lives in `01-O1-constant/01-O1-constant-space-complexity.md`.
Permutation generation doesn't have that shape: each permutation produced costs roughly
the same `O(1)` amount of *incremental* work (Heap's algorithm does one swap per step),
but the total *count* of permutations is fixed at `n!` by definition — there's no
"occasional expensive step among many cheap ones" pattern to amortize, just a flat-out
factorial number of steps, each one cheap. If you're looking for the amortized story in
this path, it lives in the constant-time folder, not here.

## 3. Local Time/Space Tradeoff

This is where factorial time gets genuinely interesting, and it's the single most
important tradeoff in this whole path to internalize: **you can trade space for a whole
complexity class**, not just a constant factor.

The Held-Karp dynamic programming algorithm solves TSP exactly using a different state
representation: instead of tracking "which specific permutation am I building," it tracks
`(set of cities visited, current city)` and memoizes the best cost to reach that state.
There are `2ⁿ` possible subsets and `n` possible "current city" values, so the DP table
has `O(n · 2ⁿ)` entries, and filling it takes `O(n² · 2ⁿ)` time — worse than polynomial,
but *dramatically* better than `O(n!)`. At `n = 20`: `20! ≈ 2.4 × 10¹⁸` vs.
`20² · 2²⁰ ≈ 4.2 × 10⁸` — roughly ten billion times fewer operations, paid for by
spending `O(n · 2ⁿ)` space on the memo table instead of `O(n)` on a recursion stack.

That's a direct instance of concept.md §5's core idea (memoization trading space for
time), just scaled up: instead of caching one overlapping subproblem's result, Held-Karp
caches `O(n · 2ⁿ)` of them, and the payoff is collapsing the time class from factorial to
"merely" exponential. It's still not fast — `2ⁿ` still explodes — but it's the difference
between "infeasible past n=13" and "usable up to roughly n=20–25" on typical hardware.
`06-O2n-exponential/06-O2n-exponential-algorithms.md` covers Held-Karp's mechanics in full; the point to take
from here is that the *space* line item is the thing you're paying to buy back time.

## 4. Worst-Case Space Deviation

Same theme as `overview.md` §1's Big O/Θ/Ω discussion: there usually isn't a worst-case
*deviation* here, because there's no adversarial input shape to deviate into. The
recursion stack for generating permutations is always exactly `n` deep, for every input,
every time — it's a function of `n` alone, not of what the distances or values are. If
you materialize all permutations, the space is always exactly `O(n · n!)`, again
regardless of the actual data. Contrast this with quicksort, where the recursion stack
average-cases at `O(log n)` but can degrade to `O(n)` on an adversarial pivot sequence
(covered in `05-On2-quadratic/05-On2-quadratic-space-complexity.md`) — that kind of best-case/worst-case
space gap doesn't exist for brute-force permutation generation, because the algorithm
does the same fixed amount of work no matter what's in the input.

## 5. Cross-Link

See root `capstone.md` for how this class's time/space profile stacks up against all 6
other classes, and specifically the memoization/space-for-time entry in the cross-class
tradeoff table — Held-Karp is the concrete DE-relevant version of that general pattern.
