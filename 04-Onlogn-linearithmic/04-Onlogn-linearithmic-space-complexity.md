# O(n log n) — Space Complexity

## 1. Typical space cost

Merge sort's textbook implementation needs **O(n) auxiliary space**. The reason is the
merge step: to merge two adjacent sorted halves back into order, you need somewhere to
write the merged result *while you still have both halves to read from* — you can't
safely overwrite either half in place mid-merge without risking clobbering a value you
still need to compare. Standard practice is a temporary buffer the same size as the
input, so on top of the input itself you're paying for a full second array. There's also
an `O(log n)` recursion stack (one frame per level of the split, `log n` levels — same
count as `overview.md` §2's recursion tree), but that's dwarfed by the `O(n)` merge
buffer, so the total auxiliary space is written simply as `O(n)` (see `concept.md` §4 on
auxiliary vs. total space — the recursion stack and merge buffer are both "auxiliary,"
beyond the input array itself).

Contrast that with **heapsort**, which also achieves `O(n log n)` time but does it
**in-place** — `O(1)` auxiliary space. A heap is just an array reinterpreted with index
arithmetic (`parent = (i-1)//2`, `children = 2i+1, 2i+2`); building the heap and
repeatedly swapping the max to the end and re-sifting all happen inside the original
array, no second buffer required. Same complexity class, opposite ends of the space
axis — see the tradeoff section below.

## 2. Amortized behavior

Not applicable here in the sense `concept.md` §5 means it. Amortized cost describes a
*sequence of operations on the same persistent structure* (dynamic array append, hash
table insert) where occasional expensive operations average out over many cheap ones.
Merge sort isn't that shape — one call sorts `n` elements once, and its cost is
`Θ(n log n)` time / `O(n)` space for *that call*, full stop. There's no repeated
structure being amortized over. (The canonical amortized examples — dynamic array
doubling and hash table resizing — live in `01-O1-constant/01-O1-constant-space-complexity.md`, where
they actually apply.)

## 3. Local time/space tradeoff

Within this same complexity class, there's real room to trade memory for other
properties:

- **Heapsort** — drops auxiliary space from `O(n)` to `O(1)` at the cost of being
  unstable (equal elements can get reordered relative to each other) and having worse
  practical constants — heap operations jump around the array (poor cache locality)
  versus merge sort's sequential scans.
- **Bottom-up (iterative) merge sort** — instead of recursing, iterate merge-width `1, 2,
  4, 8, …` directly. This removes the `O(log n)` recursion stack entirely (relevant in
  languages with shallow default recursion limits — Python's is 1000 frames by default),
  but still needs the same `O(n)` merge buffer. It trades stack depth for a bit of loop
  bookkeeping, not memory for time.
- **External merge sort** — when `n` is too large to fit in RAM at all, sort fixed-size
  chunks that *do* fit, write each sorted chunk to disk, then merge the chunks in one or
  more passes using only small per-chunk read buffers in memory. This trades the `O(n)`
  in-memory requirement for `O(1)`-ish in-memory footprint plus disk I/O — exactly how
  Postgres and Spark handle sorts and sort-merge joins that exceed `work_mem` /
  executor memory (see `de-application.md`).

## 4. Worst-case space deviation

**None — and that's the entire point of this folder.** Merge sort's `O(n)` auxiliary
space and `Θ(n log n)` time both hold for *every* input shape: sorted, reverse-sorted,
all-duplicates, random. There is no adversarial arrangement of the data that makes either
number worse, because the algorithm's structure (split by index, merge linearly) never
looks at the data's values to decide how to recurse.

Compare that directly to quicksort, whose recursion-stack space is `O(log n)` *on
average* — but on adversarial pivot choices (e.g. already-sorted input against a naive
"always pick the first element" pivot), the partitions become maximally unbalanced and
recursion depth grows to `O(n)`. That's the same root cause as quicksort's `O(n²)`
worst-case time from `overview.md` §1 — one bad pivot shape produces both symptoms at
once, extra comparisons *and* a deeper stack. The full mechanics of that degradation
belong to `05-On2-quadratic/05-On2-quadratic-space-complexity.md`, not here. Merge sort's `O(n)` space is
the fixed, guaranteed price paid on every single run in exchange for never hitting that
failure mode — you know the cost up front, and it never gets worse.

## 5. Cross-link

See the root `capstone.md` for how merge sort's `O(n)`-space / guaranteed-`Θ(n log n)`
profile stacks up against the other 6 complexity classes — in particular the merge sort
vs. quicksort tradeoff pair (average-case-efficient-but-no-guarantee vs. worse average
but a hard ceiling) and the hash join vs. sort-merge join pair from `concept.md` §6.
