# O(1) — Space Complexity

## 1. Typical Space Cost

Applying concept.md §4's auxiliary-vs-total split to this class's two canonical
structures:

**Array indexing (`arr[i]`).** Auxiliary space: `O(1)` — the operation needs a
handful of registers to hold the computed address, nothing that scales with `n`.
It doesn't touch or copy the array; it just computes where in *existing* memory
to look.

**Hash table lookup (`d[key]`).** Same story: `O(1)` auxiliary — hashing the key
and following one bucket pointer doesn't allocate anything proportional to `n`.

The nuance worth sitting with: the *operation* is O(1) auxiliary space, but the
*structure* backing it (the array holding `n` elements, the hash table holding `n`
entries) is `O(n)` **total** space — because the input itself occupies `O(n)`.
"O(1) space" always describes the *extra* memory an operation needs on top of a
structure that already exists; it never means the structure is free. A lookup on a
500 GB hash table is still O(1) auxiliary space, and still needs a machine that can
hold 500 GB.

## 2. Amortized Behavior

This is where concept.md §5's general explanation gets applied concretely — dynamic
arrays and hash tables are its canonical examples, and this is the folder that
walks through *why*.

**Dynamic array append (Python `list.append`).** A Python list isn't a raw fixed
array — it's a dynamic array: a backing buffer with some spare capacity, plus a
length. Most `.append()` calls just write into the next free slot: `O(1)`, no
allocation. But when the buffer is full, Python has to:
1. Allocate a new, bigger backing buffer (CPython grows by roughly 1.125x, other
   implementations commonly double — the growth factor changes the constant, not
   the shape of the argument below)
2. Copy every existing element into the new buffer — `O(n)` work, for that *one*
   append

Walking the aggregate method from concept.md §5 with concrete numbers, using
doubling for clean arithmetic: say the array has doubled its way up to hold `n`
elements. The resizes happened when the array crossed size `n/2`, `n/4`, `n/8`, ...
down to 1. Total elements copied across *all* those resizes:

```
n/2 + n/4 + n/8 + ... + 1  ≈  n     (geometric series, sums to just under n)
```

So across `n` total appends: the appends themselves cost `O(n)` (1 unit each), and
all the resize-copying combined costs another `O(n)`. Total: `O(n)` for `n`
appends → **O(1) amortized per append**. Any *single* append can cost O(n) (the one
that triggers the resize), but you never pay that cost often enough for it to show
up in the per-operation average.

**Hash table resize.** Same mechanism, different trigger. A hash table tracks its
*load factor* (`entries / bucket_count`). Once it crosses a threshold (commonly
~0.7), it resizes: allocate a bigger bucket array (commonly double), and re-hash and
reinsert every existing entry into the new layout — `O(n)` for that one insert.
Exactly like the dynamic array: spaced out geometrically across a sequence of `n`
inserts, the total rehashing cost is `O(n)`, so inserts are **O(1) amortized**.

**Why this matters for DE (concept.md §5's warning, applied):** if you rebuild a
fresh small list or dict from scratch per micro-batch — instead of reusing one
long-lived structure across batches — you never accumulate a long enough sequence
of operations to amortize the resize cost over. Every micro-batch pays its own
resize costs from empty, repeatedly. A hot loop that looks "O(1) per row" in
isolation can turn into "O(n) resize, every single batch" in aggregate if the
structure's lifetime is too short to amortize against.

## 3. Local Time/Space Tradeoff

Within this class, there's a real memory-vs-reliability tradeoff, not a
memory-vs-speed one (both variants are O(1) time on average) — the axis that
actually moves is *how much memory you spend to keep the worst case from happening*:

- **Lower load factor (more memory, more consistent O(1)):** resizing a hash table
  earlier — say at 50% full instead of 90% — spends more memory on empty buckets,
  but keeps chains short and collisions rare, so the *constant factor* behind "O(1)
  average" stays small and stable.
- **Higher load factor (less memory, more collision risk):** packing the table
  fuller saves memory but lets chains grow longer, pushing the average lookup closer
  to its O(n) worst case in practice, even though the asymptotic label doesn't
  change.
- **Direct addressing (a plain array indexed by the key itself, when keys are small
  bounded integers):** spends memory proportional to the *key space*, not the number
  of entries actually present, in exchange for a guaranteed Θ(1) worst case with no
  collision risk at all — the array-indexing guarantee from `overview.md` §1,
  applied as a design choice instead of a given.

A second, classic version of this same tradeoff: precomputing a lookup table
(spend `O(n)` space upfront to store every answer) so that later reads are O(1) with
zero computation, instead of recomputing an answer on every access. This is the
"pay memory once, get O(1) forever after" pattern — the same shape as memoization,
which `capstone.md` covers across all 7 classes.

## 3a. Generator Pattern — O(1) Auxiliary Space in Streaming

There's a second axis to "O(1) space" worth separating out from everything above: not
"how much does *one lookup* cost," but "how much does processing *one event* in a
stream cost, if I do it a million times in a row." A Python generator (`yield`) is the
standard way to keep that number at O(1) per event instead of letting it silently
become O(n) for the whole run.

```python
# O(n) auxiliary -- builds the entire result list before returning anything
def enrich(events, lookup):
    results = []
    for event in events:
        results.append({**event, "category": lookup[event["product_id"]]})
    return results

# O(1) auxiliary per event -- yields one result at a time, nothing accumulates
def enrich(events, lookup):
    for event in events:
        yield {**event, "category": lookup[event["product_id"]]}
```

Both versions do the same O(1) dict lookup per event — that part doesn't change. What
changes is what happens to the *results*. The list version holds every enriched event in
memory simultaneously, so peak auxiliary space grows with however many events you've
processed so far: O(n) for the whole run, even though each individual step is cheap. The
generator version hands each result to whatever consumes it (a `for` loop, a writer, the
next stage of a pipeline) and then forgets it — nothing about the stream's history
accumulates, so auxiliary space stays O(1) regardless of whether you're a thousand events
in or a billion.

This is the pattern behind every streaming framework's per-record processing model
(Kafka Streams, Flink, a `csv.reader` iterating a file) — none of them read the entire
input into memory first, because "O(1) per event" only stays true in aggregate if nothing
upstream is quietly collecting every event into a growing structure.
`03-On-linear-space-complexity.md` covers the mirror image of this: the moment a
streaming pass needs to *remember* something (dedup, join, distinct count), auxiliary
space necessarily becomes O(n) — the generator pattern here is specifically for the case
where each event can be processed and released without needing to compare it against
anything that came before.

## 4. Worst-Case Space Deviation

The same adversarial input that breaks *time* (overview.md §1's hash-collision
case) doesn't blow up total memory the way, say, a bad quicksort pivot blows up
recursion-stack space — the table still holds `n` entries either way, so total
space stays `O(n)`. What breaks is the **distribution**: instead of `n` entries
spread evenly across `k` buckets (~`n/k` each), an adversarial or poorly-chosen key
set dumps most or all of `n` entries into a single bucket's chain. That one chain is
now effectively an `O(n)`-length linked list living inside what was supposed to be a
`O(1)`-deep structure. No extra memory got allocated — but the operation that
walks that chain now touches `O(n)` entries instead of `O(1)`, which is the same
root cause as the time-complexity worst case, just visible as *shape* (one long
chain) rather than *size* (more total bytes).

## 5. Cross-Link

See root `capstone.md` for how this class's time/space profile stacks up against
the other 6 — in particular, how "O(1) time, O(n) total space for the structure"
compares to classes that spend more time to avoid holding the whole structure in
memory at all.
