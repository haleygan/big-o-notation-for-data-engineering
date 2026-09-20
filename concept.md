# Big O Notation — The Concepts Behind This Whole Path

Before you get into the 7 complexity folders, read this once. Every folder after this
assumes you already have these ideas — nobody re-derives "what does Θ mean" or "what is
amortized cost" seven more times. If a later file ever seems to skip a step, it's because
the step lives here.

Goal of this whole path: not "know what O(n²) means" — it's to be able to look at a data
processing problem and pick the right strategy under real constraints (time, memory,
latency). This file is the toolbox; the folders are the applied practice.

---

## 1. What Big O Notation Actually Is

Big O describes how a cost — usually time or memory — grows as input size `n` grows.
It does **not** describe how many seconds something takes. Two implementations of the
same O(n) algorithm can run at wildly different speeds; Big O only tells you *the shape
of the curve* as `n` gets large, not where the curve sits.

Formally: `f(n) = O(g(n))` if there exist constants `c > 0` and `n₀` such that
`f(n) ≤ c · g(n)` for all `n ≥ n₀`. In plain English: past some point, `f(n)` never
outgrows `g(n)` by more than a constant factor.

**Why we drop constants and lower-order terms.** Say your algorithm actually does
`3n + 5` operations. At `n = 10`, that's 35 — the `+5` is a third of the total, it looks
like it matters. At `n = 10,000,000`, it's 30,000,005 — the `+5` is utterly irrelevant
and even the `3×` barely matters compared to *which* term has the highest power of `n`.
Big O is about what dominates as `n → ∞`, so we simplify `3n + 5` down to `O(n)`.

The practical method ("napkin method"):
1. Find the term with the highest growth rate (the one that would win a race as `n → ∞`)
2. Drop its constant coefficient
3. Drop every other (lower-order) term

`3n² + 100n + 7` → `O(n²)`. The `100n` looks big for small `n`, but it loses to `n²`
eventually, and Big O only cares about eventually.

---

## 2. Big O vs Θ vs Ω — Upper, Tight, and Lower Bound

Three related symbols, three different claims:

| Symbol    | Name      | Claim                           | Reads as                         |
| --------- | --------- | ------------------------------- | -------------------------------- |
| `O(g(n))` | Big O     | Upper bound                     | "Never worse than this"          |
| `Ω(g(n))` | Big Omega | Lower bound                     | "Never better than this"         |
| `Θ(g(n))` | Big Theta | Tight bound (both of the above) | "This, exactly, up to constants" |

When someone casually says "quicksort is O(n log n)," what they usually *mean* is
Θ(n log n) — the typical, expected behavior. But that's the **average case**. Quicksort's
actual worst case is Θ(n²): a specific input shape (already-sorted data against a naive
pivot choice, for instance) breaks the assumption the average-case analysis relies on.

This is why every folder in this path explicitly separates:
- **Best case** — the friendliest possible input
- **Average case** — typical/random input (usually what "the complexity" colloquially means)
- **Worst case** — the input shape that's actively bad for this algorithm

...and gives you the specific input shape that causes the worst case, because in
production, adversarial-shaped input isn't rare — it's things like already-sorted
timestamps, or a single hot key. Knowing *what breaks it* is more useful than the label.

---

## 3. Time Complexity — How To Actually Derive It

"Time" here means **operation count as a function of `n`**, not wall-clock seconds —
seconds depend on your CPU, language, and whether the cache was warm. Operation count
doesn't.

General method:
1. Identify the **basic operation** — the thing that happens once per "unit of work"
   (a comparison, a hash lookup, an array access)
