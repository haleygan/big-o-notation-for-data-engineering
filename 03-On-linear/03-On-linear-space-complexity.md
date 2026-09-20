# O(n) — Space Complexity

## 1. Typical Space Cost

Linear time does **not** automatically mean linear space — this is the class where that
distinction (`concept.md` §4: auxiliary vs. total space) actually matters in practice.
`01-O1-constant-space-complexity.md` §3a showed the O(1)-per-event side of this coin (the
generator pattern: process one event, yield it, forget it); this section is the other
side — what happens the moment a linear pass needs to *remember* something instead of
just passing through.

- **A pure streaming pass** — a Kafka consumer summing a numeric field, `grep` counting
  matching lines, a running average over a file — needs only a handful of accumulator
  variables. That's **O(1) auxiliary space**. The *total* space is still `O(n)`, because
  the input itself occupies `n` slots somewhere, but the algorithm doesn't add anything
  beyond that. This is the "in-place" flavor of linear time.
- **A scan that needs to remember what it's seen** — deduplicating a stream with a hash
  set, building the hash side of a hash join, collecting distinct values — needs an
  auxiliary structure that grows with the input. That's **O(n) auxiliary space** (or
  `O(min(n, m))` for a hash join, since you only need to hash the smaller side).

So the real question for any O(n)-time algorithm isn't "is it linear" — it's "does it
need to *remember* anything, or just *pass through*." A log-parsing job that transforms
each line and writes it straight to output needs O(1) extra memory. The same job doing
"count distinct user IDs" needs O(n) extra memory for the set of IDs seen so far.

## 2. Amortized Behavior

The hash-table-building side of this class is where `concept.md` §5's amortized argument
shows up directly. Building a hash join's lookup table (or a dedup set) means inserting
`n` keys one at a time into a hash map. Most inserts are O(1) — write into an open slot.
Occasionally the table's backing array fills up and has to resize (allocate bigger,
rehash every existing key into it) — that single insert costs O(current size).

Same aggregate argument as the dynamic array in `01-O1-constant/01-O1-constant-space-complexity.md`:
sum the resize costs across all `n` inserts and the total comes out to `O(n)`, which
means **O(1) amortized per insert**. So "build a hash table over n rows" is `O(n)` total
work, not `O(n²)`, even though a few of those individual inserts are visibly more
expensive than the rest.

## 3. Local Time/Space Tradeoff

Within this same class, there's a real tradeoff between how much you remember and what
that memory buys you:

- **O(1) space, single pass, no lookups**: stream through once, keep a running
  accumulator, never look back. Cheapest possible memory footprint, but you can only
  answer questions that don't require comparing elements to each other (sums, counts,
  min/max).
- **O(n) space, single pass, with lookups**: build a hash set or hash map alongside the
  scan. Costs you memory proportional to the input (or the distinct key space), but buys
  you O(1) membership checks and joins in the same pass — the alternative without that
  structure is either a second full pass or a nested loop that turns the whole thing into
  `O(n²)` (see `05-On2-quadratic`).
- **Hash join, smaller-side-only**: instead of hashing both `A` and `B`, hash whichever
  is smaller and probe with the larger. Space cost drops from "both tables" to
  `O(min(n, m))` — a deliberate, cheap optimization that doesn't change the time
  complexity at all, only the memory footprint. This is exactly what real query planners
  do: pick the build side based on which table (or partition) is smaller.

## 4. Worst-Case Space Deviation

The same adversarial shape that stresses time in this class also stresses space — data
skew.

- **Hash join under a hot key.** If one key value appears far more often than others
  (a single customer ID responsible for a huge fraction of rows, for instance), the hash
  bucket for that key holds a disproportionate share of the rows, and the number of
  output pairs for that one key group is (count of that key in A) × (count of that key
  in B) — which can balloon well past what "O(n+m) total rows in, O(n+m) total rows out"
  would suggest. The scan itself is still linear, but the *match explosion* for one
  partition behaves like the nested-loop case locally. This is the multi-variable
  equivalent of the "no early exit" note in `overview.md` §1 — skew doesn't slow down the
  building or probing steps, but it can blow up the output and the memory needed to hold
  it for that one key.
- **Hash collisions.** A pathological hash function (or an adversarially chosen key set)
  could force many keys into the same bucket, degrading average O(1) lookups toward O(n)
  each for that bucket. Python's dict/set implementation randomizes string hashing per
  process specifically to make this hard to trigger by accident or on purpose — but it's
  worth knowing the failure mode exists, since it's the space-side analogue of quicksort
  degrading on adversarial pivots.

## 5. Cross-Link

See root `capstone.md` for how this class's time/space profile (O(n) time, O(1)–O(n)
space depending on whether you need to remember anything) stacks up against the other 6
classes — including the hash-join-vs-sort-merge tradeoff explored there in full.
