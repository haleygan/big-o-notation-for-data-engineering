# Capstone — Choosing a Processing Strategy Under Real Constraints

Everything before this file taught you to *recognize* a complexity class. This file is
about the harder skill: given a real problem with real constraints — how much data, how
much memory, how fast the answer needs to come back — which class should you actually
be aiming for, and what does hitting that target rule out?

There is no "always pick the lowest Big O" rule. The lowest time complexity that doesn't
fit in memory loses to a slower one that does. A guaranteed worst case beats a better
average case the moment "it broke in production at 2am" is more expensive than "it ran a
bit slower." This file is where the seven folders stop being separate case studies and
start being seven points on one shared map you can actually navigate.

---

## 1. Master Comparison Table

| Notation | Name | Typical time growth | Typical space growth | Canonical algorithm(s) | Representative DE technology |
|---|---|---|---|---|---|
| `O(1)` | Constant | Flat — doesn't grow with `n` | `O(1)` auxiliary (structure itself is `O(n)` total) | Array index access; hash table lookup | Redis `GET key` |
| `O(log n)` | Logarithmic | Adds ~1 step every time `n` *doubles* | `O(1)` iterative / `O(log n)` recursive | Binary search; B-tree / index descent | Postgres B-tree index lookup |
| `O(n)` | Linear | Directly proportional to `n` | `O(1)` if streaming-through, `O(n)` if remembering (hash set/join build) | Linear scan; hash join build+probe | Kafka consumer draining a partition |
| `O(n log n)` | Linearithmic | `n` copies of a slowly-growing `log n` factor | `O(n)` (merge sort) or `O(1)` (heapsort) | Merge sort; sort-merge join | Spark `SortMergeJoinExec` |
| `O(n²)` | Quadratic | Doubling `n` quadruples the work | `O(1)` in-place (quicksort) or `O(n²)` if pairs are materialized | Nested-loop join; naive all-pairs dedup | Postgres nested-loop join (no usable index) |
| `O(2ⁿ)` | Exponential | Every `+1` to `n` *multiplies* total cost | `O(n)` (naive recursion, one path on the stack) or `O(n·2ⁿ)` if every result is materialized | Naive recursive Fibonacci; power set / grouping sets | SQL `GROUP BY CUBE(...)` |
| `O(n!)` | Factorial | Multiplier grows with `n` itself, not fixed | `O(n)` streaming permutations, `O(n·n!)` if materialized | Brute-force permutation search / TSP | Postgres exhaustive join-order search (below `join_collapse_limit`) |

A few things worth noticing before you move on, because they're the whole reason this
table exists instead of seven separate ones:

- **Time and space are separate columns for a reason.** Several rows have *two* space
  answers, because the same time complexity hides genuinely different memory profiles
  depending on implementation choice (in-place vs. materializing, streaming vs.
  collecting). "This algorithm is O(n²) time" tells you almost nothing about its memory
  footprint until you ask the follow-up question.
- **The canonical algorithm column is doing double duty.** For `O(n²)` and `O(2ⁿ)`
  especially, the "canonical algorithm" is also the cautionary tale — nested-loop joins
  and naive recursion are things query planners and engineers actively try to avoid
  landing on, not things anyone picks on purpose at scale.
- **The DE technology column is one example each, not the only example.** Every folder's
  `de-application.md` has a full table; this row just anchors each class to one thing you
  can picture immediately.

---

## 2. Combined Growth Chart

Here's the problem with plotting all seven curves on one normal chart: at `n = 20`,
`O(1)` is still `1` and `O(n!)` is `2,432,902,008,176,640,000`. Any chart with a linear
y-axis that fits both of those numbers makes the first six classes look like a flat line
sitting on the x-axis. So the honest way to show this is a log-scale view, the same trick
`01-O1-constant/01-O1-constant-overview.md` used for its own three-curve chart, just extended to all
seven.

Raw operation counts, same `n` values across all seven classes:

