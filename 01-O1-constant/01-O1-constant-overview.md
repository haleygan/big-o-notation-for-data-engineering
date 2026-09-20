# O(1) — Constant Time

## 1. Mathematical Definition

`f(n) = O(1)` means the cost doesn't depend on `n` at all — it's bounded by some
constant `c`, no matter how big the input gets. Not "small." Not "fast." *Flat.*
A billion-row table and a 3-row table cost the same for a true O(1) operation.

Using concept.md §2's Big O / Θ / Ω framing, applied to this class's two canonical
structures:

**Array index access (`arr[i]`).** This is genuinely Θ(1) — best, average, *and*
worst case are identical. There's no input shape that makes `arr[i]` slower, because
the operation is just arithmetic: `address = base_address + i * element_size`, then
one memory fetch. Same cost every time. This is the rare case in this whole path
where best/average/worst don't need separating, because there's nothing that can
degrade it.

**Hash table lookup (`d[key]` / `key in d`).** This is O(1) *average case*, but that's
doing real work in the sentence — it's not Θ(1) the way array access is:
- **Best case:** O(1) — hash the key, land on a bucket, the value is right there.
- **Average case:** O(1) — assuming a decent hash function and a load factor kept in
  check (this is what people mean when they casually say "hash maps are O(1)").
- **Worst case:** O(n) — if many keys collide into the same bucket, that bucket's
  chain (or the open-addressing probe sequence) degenerates into a linear scan.

**What actually causes the worst case:** either a bad/predictable hash function, or
an adversary who crafts keys to all hash to the same bucket (a real attack class —
"hash flooding" — against web frameworks that used weak hash functions for form
parameters). Practically, in normal data engineering work, the worst case shows up
less from attacks and more from a **bad hash key choice** — e.g. hashing on a field
with almost no variation (like a boolean or a status enum with 3 values) crams every
row into a couple of buckets, and your "O(1) lookup" quietly becomes an O(n) scan.

## 2. Derivation Walkthrough

Start from the code, not the label — this is concept.md §3's method (identify the
basic operation, count how many times it runs as a function of `n`, simplify).

**Array indexing:**

```python
def get_element(arr, i):
    return arr[i]   # <- basic operation
```

Step through it:
1. Basic operation: computing a memory address and dereferencing it.
2. How many times does it run, as a function of `len(arr)`? Once. Always once,
   regardless of whether `arr` has 5 elements or 5 billion — the address formula
   (`base + i * size`) doesn't care about the array's length, only the index.
3. Simplify: 1 operation, no `n` term at all → `O(1)`.

**Hash table lookup:**

```python
def get_value(d, key):
    return d[key]   # <- hash(key), then bucket index, then compare
```

1. Basic operation: hash the key, use the hash to compute a bucket index, compare
   against what's stored there.
2. How many times does step 3 (the compare) run? If the load factor is kept low and
   the hash function spreads keys evenly, ~1 comparison on average — the number of
   *keys already in the table* (`n`) doesn't show up in the operation count, only in
   how full each bucket gets, which the table's resize policy keeps bounded (see
   `space-complexity.md` §3 for why).
3. Simplify: constant work per lookup, independent of `n` → `O(1)` average.

Contrast this with a linear scan (`for item in arr: if item == target: return True`),
where step 2 is explicitly "up to `n` times" — that's the whole difference between
O(1) and O(n): does the basic operation's *count* depend on input size, or not?

## 3. Visual Graph

```
Operation count (y) vs. input size n (x) — log-scaled y so all three curves
stay visible on one plot; O(1) genuinely never leaves the bottom.

  10^5 |                                                          ▄▄  O(n)
       |                                            ▄▄
  10^4 |                              ▄▄
       |
  10^3 |                 ▄▄
       |
  10^2 |         ▄▄
       |
  10^1 |  ▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂  O(log n)
       |
  10^0 |──────────────────────────────────────────────────────  O(1)
       +--------------------------------------------------------------> n
           10        100       1,000      10,000      100,000

n=10        →  O(1): 1     O(log n): ~3     O(n): 10
n=1,000     →  O(1): 1     O(log n): ~10    O(n): 1,000
n=100,000   →  O(1): 1     O(log n): ~17    O(n): 100,000
```

The line for O(1) isn't "small growth" — it's *zero* growth. That flat line at the
bottom is the entire point of this complexity class: at `n = 100,000` it's still
doing exactly 1 unit of work, same as at `n = 10`.

## 4. Layman Explanation

Picture two ways of finding line 500,000 in a huge fixed-width log file, where every
line is padded to exactly 200 bytes:

- **O(1), the "seek" way:** you already know each line is 200 bytes, so line 500,000
  starts at byte `500,000 × 200`. You call `file.seek(that_byte_offset)`, read 200
  bytes, done. One seek, one read — same cost whether the file has 1,000 lines or
  1,000,000,000 lines, because the math to find the offset doesn't get harder as the
  file grows.

- **O(n), the "scan" way:** if lines weren't fixed-width (or you didn't trust the
  offset), you'd `readline()` in a loop, counting until you hit line 500,000. Cost
  scales directly with how far into the file that line is.

Array indexing is the "seek" case — the position is computable in one step. A hash
table lookup is almost the same trick, except instead of the position being your
own arithmetic (`index × size`), it's the hash function's arithmetic (`hash(key) %
table_size`) — but the shape of the win is identical: jump straight to the answer
instead of walking there.
