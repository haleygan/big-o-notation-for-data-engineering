# O(log n) — Space Complexity

## 1. Typical Space Cost

**Iterative binary search: O(1) auxiliary space.** Look back at the loop in
`overview.md` §2 — `low`, `high`, and `mid` are three integer variables, and that's it.
None of them grow with `n`. Total space is the input array itself (which you didn't
allocate, it already existed) plus a constant handful of variables. This is the
"in-place" case concept.md §4 describes: auxiliary space stays flat regardless of input
size.

**Recursive binary search: O(log n) auxiliary space.** If you write binary search as a
function that calls itself on one half instead of looping, each call adds a frame to the
call stack, and that frame doesn't pop until the recursive call underneath it returns:

```python
def binary_search_recursive(arr, target, low, high):
    if low > high:
        return -1
    mid = (low + high) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, high)
    else:
        return binary_search_recursive(arr, target, low, mid - 1)
```

The recursion depth mirrors the loop count from the time analysis exactly — every level
of recursion halves the range the same way every loop iteration did — so the call stack
grows to `O(log n)` frames deep before unwinding. Same time complexity as the iterative
version, different space profile.

**B-tree / database index lookup:** a B-tree traversal (Postgres, MySQL InnoDB, most
production index structures) walks from the root page down to a leaf page, reading one
page per level. The traversal itself needs O(1) extra space beyond a pointer to "current
page" — it doesn't need to remember the path it took unless it's also going to do
something like a reverse scan or a delete-with-rebalancing, which is a separate concern
from the plain lookup.

## 2. Amortized Behavior

Not really applicable to this class the way it is to `01-O1-constant`. Amortized cost
(concept.md §5) is about a *sequence of operations on the same structure*, where
occasional expensive operations average out — dynamic array doubling, hash table resize.
A single binary search, or a single B-tree lookup, is a one-shot operation: it doesn't
have a "sometimes expensive, usually cheap" pattern to average over. Every lookup costs
the same `O(log n)` regardless of which lookup number it is in a sequence.

The place amortization *does* show up nearby is B-tree **inserts**, not lookups — a
B-tree node that overflows triggers a page split, which is momentarily more expensive
than a normal insert, and that cost amortizes across the inserts between splits. But
that's a different operation with a different complexity profile (see `algorithms.md`
for the lookup-focused version); the lookup itself, this folder's canonical operation,
has no amortized component worth deriving.

## 3. Local Time/Space Tradeoff

Within this same O(log n) time class, iterative vs. recursive binary search is the
textbook local tradeoff:

| Variant | Time | Auxiliary space | Why pick it |
|---|---|---|---|
| Iterative | O(log n) | O(1) | No stack growth, no recursion-depth limits, marginally faster in most languages (no call overhead) |
| Recursive | O(log n) | O(log n) | Reads closer to the mathematical definition ("solve on half the problem"), sometimes clearer for tree-shaped variants (e.g. recursive BST search naturally mirrors recursive binary search) |

Same time complexity either way — the tradeoff is purely on the space axis, and it's a
small one, since `O(log n)` stack frames for even a billion-element array is only ~30
frames. This is a case where the "extra" cost of the more expensive variant is still
negligible in absolute terms; it becomes a real concern only in languages/runtimes with
small default stack limits or extremely tight memory budgets (e.g. embedded contexts).

## 4. Worst-Case Space Deviation

This is the interesting negative result: **there isn't one**, and that's worth noticing
explicitly because it's the exception rather than the rule among the 7 complexity
classes in this path.

Compare to quicksort (`05-On2-quadratic`): its recursion-stack space is O(log n) on
*average* (balanced partitions) but degrades to O(n) stack depth on adversarial pivot
choices — same root cause as its O(n²) worst-case time, because both come from
partitions being lopsided instead of balanced.

Binary search has no equivalent failure mode *within its assumptions*. Every recursive
call splits the remaining range in exactly half (or as close to half as integer division
allows), regardless of what values are in the array or what target you're searching for.
There's no "unlucky" input that makes one half bigger than the other — the split point
is determined by array *position* (the midpoint index), not by data values. So the
recursion depth is always `Θ(log n)`, worst case equals average case equals (up to a
small constant) best case, for both time and space.

The one place this whole model *does* break — same one flagged in `overview.md` §1 — is
an unsorted input array. That's not a "worst case within the model," it's stepping
outside the model's precondition entirely: the algorithm's halving logic silently
produces wrong answers instead of a slower right answer, and there's no space-complexity
angle to that failure at all, since it's a correctness bug, not a performance one.

## 5. Cross-Link

See root `capstone.md` for how this class's O(log n) time / O(1)-to-O(log n) space
profile stacks up against the other 6 complexity classes on the same axes.
