# O(n!) — Factorial Time

## 1. Mathematical Definition

`n!` (n factorial) means `n × (n-1) × (n-2) × ... × 2 × 1`. It's the count of ways to
arrange `n` distinct items in order. 5 items → 120 orderings. 10 items → 3,628,800
orderings. 15 items → over 1.3 trillion. This is the steepest growth curve in this
entire path — steeper than `O(2ⁿ)`, because `2ⁿ` multiplies by a constant `2` each time
`n` grows by 1, while `n!` multiplies by a number that itself keeps growing (`n!` is
`n × (n-1)!`, so the multiplier at each step is `n` itself, not a fixed 2).

**Canonical algorithm:** brute-force Traveling Salesman Problem (TSP) — given `n`
cities and the distances between every pair, find the shortest possible loop that visits
all of them exactly once and returns to the start. The brute-force approach: generate
every possible ordering of the cities (every permutation), compute the total distance
for each one, keep the cheapest. Generating all permutations of `n` items is itself the
purest possible `O(n!)` example, and TSP is just "permutations + a cost function," so
we'll use both interchangeably below.

**Applying concept.md §2 (Big O vs Θ vs Ω) to this class.** For most complexity classes
in this path, worst/average/best case are three genuinely different scenarios driven by
*what the input looks like* — quicksort is fast on random data and slow on already-sorted
data, for instance. Brute-force TSP breaks that pattern: **every input of size `n` costs
the same**, regardless of what the actual distances are. The algorithm has no early exit
and no data-dependent shortcut — it always generates all `(n-1)!` permutations (fixing
one city as the start, since a loop and its rotations are the same tour) and evaluates
every single one. So for plain brute-force TSP:

- Best case: Θ(n!)
- Average case: Θ(n!)
- Worst case: Θ(n!)

All three collapse to the same tight bound. There's no adversarial *input shape* the way
there is for quicksort — the only thing that moves the needle is `n` itself. That said,
if you add **branch-and-bound pruning** (cut off a partial route early once its running
cost already exceeds the best complete tour found so far), the *average* case can improve
a lot in practice — most branches get pruned before they're fully explored — but the
*worst* case is still Θ(n!), because a pathological distance matrix (e.g., all distances
nearly equal) gives the pruning heuristic nothing to cut. That's the one place a "typical
vs. adversarial" distinction sneaks back in: adversarial input for pruned brute force is
input that defeats the bound-and-cut heuristic, not input that changes the raw
permutation count.

## 2. Derivation Walkthrough

Start from the simplest possible version: a recursive function that generates every
permutation of a list by picking each possible "next item" in turn.

```python
def permutations(remaining, current, results):
    if not remaining:
        results.append(current)
        return
    for i in range(len(remaining)):
        permutations(
            remaining[:i] + remaining[i+1:],
            current + [remaining[i]],
            results,
        )
```

Count the calls the way concept.md §3 describes — identify the basic operation (one
recursive call per item chosen), then count how many times it executes as a function of
`n`:

- At the top level, there are `n` choices for the first item.
- For each of those, there are `n-1` choices for the second item.
- For each of those, `n-2` choices for the third item.
- ...down to 1 choice for the last item.

Total leaf calls (complete permutations produced): `n × (n-1) × (n-2) × ... × 1 = n!`.
Each leaf also does `O(n)` work to build/copy the final ordering (or, for TSP, to sum up
`n` edge distances), so the fully precise cost is `O(n · n!)`. Following the same napkin
method from concept.md §1 — find the dominant term, drop everything that doesn't
dominate as `n → ∞` — the `n!` term dominates the extra linear factor so overwhelmingly
that essentially every textbook and interview answer just writes `O(n!)`. It's worth
knowing the more precise `O(n · n!)` exists under the hood, the same way `O(n log n)`
sorts have a "with a small constant" footnote that doesn't change the class.

## 3. Visual Graph

Factorial growth is so extreme that plotting it on a normal linear axis makes every other
curve look like a flat line at the bottom. The table below shows raw operation counts for
`n = 1` through `10`, followed by an ASCII chart on a log scale (each `#` ≈ half an order
of magnitude) so you can see how the gap opens up:

| n | O(n) | O(n²) | O(2ⁿ) | O(n!) |
|---|---|---|---|---|
| 1 | 1 | 1 | 2 | 1 |
| 2 | 2 | 4 | 4 | 2 |
| 3 | 3 | 9 | 8 | 6 |
| 4 | 4 | 16 | 16 | 24 |
| 5 | 5 | 25 | 32 | 120 |
| 6 | 6 | 36 | 64 | 720 |
| 7 | 7 | 49 | 128 | 5,040 |
| 8 | 8 | 64 | 256 | 40,320 |
| 9 | 9 | 81 | 512 | 362,880 |
| 10 | 10 | 100 | 1,024 | 3,628,800 |

```
Operation count at n = 10, log10 scale (each # ≈ half an order of magnitude)

n     (10)                #
n²    (100)                ####
2ⁿ    (1,024)               ######
n!    (3,628,800)           #############

                    0      1      2      3      4      5      6   (log10 scale)
```

Notice `n!` already overtakes `2ⁿ` by `n = 4` (24 vs. 16), and by `n = 10` it's roughly
3,500x bigger than `2ⁿ`, and 36,000x bigger than `n²`. This is why the "just add more
compute" instinct doesn't work here the way it sometimes limps along for `O(2ⁿ)` — going
from `n=10` to `n=15` doesn't 32x the work like `2ⁿ` would, it multiplies it by
`11 × 12 × 13 × 14 × 15 ≈ 360,000x`.

## 4. Layman Explanation

Picture a data engineer with a folder of 10 ETL scripts that have to run in some
particular order, but the dependency metadata got lost — nobody documented which script
depends on which. A junior engineer, not wanting to read the SQL to figure out the real
dependency graph, writes a "smart" scheduler: it tries running the scripts in every
possible order, and whichever order finishes without a foreign-key error is "the"
order.

For 5 scripts, that's 120 orderings to try — annoying, but a computer chews through it in
milliseconds. For 10 scripts, it's 3,628,800 orderings. For 15 scripts, it's over 1.3
trillion — the job would still be running long after everyone on the team has changed
roles twice. The actual fix costs almost nothing by comparison: read the foreign keys (or
the `dbt` DAG, or the Airflow task dependencies) once, build a real dependency graph, and
topologically sort it — an `O(n + e)` operation from the `03-On-linear` class, done in one
pass, correct every time, with zero trial and error. That gap — between "try every
ordering" and "read the one ordering the data already implies" — is the entire lesson of
this complexity class: factorial-time solutions are almost always a sign that a smarter,
structure-aware algorithm was available and skipped.

See `../concept.md` §1–§3 for the general Big O / derivation method this section applies,
and `../06-O2n-exponential/06-O2n-exponential-overview.md` for the next class down, which this class
dwarfs by `n = 10`.