2. Count how many times it executes, as a function of `n`
3. Simplify to the dominant term (§1's napkin method)

One loop over `n` items, one operation per iteration → `O(n)`. A loop over `n` items,
each doing a loop over `n` items → `O(n²)`. A loop that halves the search space each
iteration → `O(log n)`. Each complexity folder's "Derivation walkthrough" applies this
exact method to one canonical algorithm, in detail.

**Reading complexity from benchmark data (the doubling test).** Deriving `f(n)` from code
works when you can read the code. Often you can't — a third-party library, a black-box
API, a system you're profiling in production. In that case you can go the other
direction: run the same operation at `n` and at `2n`, and see how the elapsed time
reacts. Each complexity class has a distinct doubling signature:

| Complexity | What happens when `n` doubles |
|---|---|
| `O(1)` | No change |
| `O(log n)` | Barely changes — adds roughly one more step |
| `O(n)` | Roughly doubles |
| `O(n log n)` | Slightly more than doubles |
| `O(n²)` | Roughly quadruples |
| `O(n³)` | Roughly 8x |
| `O(2ⁿ)` | Squares — an entirely different regime, not a fixed multiplier |

This is a real diagnostic tool, not just a classroom trick: it's how you infer the
complexity of code you can't or don't want to read line-by-line. Every complexity
folder's `example.py` prints a timing table across increasing `n` for exactly this
reason — the ratio column in that output is this doubling signature made visible. Two
caveats worth knowing before trusting a doubling test on real numbers: at small `n`,
constant-factor overhead (function call cost, cache effects) can swamp the signature and
make an `O(n)` operation look flat; and this only tells you the *shape*, not which
specific algorithm is running it — an `O(n)` signature is consistent with many different
linear algorithms.

---

## 4. Space Complexity — The Other Half

Space complexity is derived the *same way* as time complexity — count how much *extra*
memory the algorithm needs as a function of `n` — but people forget it exists because
time is what shows up as "my job is slow." Memory is what shows up as "my job got
OOM-killed," which is arguably the more common production failure mode in data
engineering.

Two things to distinguish:
- **Auxiliary space** — extra memory the algorithm allocates beyond the input itself
  (a hash map, a recursion stack, a second array)
- **Total space** — auxiliary space + the space the input already occupies

When people say "O(1) space" or "in-place," they mean auxiliary space — the input isn't
free, but the algorithm doesn't need more than a constant amount *beyond* it.

Each complexity folder has its own `space-complexity.md` covering the typical space cost
for that class's canonical algorithm(s). The root `capstone.md` then compares space cost
*across* all 7 classes, because the real decision in practice is rarely "what's fastest"
in isolation — it's "what's fastest, given how much memory I actually have."

---

## 5. Amortized Complexity — Why One Slow Operation Doesn't Ruin The Average

This is **not** the same idea as average-case (§2). Average-case is about *typical input
shape*. Amortized cost is about a *sequence of operations on the same structure* — some
individual operations in the sequence are expensive, but rarely enough that the average
cost *per operation, over the whole sequence* stays cheap.

**Canonical example: dynamic array append** (Python `list.append`, Java `ArrayList.add`).
Most appends just write into the next free slot — O(1). But when the backing array is
full, it has to grow: allocate a new array (commonly double the size) and copy every
existing element over. That one append costs O(n).

Walked through simply (the "aggregate method"): say the array doubles each time it's
full. Across `n` appends, the total copying work done by all the resizes is roughly
`n/2 + n/4 + n/8 + ... ≈ n`. So the total cost of `n` appends is `O(n)` for the appends
themselves plus `O(n)` for all the copying combined — `O(n)` total, which averages out to
**O(1) amortized per append**, even though any single append can cost O(n).

Second example: hash table resizing works the same way — inserts are amortized O(1) even
though an individual rehash is O(n).

**Counterexample — where amortization does *not* save you: string concatenation in a
loop.** Python strings are immutable, so `result = result + next_piece` doesn't append
in place — it allocates a brand-new string and copies the *entire* accumulated
`result` into it, every single time, no matter how small `next_piece` is. That's not an
occasional expensive operation on an otherwise-cheap sequence (the pattern that made the
dynamic array amortize down to O(1)) — it's an expensive operation *every single time*,
with the cost growing as the string grows. Summed over `n` concatenations, that's
`1 + 2 + 3 + ... + n ≈ n²/2`, so the total cost is `O(n²)`, and the amortized cost per
concatenation is `O(n)` — not O(1). The fix, `"".join(pieces)`, works precisely because
it knows the total size upfront and allocates once — one `O(n)` copy instead of `n`
growing copies. This pair (`+=` in a loop vs. `"".join()`) is worth holding next to the
dynamic-array example above: both involve "growing something in a loop," but only one of
them amortizes, because only one of them reuses its existing buffer instead of
copying everything on every step.

**Why this matters for DE:** a hot loop appending millions of rows "looks like" O(1) per
row by amortized reasoning, but if you repeatedly rebuild small structures from scratch
(e.g. a fresh list per micro-batch instead of one long-lived list), you pay the resize
cost far more often than amortized analysis assumes — you never get to amortize it over
a long enough sequence. `01-O1-constant/01-O1-constant-space-complexity.md` applies this specifically to
the dynamic array and hash table case.

---

## 6. Multi-Variable Complexity — When There's More Than One `n`

Textbook Big O examples almost always use one input of size `n`. Real data engineering
problems usually have at least **two**: joining two tables, matching a stream against a
lookup table, deduplicating across two sources.

Example — joining dataset `A` (size `n`) against dataset `B` (size `m`):

| Strategy | Time | Space | Notes |
|---|---|---|---|
| Nested-loop join | O(n·m) | O(1) | Compare every row of A against every row of B |
| Hash join | O(n + m) | O(min(n, m)) | Build a hash table on the smaller side, probe with the larger |
| Sort-merge join | O(n log n + m log m) | O(n + m) or less | Sort both sides, then merge |

`O(n·m)` and `O(n+m)` can look similar written down, but they behave completely
differently once one side is huge and the other is tiny — that gap is exactly why query
planners (Spark, Postgres) pick different join strategies based on table size. When a
DE technology example anywhere in this path involves a join, check which variable is
which before assuming "the input" is a single number.

---

## 7. Notation Cheat Sheet

| Symbol | Name | Meaning | Example |
|---|---|---|---|
| `O(g(n))` | Big O | Upper bound — "no worse than" | Binary search is `O(log n)` |
| `Ω(g(n))` | Big Omega | Lower bound — "no better than" | Any comparison sort is `Ω(n log n)` |
| `Θ(g(n))` | Big Theta | Tight bound — "exactly, up to constants" | Merge sort is `Θ(n log n)` |
| `o(g(n))` | Little o | Strictly slower-growing than (loose bound, rarely used casually) | `n` is `o(n²)` |
| Amortized `O(g(n))` | Amortized bound | Average per-operation cost over a sequence | Dynamic array append: amortized `O(1)` |

---

## 8. Why This Matters For Choosing A Data Processing Strategy

Picking the right strategy is never "find the lowest Big O and use that." It's:

- Time **and** space, together — a faster algorithm that doesn't fit in memory loses
- Average case **and** worst case — a strategy that's great on typical input but falls
  apart on one adversarial shape (skewed keys, already-sorted timestamps, a single huge
  partition) is a production incident waiting to happen
- Amortized reasoning — don't assume a "cheap" operation stays cheap if you keep
  resetting the sequence it's amortized over
- However many inputs are actually involved — most DE problems are joins, lookups, or
  merges across more than one dataset, not a single list

The next 7 folders each take one time-complexity class and go deep: the math, the
derivation, the space cost, where it shows up in real DE technology, the algorithms that
achieve it, and runnable benchmark code. `capstone.md` at the root then puts all 7 next
to each other and turns this into an actual decision framework.