| n | O(1) | O(log n) | O(n) | O(n log n) | O(n²) | O(2ⁿ) | O(n!) |
|---|---|---|---|---|---|---|---|
| 1 | 1 | ~0 | 1 | ~0 | 1 | 2 | 1 |
| 2 | 1 | 1 | 2 | 2 | 4 | 4 | 2 |
| 4 | 1 | 2 | 4 | 8 | 16 | 16 | 24 |
| 8 | 1 | 3 | 8 | 24 | 64 | 256 | 40,320 |
| 16 | 1 | 4 | 16 | 64 | 256 | 65,536 | ~2.09 × 10¹³ |
| 20 | 1 | ~4.3 | 20 | 86 | 400 | 1,048,576 | ~2.43 × 10¹⁸ |

And the same data as a log10-scale plot — each row is one class, the bar length is
`log10(operation count)` at `n = 20`, so every `#` is one order of magnitude:

```
Operation count at n = 20, log10 scale (each # ≈ 1 order of magnitude)

O(1)         (1)                #
O(log n)     (~4)               #
O(n)         (20)               ##
O(n log n)   (86)               ##
O(n²)        (400)              ###
O(2ⁿ)        (1,048,576)        ######
O(n!)        (2.4 × 10¹⁸)       ###################

             0    2    4    6    8    10   12   14   16   18   (log10 scale)
```

Read this chart the way it's meant to be read: the *gaps* between bars are the point, not
the bars themselves. `O(1)` through `O(n log n)` are visually indistinguishable at small
`n` — they all sit in "single or double digit" territory even at `n = 20`. `O(n²)` starts
to separate. `O(2ⁿ)` and `O(n!)` aren't just "bigger" — they're categorically different,
which is exactly why `06-O2n-exponential` and `07-Onfactorial-factorial` both frame
themselves as "the point where more compute stops being a viable answer," not "the slow
classes."

The one thing every folder's own growth chart already showed you, worth restating once
here for all seven at once: **the ordering never changes.** `O(1) < O(log n) < O(n) <
O(n log n) < O(n²) < O(2ⁿ) < O(n!)` holds for every `n` past a small crossover point, and
in practice for essentially every `n` a data engineer will ever touch.

---

## 3. Time/Space Tradeoff, Cross-Class

This is the section the whole path has been building toward. Every pairing below is the
*same problem*, solved twice, landing at two different points on the time/space curve —
and a real system picking between them based on a real constraint, not a benchmark.

### Hash join vs. sort-merge join

Joining dataset `A` (size `n`) against `B` (size `m`) has two workhorse strategies, and
they sit on opposite sides of the memory question:

- **Hash join** — `O(n + m)` time, `O(min(n, m))` extra space. Build a hash table over
  whichever side is smaller, probe it with the larger side. This is `03-On-linear`'s
  canonical two-input example: fast, but that hash table has to live somewhere, all at
  once, for the whole probe phase.
- **Sort-merge join** — `O(n log n + m log m)` time, and the *merge* step itself needs
  only `O(1)` extra space (two cursors walking two sorted streams in lockstep). The
  catch is getting both sides sorted in the first place: if they aren't already sorted
  (or arriving off an index in sorted order), that costs `O(n)` auxiliary space for an
  in-memory merge sort (`04-Onlogn-linearithmic/04-Onlogn-linearithmic-space-complexity.md`) — or, when the
  data doesn't fit in memory at all, an **external merge sort** that spills sorted runs
  to disk and merges them with only small per-chunk buffers in RAM.

Here's the actual decision a query planner (Spark, Postgres, DuckDB) is making: hash
join is faster *if the smaller side comfortably fits in the memory budget you've given
the query*. The moment the smaller side doesn't fit, a hash join doesn't get "a bit
slower" — it spills to disk in an ugly, unpredictable way, or fails outright. Sort-merge
join's external-sort variant was built for exactly that failure mode: it trades a
guaranteed-to-fit hash table for a strategy that degrades gracefully by writing to disk
instead of falling over. That's why Spark's planner picks broadcast/hash join for a
small dimension table joined against a huge fact table, and falls back to sort-merge the
moment neither side is small enough to build a hash table over in executor memory. Same
logic, same tradeoff, in Postgres's `work_mem` setting and its own hash-vs-merge join
planner choice.

### Exact distinct count vs. approximate sketch (HyperLogLog)

"How many distinct user IDs hit this endpoint today?" has an exact answer and a
close-enough answer, and they live at wildly different points on the space axis:

