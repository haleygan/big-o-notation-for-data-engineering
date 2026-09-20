# O(n²) — Quadratic Time

## 2. Mathematical Definition

O(n²) means the work grows with the *square* of the input size. Formally (concept.md §1):
there exist constants `c` and `n₀` such that the operation count `T(n) ≤ c·n²` for all
`n ≥ n₀`. The practical consequence: double `n` and the work doesn't double — it
quadruples. Ten times the input means *one hundred times* the work. This is the point
where "just let it run" stops being a viable strategy for large `n`.

**The canonical example, and why it's the perfect case study for concept.md §2's
Big O vs Θ vs Ω distinction: quicksort.**

Say it out loud and most people say "quicksort is O(n log n)." What they actually mean
is Θ(n log n) — the *typical* case. That single sentence is quietly collapsing three
different claims into one:

| Case | Bound | Value | Why |
|---|---|---|---|
| Best case | Ω(n log n) | `Θ(n log n)` | Every pivot splits the array into two roughly equal halves — recursion tree depth `log n`, each level does `O(n)` partition work |
| Average case | Θ(n log n) | `Θ(n log n)` | Random/typical input produces "good enough" splits often enough that the expected cost matches the best case, up to constants |
| Worst case | O(n²) | `Θ(n²)` | A specific input shape forces every partition to split maximally unevenly |

So quicksort's true, complete description is: **Ω(n log n), O(n²), and Θ(n log n) only
in the average case.** It never beats `n log n` (that's the Ω floor — even the best case
can't do better, since any comparison-based partition of `n` elements costs at least
`O(n)` per level and you need at least `log n` levels to get down to size 1). But it can
be dragged all the way up to `n²` if the input is shaped wrong.

**The exact input shape that triggers the worst case:** a naive pivot rule — "always pick
the first element" or "always pick the last element" — combined with data that is already
sorted (or reverse-sorted, or has huge runs of duplicate keys). If the pivot is always the
last element and the array is already sorted ascending, then the pivot is always the
*maximum* of whatever subarray you're currently partitioning. Every single element other
than the pivot is smaller than it, so the partition step puts `n-1` elements on one side
and `0` elements on the other. Instead of splitting the problem in half each time
(recursion depth `log n`), you peel off exactly one element per recursive call
(recursion depth `n`). That's the whole story: a partitioning algorithm designed to
divide-and-conquer degenerates into a linear peel, and a linear peel of linear-cost steps
is `n · n = n²`.

This matters in practice because "already sorted" isn't an exotic adversarial input in
data engineering — it's timestamp columns, auto-incrementing IDs, and re-sorting data
that's already 99% sorted from a previous stage. A naive quicksort implementation meets
this input constantly, not rarely.

## 3. Derivation Walkthrough

Apply concept.md §3's method — identify the basic operation, count it as a function of
`n`, simplify to the dominant term — directly to the worst-case partition sequence above.

**Basic operation:** one element-vs-pivot comparison during the partition step (the loop
that decides which side of the pivot each element belongs on).

**Setup:** array of `n` elements, already sorted ascending, pivot rule = "last element."

```python
def partition(items, lo, hi):
    pivot = items[hi]          # last element — the naive rule
    i = lo - 1
    for j in range(lo, hi):    # one comparison per element in this subarray
        if items[j] <= pivot:
            i += 1
            items[i], items[j] = items[j], items[i]
    items[i + 1], items[hi] = items[hi], items[i + 1]
    return i + 1                # pivot's final index
```

**Counting the comparisons across the whole sort**, on sorted input:

1. First call: subarray has `n` elements. Pivot = max of the subarray, so the loop runs
   `n - 1` comparisons, and the partition splits into `(n-1, 0)`.
2. Recurse into the `n-1`-sized side: `n - 2` comparisons, splits into `(n-2, 0)`.
3. Recurse into the `n-2`-sized side: `n - 3` comparisons.
4. ...continue until the subarray has 1 element (0 comparisons, base case).

Total comparisons:

```
(n-1) + (n-2) + (n-3) + ... + 1 + 0  =  n(n-1)/2
```

