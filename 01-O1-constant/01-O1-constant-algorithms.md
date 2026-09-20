# O(1) — Algorithms

## 1. Algorithm Index

- **Array/list index access** — jump straight to an element via computed address,
  no traversal.
- **Hash table lookup / insert / delete (average case)** — hash a key straight to a
  bucket instead of searching for it.
- **Stack push / pop** — add/remove from one end of a structure, no shifting.
- **Queue enqueue / dequeue (deque / circular buffer backed)** — add/remove from
  either end without touching the rest of the structure.
- **Bitmask check** — test/set a single bit in a fixed-width integer.

## 2. Algorithm Details

### Array Index Access

**Background/context.** This is the operation every other O(1) structure in this
folder ultimately builds on top of. Arrays live in one contiguous block of memory,
so "give me element `i`" is pure arithmetic (`base_address + i * element_size`),
not a search. It's the reason arrays exist as a primitive at all instead of every
language just using linked lists everywhere.

**Code sample:**

```python
def get_element(arr: list, i: int):
    return arr[i]          # one address computation, one memory fetch
```

Walkthrough: `arr[i]` in CPython resolves to a pointer-array dereference at index
`i` — CPython lists are arrays of pointers to objects, so this is: compute
`arr.ob_item + i` (pointer arithmetic), then dereference that pointer. Cost is fixed
regardless of `len(arr)`.

**Reference:** [Python data model — sequence indexing](https://docs.python.org/3/reference/datamodel.html#object.__getitem__); general background: [Wikipedia — Array (data structure)](https://en.wikipedia.org/wiki/Array_(data_structure)).

---

### Hash Table Lookup / Insert / Delete

**Background/context.** Solves "map an arbitrary key to a value fast" without
needing the keys sorted or comparable — a tree-based map (O(log n)) needs an
ordering on keys; a hash table only needs the keys to be hashable. It trades a
worst-case guarantee for an average-case win, which is exactly the tension
`overview.md` §1 walks through.

**Code sample** (a minimal separate-chaining hash table, to show the mechanics
Python's `dict` hides from you):

```python
class SimpleHashTable:
    def __init__(self, capacity: int = 8):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0

    def _bucket_index(self, key) -> int:
        return hash(key) % self.capacity          # step 1: hash -> bucket index

    def put(self, key, value) -> None:
        idx = self._bucket_index(key)
        bucket = self.buckets[idx]
        for i, (k, _) in enumerate(bucket):        # step 2: check for existing key
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))                # step 3: append new entry
        self.size += 1
        if self.size / self.capacity > 0.7:        # resize trigger — see
            self._resize()                         # space-complexity.md §2

    def get(self, key):
        idx = self._bucket_index(key)
        for k, v in self.buckets[idx]:              # O(1) average: bucket has
            if k == key:                            # ~size/capacity entries
                return v
        raise KeyError(key)

    def _resize(self) -> None:
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for bucket in old_buckets:                  # O(n) — this one call pays
            for key, value in bucket:                # for every future O(1) put,
                self.put(key, value)                 # amortized (see space-complexity.md §2)
```

Walkthrough: `put`/`get` both do one hash computation to find a bucket, then walk
*that bucket only* — not the whole table. As long as `_resize` keeps the average
bucket short (via the load-factor check), that inner walk stays O(1) on average.
The `_resize` call itself is the O(n) operation that `space-complexity.md` §2
explains gets amortized away across a sequence of inserts.

**Reference:** [Wikipedia — Hash table](https://en.wikipedia.org/wiki/Hash_table); for how CPython's real `dict` does it (open addressing, not chaining): [CPython dict implementation notes](https://github.com/python/cpython/blob/main/Objects/dictobject.c).

---

### Stack Push / Pop

**Background/context.** LIFO (last-in-first-out) access shows up everywhere:
function call stacks, undo/redo, DFS traversal, matching brackets/parentheses,
expression evaluation. The reason it's O(1) is structural — you only ever touch
the *one* end of the structure, so nothing ever needs to shift.

**Code sample:**

```python
stack: list = []

def push(item) -> None:
    stack.append(item)     # O(1) amortized — see space-complexity.md §2

def pop():
    return stack.pop()     # O(1) — removes the last element, no shifting
```

Walkthrough: `list.append` writes to the next free slot (or triggers a resize —
amortized O(1), per `space-complexity.md` §2). `list.pop()` with no argument
removes the *last* element — critically, not `pop(0)`, which would have to shift
every remaining element left by one slot and is O(n). Popping from the wrong end is
the single most common way people accidentally turn an O(1) stack operation into an
O(n) one.

**Reference:** [Wikipedia — Stack (abstract data type)](https://en.wikipedia.org/wiki/Stack_(abstract_data_type)).

## 3. LeetCode Pattern Callout

**Pattern: "hash map for O(1) lookup."** Recognize it whenever a problem asks some
version of "have I seen this before," "find the complement/pair," or "count
occurrences" — anywhere the naive approach is "for each item, scan everything else"
(O(n²)), and the fix is "for each item, check a hash map instead" (O(n)). The
signal phrases in a problem statement: *"find two numbers that..."*, *"check for
duplicates"*, *"group by..."*, *"first non-repeating..."*.

Example problems that use this pattern:
- **Two Sum** — for each number, check `target - num` against a hash map of numbers
  seen so far, instead of nested-looping over every pair.
- **Contains Duplicate** — insert each element into a `set`; if an insert finds it
  already there, you're done. O(n) total instead of an O(n²) all-pairs comparison
  or an O(n log n) sort-first approach.
- **LRU Cache** — combines a hash map (O(1) key → node lookup) with a doubly linked
  list (O(1) move-to-front / evict-from-back), so both `get` and `put` stay O(1).
