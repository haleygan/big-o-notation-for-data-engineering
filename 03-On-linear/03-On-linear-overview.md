# O(n) — Linear Time

## 1. Mathematical Definition

Linear time means the cost grows in direct proportion to the input size. Double `n`,
double the work. If the operation count is `T(n) = c·n + k`, the napkin method from
`concept.md` §1 drops the constant `c` and the additive `k`, leaving `O(n)`.

There's no faster-growing or slower-growing hidden term lurking here — every element of
the input gets touched exactly once (or some fixed number of times), and that's the whole
story.

**Applying `concept.md` §2 (Big O vs Θ vs Ω) to the canonical algorithm.** Take a linear
scan — "does this list contain the value 7?" — as the example:

- **Best case: Ω(1).** The target is the very first element. You find it and stop. This
  is a real, valid bound, but it's the *lucky* case, not the typical one.
- **Average case: Θ(n).** On average, across random positions, you scan about half the
  list before finding a match (or scanning the whole thing when there's no match).
- **Worst case: Θ(n).** The target is the last element, or absent entirely — you touch
  every item.

When someone says "linear search is O(n)," they're really claiming **Θ(n)** for the
average and worst case — the Ω(1) best case is a different, better bound that only shows
up if you get lucky early. The input shape that pushes you off the best case: the target
value sitting at the end of the list, or not existing in it at all.

Now compare that to a **full scan that has no early-exit option at all** — summing every
value in a column, or a Kafka consumer that must process every message in a partition.
Here there is no lucky case. Best, average, and worst case all collapse to the same
**Θ(n)** — you cannot finish early no matter how the input is shaped, because the
definition of the task requires touching everything. This "no early exit" property is
the real fingerprint of this complexity class in data engineering: a full table scan, a
consumer draining a partition, a `.map()` over every row.

**Aside — two inputs, still linear.** Not every `n` in the world is a single list. Say
you're joining dataset `A` (size `n`) against dataset `B` (size `m`) with a **hash join**:
build a hash table over the smaller side, then probe it with every row of the larger
side. That's `O(n)` to build plus `O(m)` to probe — `O(n + m)` total. Two variables, but
still linear: neither variable is multiplied against the other, they're just added
(`concept.md` §6). That's a fundamentally different shape than the `O(n·m)` you get from
a nested-loop join, and the gap between "+" and "×" is exactly why query planners
(Spark, Postgres, DuckDB) reach for a hash join whenever they can. The full strategy
comparison table (nested-loop vs. hash join vs. sort-merge) lives in the root
`capstone.md` — here, just file away that "linear" doesn't require a single `n`.

## 2. Derivation Walkthrough

Start from the plainest possible loop:

```python
def process_all(records):
    total = 0
    for r in records:          # runs exactly n times
        total += transform(r)  # O(1) work per record
    return total
```

Step through it the way `concept.md` §3 prescribes:

1. **Basic operation**: one loop iteration — call `transform(r)`, add the result.
2. **Count**: the loop runs once per element, so exactly `n` iterations, each doing a
   constant amount of work.
3. **Simplify**: `T(n) = c·n` for some constant `c` (the cost of one iteration's work).
   Drop the constant → `O(n)`.

Now the two-input version, the hash join build-and-probe:

```python
def hash_join(table_a, table_b):
    lookup = {}
    for row in table_a:            # n iterations, O(1) amortized insert each
        lookup.setdefault(row["key"], []).append(row)
    matches = []
    for row in table_b:            # m iterations, O(1) average lookup each
        for hit in lookup.get(row["key"], ()):
            matches.append((hit, row))
    return matches
```

Building the hash table over `table_a` is `n` insertions, each `O(1)` amortized
(`concept.md` §5 — the dict resizes occasionally, but the aggregate cost across all `n`
inserts is `O(n)`). Probing with `table_b` is `m` lookups, each `O(1)` on average. Total:
`O(n) + O(m) = O(n + m)`. Still linear — just linear in the combined size of two inputs
instead of one.

## 3. Visual Graph

Growth curves for the three neighbors in this ladder — `O(log n)`, `O(n)` (this class),
and `O(n log n)` — at the same input sizes:

```
Operations
      n         O(log n)     O(n)      O(n log n)
     10            3.3        10          33
     20            4.3        20          86
     40            5.3        40         213
     80            6.3        80         506
    160            7.3       160        1172
    320            8.3       320        2663

  2700 |                                                     * n log n
  2400 |                                                *
  2100 |                                            *
  1800 |                                       *
  1500 |                                  *
  1200 |                             *
   900 |                        *
   600 |                   *                              + n
   300 |             *                        +---+---+---+
     0 |___+___+___+---+---+---+---+---+---+---+---+---+---
       o___o___o___o___o___o___o___o___o___o___o___o___o___  log n
         10   20   40   80  160  320     (n, input size)

  * = n log n     + = n (this class)     o = log n
```

`O(log n)` barely lifts off the axis even at `n = 320`. `O(n)` (this class) is the
straight diagonal line — the defining visual signature of linear time: a constant slope,
no curvature. `O(n log n)` tracks `O(n)` closely at small `n` but visibly bends upward
as `n` grows, because it's `n` copies of a slowly-growing `log n` factor stacked on top.

## 4. Layman Explanation

Say you've got a log file and you want to know how many lines contain the word `ERROR`.
There's no shortcut here — you have to open the file and look at every single line, one
at a time, because an error could be anywhere and the file isn't organized in any way
that lets you skip around. Read line 1, check it, read line 2, check it, ... all the way
to the last line.

Double the file size, and you double the number of lines you have to look at — the time
scales exactly in step with the input. That's linear time. It's the "no reader's trick
available" case: compare it to binary search on a *sorted* index of line offsets
(`02-Ologn-logarithmic`), where halving the search space each step gets you to the answer
in `log n` steps instead of `n`. A linear scan doesn't get that luxury — usually because
the data isn't sorted, isn't indexed, or the task (like "count every error") inherently
requires looking at everything rather than finding one thing.
