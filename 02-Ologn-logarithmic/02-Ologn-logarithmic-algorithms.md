# O(log n) — Algorithms

## Algorithm Index

- **Binary search** — find a target in a sorted array by repeatedly halving the search
  range.
- **Binary search tree (BST) / B-tree lookup** — search, insert, or delete in a balanced
  tree structure by walking one level per comparison.
- **Exponentiation by squaring** — compute `x^n` in `O(log n)` multiplications instead of
  `n`.
- **Binary search on the answer** — a pattern, not a single algorithm: binary-search over
  a *range of possible answers* rather than over an array, when the answer space is
  monotonic.

---

## 1. Binary Search

**Background.** The foundational O(log n) algorithm. Requires a sorted, randomly
accessible sequence (array, not a linked list — you need O(1) access to the midpoint,
or the halving trick doesn't pay off). Every other algorithm in this file is either a
direct application of this idea or a generalization of it.

```python
def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1        # target is in the right half
        else:
            high = mid - 1       # target is in the left half
    return -1                    # not found
```

Walkthrough: `low`/`high` bound the current candidate range. Each pass computes the
midpoint, compares it to the target, and throws away the half that can't contain the
target — this is the exact operation counted in `overview.md` §2. The loop terminates
either by finding the target or by `low` crossing `high`, meaning the range emptied out.

Reference: [Binary search algorithm — Wikipedia](https://en.wikipedia.org/wiki/Binary_search_algorithm)

## 2. Binary Search Tree / B-Tree Lookup

**Background.** Generalizes binary search from "halve an array" to "walk a tree." A
balanced BST (red-black tree, AVL tree) keeps height at `O(log n)` for `n` nodes by
rebalancing on insert/delete. A B-tree is the disk/page-oriented cousin used by
databases — each node holds many keys (sized to a disk page) instead of just one, which
reduces tree height further and minimizes disk reads per lookup, but the height is still
`O(log n)` in the node count.

```python
class BSTNode:
    def __init__(self, key, value):
        self.key, self.value = key, value
        self.left = self.right = None

def bst_search(node, key):
    if node is None:
        return None
    if key == node.key:
        return node.value
    elif key < node.key:
        return bst_search(node.left, key)
    else:
        return bst_search(node.right, key)
```

Walkthrough: same comparison-and-branch shape as binary search — each recursive call
walks exactly one level down the tree, and a balanced tree guarantees at most
`O(log n)` levels between root and any leaf. If the tree isn't kept balanced (e.g. keys
inserted in sorted order into a naive BST with no rebalancing), it degenerates into a
linked list and lookup becomes `O(n)` — the tree equivalent of binary search's "must be
sorted" precondition.

Reference: [B-tree — Wikipedia](https://en.wikipedia.org/wiki/B-tree)

## 3. Exponentiation by Squaring

**Background.** Computing `x^n` the naive way is `n - 1` multiplications — O(n). But
`x^n = (x^(n/2))^2` (for even `n`), so you can halve the exponent each step the same way
binary search halves the search range, cutting the multiplication count to `O(log n)`.
Used everywhere fast modular exponentiation matters — RSA/crypto, hashing schemes, and
any "compute a huge power modulo something" step in a data pipeline (e.g. deterministic
sampling/hashing schemes that use modular exponentiation).

```python
def power(x, n):
    result = 1
    while n > 0:
        if n % 2 == 1:        # n is odd — fold current x into the result
            result *= x
        x *= x                # squaring: x becomes x^2, x^4, x^8, ...
        n //= 2               # halve the exponent — same halving idea as binary search
    return result
```

Walkthrough: each loop iteration either doubles `x`'s implicit exponent or folds it into
the result, and `n` is halved every iteration regardless. Number of iterations is
`O(log n)` — same halving argument as `overview.md` §2, applied to an exponent instead of
an array index.

Reference: [Exponentiation by squaring — Wikipedia](https://en.wikipedia.org/wiki/Exponentiation_by_squaring)

## 4. Binary Search on the Answer

**Background.** A pattern rather than a fixed algorithm: instead of binary-searching an
*array*, you binary-search a *range of candidate answers*, using a check function that
tells you "is this candidate answer big/small enough?" This works whenever the answer
space is monotonic — if answer `X` works, every answer bigger (or smaller) than `X` also
works, which is exactly the property binary search's halving logic needs.

```python
def min_capacity_to_ship(weights, days):
    def can_ship_with_capacity(capacity):
        days_needed, current_load = 1, 0
        for w in weights:
            if current_load + w > capacity:
                days_needed += 1
                current_load = 0
            current_load += w
        return days_needed <= days

    low, high = max(weights), sum(weights)
    while low < high:
        mid = (low + high) // 2
        if can_ship_with_capacity(mid):
            high = mid          # mid works — try to do even better (smaller capacity)
        else:
            low = mid + 1       # mid too small — need more capacity
    return low
```

Walkthrough: `low`/`high` bound the *capacity* being searched for, not an array index.
`can_ship_with_capacity` is the monotonic check — if a given capacity ships everything in
time, any larger capacity does too. That monotonicity is what lets binary search's
halving logic apply to an abstract answer space instead of a concrete array.

Reference: this exact problem is LeetCode 1011, "Capacity To Ship Packages Within D Days."

---

## LeetCode Pattern Callout: Binary Search on the Answer

**How to recognize it:** the problem asks for a minimum or maximum value satisfying some
condition ("find the smallest X such that...", "find the minimum capacity/speed/number of
days such that..."), and increasing the candidate value never makes a passing case fail
(monotonicity). If you can write a yes/no function `works(candidate)` where all values
above (or below) some threshold return `True` and all values on the other side return
`False`, you can binary search over the candidates instead of checking every one
linearly.

Example problems using this pattern:
- **Koko Eating Bananas** (LeetCode 875) — find the minimum eating speed such that all
  bananas are eaten within `h` hours.
- **Capacity To Ship Packages Within D Days** (LeetCode 1011) — shown above.
- **Split Array Largest Sum** (LeetCode 410) — find the minimum possible value of the
  largest subarray sum when splitting an array into `k` parts.