That's the classic sum-of-first-`n`-integers identity. Apply concept.md §1's napkin
method: `n(n-1)/2 = (n² - n)/2`. Drop the constant coefficient `1/2`, drop the
lower-order term `n` — what's left is `O(n²)`.

**Sanity check with a small trace**, `n = 5`, sorted input `[1, 2, 3, 4, 5]`:

- Partition `[1,2,3,4,5]`, pivot=5: compare against 1,2,3,4 → **4 comparisons**, splits `(4, 0)`
- Partition `[1,2,3,4]`, pivot=4: compare against 1,2,3 → **3 comparisons**, splits `(3, 0)`
- Partition `[1,2,3]`, pivot=3: compare against 1,2 → **2 comparisons**, splits `(2, 0)`
- Partition `[1,2]`, pivot=2: compare against 1 → **1 comparison**, splits `(1, 0)`
- Partition `[1]`: base case, 0 comparisons

Total: `4 + 3 + 2 + 1 + 0 = 10`, and `n(n-1)/2 = 5·4/2 = 10`. Matches. Notice the shape:
this is exactly the same nested-loop arithmetic as "compare every element against every
other element" — quicksort's worst case isn't a different kind of quadratic, it's the
same nested-loop cost wearing a recursive-algorithm costume.

## 4. Visual Graph

O(n²) sits between O(n log n) (04-Onlogn-linearithmic) and O(2ⁿ)
(06-O2n-exponential) in the growth-curve ordering. Actual values, so the gap is concrete
rather than just implied:

| n | O(n log n) | O(n²) | O(2ⁿ) |
|---|---|---|---|
| 2 | 2 | 4 | 4 |
| 4 | 8 | 16 | 16 |
| 6 | 16 | 36 | 64 |
| 8 | 24 | 64 | 256 |
| 10 | 33 | 100 | 1,024 |
| 12 | 43 | 144 | 4,096 |

And the shape of it, drawn out (illustrative, not to precise scale — the table above has
the exact numbers):

```
 growth
   ^
   |                                                    ,·'  O(2ⁿ)
   |                                               ,·''
   |                                          ,·''
   |                                     ,·''
   |                                ,·''
   |                          _,·''              ,,--···'''  O(n²)
   |                    _,·''              __,--''
   |              _,·''            __,--''
   |         _,·''           __,--''                     ___----  O(n log n)
   |     _,·''         __,--''                  ___----''
   |  ,·'        __,--''                ___----''
   +-·'----__,--''--___----''----------------------------------->  n
     2     4     6     8     10    12
```

O(n log n) stays nearly flat by comparison. O(n²) climbs noticeably but predictably —
each doubling of `n` roughly quadruples the curve. O(2ⁿ) is barely distinguishable from
flat for small `n` and then rockets past everything else — by `n = 12` it's already 28x
the O(n²) value. That gap is exactly why 06-O2n-exponential is a different category of
problem, not just "a slower version of quadratic."

## 5. Layman Explanation

Picture a folder of `n` text files, and a naive duplicate-content detector: for every
file, scan every *other* file and compare contents byte-for-byte. With 10 files, that's
roughly 100 comparisons. With 100 files, roughly 10,000. You didn't add that many files —
you 10x'd the file count and the work went up 100x. That's the physical feel of O(n²):
the cost isn't "one pass over everything," it's "one pass over everything, repeated once
per item."

Now put quicksort's worst case in the same folder. Imagine those files are log lines
already sitting in an already-sorted-by-timestamp file, and someone re-sorts it with a
naive quicksort that always picks the *last line* as the pivot. Because the file is
already sorted, that last line is always the "biggest" one in whatever chunk you're
currently looking at — so partitioning it doesn't split the chunk in half, it splits off
just that one line and leaves everything else in one big pile. Repeat that `n` times
instead of `log n` times, and you've quietly turned a "divide and conquer" sort into "compare
this line against almost every other line, one line at a time" — the exact same
nested-loop pain as the duplicate detector, just hidden inside recursive calls.