- **Exact count** — keep a hash set of every distinct value you've seen. `O(n)` space
  in the worst case (every value distinct), because you cannot know a value is a repeat
  without remembering every value you've already seen. This is the same "remembering
  costs space" idea from `03-On-linear/03-On-linear-space-complexity.md`'s dedup discussion, just
  applied to counting instead of filtering.
- **HyperLogLog (and sketches like it)** — a small, *fixed-size* set of registers
  (commonly a few KB, regardless of whether you've seen a thousand values or a billion)
  that hashes each incoming value and tracks statistical patterns in the hash bits (the
  longest run of leading zeros seen, per register) to *estimate* cardinality. Space is
  `O(1)` relative to the number of distinct values — it does not grow as the true
  cardinality grows, only the accuracy bound tightens or loosens based on how many
  registers you configured up front. Typical error is around 1-2% for a modest register
  count.

Why streaming systems (Redis `PFCOUNT`, Presto/Trino `approx_distinct`, BigQuery
`APPROX_COUNT_DISTINCT`, Spark's `approx_count_distinct`) default to the sketch at scale:
an exact distinct count over a high-cardinality stream — think unique visitor counts
across a large ad platform — would need a hash set that grows without bound as long as
the stream runs, and merging exact counts across distributed shards means shipping and
unioning giant sets across the network. A HyperLogLog sketch merges in constant time and
constant space regardless of how much data fed into either side, and 1-2% error is a
completely acceptable price for a dashboard metric that nobody is going to bill an
invoice against. The exact count still wins whenever the number *has* to be exact — a
regulatory report, a billing reconciliation — because there the accuracy loss isn't a
rounding error, it's a wrong answer. The decision is entirely about what the number is
*for*, not which one is technically superior.

### Exact deduplication (set) vs. approximate deduplication (Bloom filter)

The streaming-systems sibling of the HyperLogLog pairing above — same shape, different
question. HyperLogLog answers "how many distinct values?"; a Bloom filter answers "have I
seen this exact value before?" — the O(1) membership check `01-O1-constant-de-application.md`
§2 uses for streaming dedup, but with the underlying structure swapped out once the
`seen_ids` set gets too large to hold in memory.

- **Exact dedup with a `set`** — `O(n)` space, one entry per distinct value ever seen.
  Zero false positives or negatives: if `event_id in seen_ids` says yes, it's certainly
  yes. This is `01-O1-constant-de-application.md`'s dedup pattern exactly as written —
  and it's the right choice as long as the full set of distinct IDs comfortably fits in
  memory for the lifetime of the job.
- **Approximate dedup with a Bloom filter** — a fixed-size bit array plus a handful of
  hash functions, checked and set on every insert. Space is `O(1)` relative to the
  number of distinct values seen — a Bloom filter sized for a billion entries doesn't
  grow past its configured bit-array size no matter how many more events arrive, unlike
  a `set` which keeps growing by construction. The tradeoff: false positives are
  possible (it can wrongly say "seen before" for something new), tunable down to a
  small, known rate by sizing the bit array and hash-function count appropriately — but
  false *negatives* are not possible (it never wrongly says "new" for something already
  seen).

Why Kafka, Cassandra, and similar systems reach for a Bloom filter at scale: an exact
`set`-based dedup over a high-cardinality, long-running or unbounded stream grows without
bound for as long as the job runs, eventually exhausting memory — the same failure mode
HyperLogLog avoids for counting. A Bloom filter trades "always exactly right" for "fixed
memory footprint, occasionally lets through a false positive" — for deduplication that
means occasionally treating a genuinely-new event as a duplicate and dropping it, which is
an acceptable cost in systems (log aggregation, cache-miss avoidance, spam filtering) where
occasionally over-suppressing is far cheaper than an unbounded memory leak. Where a missed
event is unacceptable — a payments pipeline, an exactly-once processing guarantee — the
exact `set` (or a distributed store backing it) is worth the memory cost, same reasoning
as the exact-count-vs-HyperLogLog choice above: the decision is about what a false answer
costs, not which structure is technically more sophisticated.

### In-place sort: quicksort's average-case space vs. merge sort's guaranteed space

This is the pairing the whole path has been circling since `concept.md` §2 first
introduced Θ vs. worst case, and it's worth stating as plainly as possible:

**Quicksort's recursion-stack space is `O(log n)` in the average case — but that number
is not a guarantee.** `05-On2-quadratic/05-On2-quadratic-space-complexity.md` walks through exactly why:
on the same adversarial input that produces quicksort's `O(n²)` worst-case *time*
(already-sorted or reverse-sorted data, combined with a naive first-or-last-element pivot
rule), the partitioning degenerates into peeling off one element per recursive call
instead of splitting the array in half. That means recursion depth grows from `O(log n)`
frames to `O(n)` frames — and as that file states directly, *"this is the same root
cause showing up as two symptoms, not two separate problems."* Bad pivoting is the one
mistake; degraded time and degraded stack space are both direct, simultaneous
consequences of it.

**Merge sort pays `O(n)` auxiliary space on every single run, no exceptions** —
`04-Onlogn-linearithmic/04-Onlogn-linearithmic-space-complexity.md` is explicit that this holds "for *every*
input shape: sorted, reverse-sorted, all-duplicates, random," because the algorithm's
split-by-index-then-merge structure never looks at the data's values to decide how to
recurse. There is no adversarial input that makes merge sort's space number worse,
because there's no data-dependent branch for an adversary to exploit.

Frame the choice exactly as the schema for this file names it: quicksort is
**average-case-efficient but carries no guarantee** — cheap in the typical case, with a
tail risk that shows up precisely on inputs (already-sorted timestamps, pre-sorted
re-runs) that are common in data pipelines, not rare. Merge sort is **worse on average,
but has a hard ceiling** — you know the `O(n)` space bill up front, on every run, and it
never gets worse no matter what shape the data takes. A production sort job with a fixed
memory budget and no tolerance for a 2am stack-depth surprise should default to a sort
with a guaranteed bound (merge sort, or a randomized/median-of-three quicksort variant
that removes the adversarial pivot case entirely — see `05-On2-quadratic/05-On2-quadratic-de-application.md`
§4). A one-off interactive sort where average-case speed matters more than a rare tail
risk can reasonably stick with quicksort.

### Memoization / caching: spending space to drop a whole time class

`06-O2n-exponential/06-O2n-exponential-space-complexity.md`'s naive-vs-memoized Fibonacci comparison is the
cleanest possible demonstration that time and space aren't just "traded" against each
other in the sense of shaving off a constant factor — sometimes the trade buys you an
entire complexity class:

| Approach | Time | Space | What's different |
|---|---|---|---|
| Naive recursive Fibonacci | `O(2ⁿ)` (tight bound `Θ(φⁿ)`) | `O(n)` | Every sub-problem is re-solved from scratch, every time it's requested — no memory of past work |
| Memoized (cache each result) | `O(n)` | `O(n)` | Each of the `n` distinct sub-problems is solved exactly once and reused |

The naive version isn't slow because `n` is large — it's slow because it **redundantly
recomputes the same answers** over and over (that file's trace shows `fib(1)` computed
five separate times just to get `fib(5)`). Memoization is the direct fix: the first time
you solve a sub-problem, write the answer down; every later request for that same
sub-problem becomes an `O(1)` lookup instead of a fresh recursive descent. You deliberately
spend `O(n)` space you weren't spending before, and in exchange the total time collapses
from exponential to linear.

This is one of the highest-leverage moves available to a data engineer, and it shows up
constantly outside of textbook Fibonacci: caching a feature-store lookup instead of
recomputing a derived feature per request, memoizing a config-resolution function that
gets called once per row of a batch when the config itself only changes a handful of
times, caching the result of an expensive join or aggregation that gets rebuilt from
scratch inside a hot loop. The question worth asking whenever a recursive or repeated
computation feels too slow isn't "how do I make this loop cleverer" — it's "am I solving
the same sub-problem more than once, and can I afford to remember the answer?"

### Bonus pair: Held-Karp — spending `O(n·2ⁿ)` space to buy back `O(n!)` time

`07-Onfactorial-factorial/07-Onfactorial-factorial-space-complexity.md` covers a more extreme version of the same
memoization idea, worth calling out because the scale of the trade is so dramatic. Exact
TSP by brute force means generating and scoring every permutation of `n` cities:
`O(n!)` time, and — if you're careful to stream permutations instead of materializing
them — only `O(n)` space.

The Held-Karp algorithm re-frames the problem's *state* as `(set of cities visited,
current city)` instead of "which full permutation am I building," and memoizes the best
cost for each state. There are `2ⁿ` possible subsets and `n` possible current cities, so
the memo table holds `O(n·2ⁿ)` entries, and filling it takes `O(n²·2ⁿ)` time. At `n = 20`:
brute force is `20! ≈ 2.4 × 10¹⁸` operations; Held-Karp is `20² · 2²⁰ ≈ 4.2 × 10⁸` —
roughly ten billion times fewer operations, paid for by spending `O(n·2ⁿ)` space on the
memo table instead of `O(n)` on a bare recursion stack. It's still exponential, and it
still eventually explodes — but it moves TSP from "infeasible past `n = 13`" to "usable up
to roughly `n = 20-25`" on ordinary hardware. Same lesson as Fibonacci, just at a scale
where the payoff is measured in billions instead of "noticeably faster."

---

## 4. Decision Framework

There's no formula that spits out "use O(n log n)" from a set of constraints — but there
is a reliable order of questions to ask, and each answer rules a few strategies in or
out. Work through these roughly in order:

**1. Does the whole dataset fit in memory, on one machine, at once?**
- Yes → time-optimal in-memory strategies (hash joins, in-memory sorts, hash-set
  dedup) are all on the table. Optimize mostly for time.
- No → you need either a strategy with bounded auxiliary space regardless of `n`
  (streaming/O(1)-space passes, external merge sort, sketches like HyperLogLog), or
  a distributed system that partitions the problem so no single node needs the whole
  thing in memory. Ruling out: naive hash joins over the full dataset, any algorithm
  that materializes an `O(n²)` or `O(n·2ⁿ)` result set in one place.

**2. What's the actual memory budget, in concrete terms (executor memory, `work_mem`,
container limit) — not "however much the box has"?**
- Tight budget, large `n` → prefer `O(1)`-or-`O(log n)`-auxiliary-space strategies:
  streaming aggregation, sketches, sort-merge over hash join, external sort over
  in-memory sort. Ruling out: building full hash tables or similarity matrices over
  the large side.
- Generous budget → you can afford `O(n)` or even `O(n²)` auxiliary structures if they
  buy meaningfully better time — a hash join, a memoized recursion, a materialized
  distance matrix for a bounded, genuinely small `n`.

**3. Is there a latency SLA on a single request, or is this a batch job with a wall-clock
deadline measured in hours?**
- Tight per-request latency (an API, a real-time feature lookup) → you need `O(1)` or
  `O(log n)` *time* on the hot path, full stop — anything higher must be precomputed
  ahead of time and cached (see §3's memoization pairing) so the request-time cost is
  cheap. Ruling out: any per-request `O(n)` scan or worse, unless `n` is provably tiny
  and bounded.
- Batch job with a wide time window → `O(n log n)` and even `O(n²)` can be perfectly
  fine if `n` is small enough or the window is generous enough — don't over-optimize
  time at the cost of code complexity or memory risk if the job already finishes with
  room to spare (see the pitfalls in §5).

**4. Batch or streaming?**
- Streaming (unbounded, continuously arriving data) → you cannot hold "everything seen
  so far" without an ever-growing memory footprint, so bounded-space approximations
  (sketches, reservoir sampling, bounded windows) become the default rather than the
  exception. Exact algorithms that assume a finite, fully-available input (most sorts,
  most joins as classically taught) need reframing into windowed or incremental
  versions.
- Batch (bounded, known-size input) → exact algorithms are back on the table, and the
  earlier questions (memory budget, latency SLA) drive the choice more than the
  batch/streaming distinction itself.

**5. Single-node or distributed?**
- Single-node → the complexity classes in this path map directly onto real cost; the
  main risk is simply exceeding the box's memory.
- Distributed (Spark, a sharded database, a multi-partition Kafka topic) → multiply the
  question by "does this strategy require global state, or can it be computed
  per-partition and combined cheaply?" A hash join needs the build side shipped to
  every node (or one side small enough to broadcast); an exact distinct count needs
  every shard's hash set merged, which is expensive; a HyperLogLog sketch merges across
  shards in `O(1)` per shard, which is exactly why distributed systems lean on
  approximate sketches even harder than single-node ones do.

**6. What does "wrong sometimes" cost, versus what does "slow" cost?**
This is the question underneath the exact-vs-approximate pairing in §3, and it deserves
to be asked explicitly rather than defaulted. If a wrong answer is a compliance problem,
approximate strategies are off the table regardless of how much memory they'd save. If
a wrong answer is a dashboard being off by 1%, the memory and latency savings from an
approximate strategy are almost always worth it.

---

## 5. Common Strategy-Picking Pitfalls

**Optimizing time while ignoring the memory budget that will OOM in production.** The
single most common version of this: reaching for a hash join, a full in-memory sort, or
an eagerly-materialized dedup set because it's faster on a laptop with a small sample,
then watching it OOM-kill an executor once the real data volume shows up. `concept.md`
§4 called this out directly — memory running out is arguably the more common production
failure mode in data engineering than a job simply being slow, and it's the one that gets
discovered at 2am instead of during development, because dev data is almost always
smaller than prod data.

**Over-engineering a low-complexity solution for an `n` that will never be large enough
to matter.** The flip side of the above: building a HyperLogLog pipeline, a custom
external merge sort, or a hand-rolled B-tree index for a lookup table with 500 rows.
`O(n²)` on `n = 500` is 250,000 operations — a rounding error on modern hardware, done in
microseconds. The engineering cost (more moving parts, more code to maintain, an
approximate answer where an exact one was free) isn't paid back by anything, because the
input was never going to be big enough for the complexity class to matter. Know your
actual `n`, and its realistic growth, before reaching for a fancier algorithm than the
data requires.

**Trusting a "typical" complexity without checking what breaks it.** `concept.md` §2 and
every folder after it repeats the same warning for a reason: quicksort's Θ(n log n) is an
*average*, not a guarantee, and the specific input shape that breaks it — already-sorted
data — is exactly what timestamp columns and re-runs of previously-sorted data look like
in production. The pitfall isn't picking quicksort; it's picking it (or any
average-case-optimized strategy) without checking whether your actual data can look like
the adversarial shape that breaks it, and without a fallback (randomized pivots,
median-of-three, or just defaulting to a guaranteed-bound algorithm) when it can.

**Re-deriving amortized cost from a sequence that's too short to amortize over.**
`concept.md` §5 and `01-O1-constant/01-O1-constant-space-complexity.md` both flag this: a hot loop that
"looks" O(1) per operation only stays that way if it runs over a long-lived structure.
Rebuilding a fresh list or hash map from scratch per micro-batch — instead of reusing one
structure across batches — means every micro-batch pays its own resize costs from empty,
never getting a long enough sequence to amortize against. The pitfall is treating
amortized-O(1) as if it were a property of the *operation* rather than a property of the
*sequence* it runs in.

**Choosing exactness by default instead of by requirement.** Reaching for an exact
distinct count, an exact join, or a fully materialized result set out of habit, without
asking what the number is actually *for*. If nobody downstream needs the fourth
significant digit, a sketch that's 100x cheaper on memory and merges instantly across
shards is the better engineering choice — and conversely, defaulting to an approximate
sketch for a number that's about to appear on an invoice is the same mistake in the other
direction. The right default is "ask what wrong costs," not "always exact" or "always
approximate."

**Ignoring the multi-variable case and assuming "the input" is a single `n`.**
`concept.md` §6 flagged this early, and it's worth restating here at the end: most real
data engineering problems are joins, lookups, or merges across *at least two* datasets,
not one list. `O(n·m)` and `O(n+m)` can look similar on paper and behave completely
differently once one side is a 10-row config table and the other is a 10-billion-row
fact table. Before applying any of the strategies or tradeoffs in this file, check how
many `n`s are actually in play — the whole hash-join-vs-nested-loop story in §3 only
makes sense once you've done that.

---

That's the full arc: `concept.md` gave you the vocabulary, the seven folders gave you the
depth on each class, and this file is the map connecting them into an actual decision —
time versus space, average case versus guaranteed worst case, exact versus approximate,
all judged against the constraints of the system actually running the job, not against
which number looks smallest on a whiteboard.
