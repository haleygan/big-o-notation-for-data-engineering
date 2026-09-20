# O(1) — In Data Engineering

## 1. DE Technology Examples

| Technology | Operation | Why this complexity | Minimal code sample |
|---|---|---|---|
| Redis | `GET key` | In-memory hash table keyed by string; hash the key, jump to its slot | `r.get("user:1234:features")` |
| Python `dict` | key lookup | CPython dict is an open-addressing hash table under the hood | `feature_vec = cache[user_id]` |
| Java `HashMap` | `map.get(key)` | Same hash-table mechanics, classic JVM data-processing glue code | `Vector v = map.get(userId);` |
| Apache Kafka | default partitioner | Hashes the record key (murmur2) straight to a partition number — no scan over partitions | `producer.send(ProducerRecord("t", key, val))` |
| Postgres | hash index equality lookup | `CREATE INDEX ... USING HASH` maps a value straight to a bucket, unlike a B-tree's O(log n) descent | `SELECT * FROM users WHERE id = 42;` |
| pandas | `.at[]` scalar access | Direct label-based single-cell access, not a scan over the column | `df.at[5, "revenue"]` |
| Apache Spark | broadcast variable read | Small lookup table shipped once to every executor; each task reads it locally, no shuffle | `bc.value.get(key)` |
| Memcached | `cache.get(key)` | Same hash-table-backed key-value model as Redis, older generation | `mc.get("session:abc123")` |

## 2. Where It Naturally Emerges

- **Feature store reads at inference time.** An online feature store (Redis,
  DynamoDB, a keyed cache) maps `entity_id -> feature_vector`. A model server doing
  real-time scoring needs this lookup to stay O(1) regardless of how many entities
  exist, because it's on the request's critical path — an O(log n) or O(n) lookup
  here directly becomes added request latency at scale.

- **Deduplication membership checks.** Before writing a record, checking "have I
  already processed this event ID" against an in-memory `set` (or a Redis `SISMEMBER`)
  is the O(1) hash-table pattern applied to streaming dedup — the alternative
  (scanning a list of seen IDs) turns a cheap per-event check into an O(n) one that
  gets slower as the run goes on. Pairing the O(1) membership check with the generator
  pattern keeps the whole pipeline lean — check-and-emit, one event at a time, nothing
  accumulates beyond the `seen_ids` set itself:

  ```python
  def dedup(events):
      seen_ids = set()
      for event in events:
          if event["id"] in seen_ids:   # O(1) membership check
              continue
          seen_ids.add(event["id"])     # O(1) amortized insert
          yield event                   # O(1) auxiliary space per event — see 01-O1-constant-space-complexity.md §3a
  ```

  (`seen_ids` itself is the one deliberately O(n) piece here — see
  `capstone.md` §3 for the exact-set-vs-Bloom-filter tradeoff once that set gets too
  large to hold in memory.)

- **Broadcasting a small dimension table in Spark.** Instead of shuffling both sides
  of a join across the cluster, Spark can broadcast a small table to every executor
  and let each task do local O(1) hash lookups against it in-memory — this is the
  multi-variable framing from concept.md §6's join table, picking the strategy whose
  per-row cost is O(1) instead of paying for a shuffle.

- **Keyed state access in stream processing.** Kafka Streams and Flink both keep
  per-key state (running counts, last-seen values, session windows) in a keyed store
  backed by a hash table (often RocksDB with an in-memory hash index layer). Each
  incoming event does an O(1) get/put against its own key's state, independent of
  how many other keys exist in the job.

- **Config and feature-flag lookups.** Any per-request or per-row check against a
  small, frequently-read config map (`is_feature_enabled(flag_name)`) is the same
  pattern at a smaller scale — the map might have a handful of entries, but the win
  is that the lookup cost doesn't grow as you add more flags or more traffic.

- **Rate limiting / counters.** Incrementing a per-key counter (`INCR user:1234:reqs`
  in Redis) to enforce a rate limit is an O(1) read-modify-write against a single
  bucket, done once per event, no matter how many other keys are being rate-limited
  in parallel.

## 3. O(1) Does Not Mean Equally Fast — Constant Factors

Two operations can both be O(1) — same complexity class, same growth shape — and still
differ by an order of magnitude in practice, because Big O deliberately drops the
constant factor (`concept.md` §1) and that constant factor is where the real work hides.

**`set.add(x)` vs. `list.append(x)`.** Both are O(1) amortized. Benchmarked head to
head at `n = 1,000,000` insertions:

```
set.add:      0.00038 ms/op
list.append:  0.000035 ms/op
→ set.add is ~10.9x slower, same complexity class
```

The gap is entirely constant-factor work that `list.append` doesn't do: `set.add` has to
compute a hash of the value, use it to locate a bucket, check that bucket for a
collision, and possibly trigger a resize once the load factor crosses its threshold
(`01-O1-constant-space-complexity.md` §2). `list.append` just writes to the next free
slot. Same asymptotic label, genuinely different amount of work per call — and in
practice this multiplier commonly lands anywhere in the 10x-36x range depending on `n`,
hash cost, and Python version.

**Why this matters for DE:** "it's O(1), so it doesn't matter which one I use" is a
trap. In a hot loop processing millions of rows, picking `set` when a `list` (or no
structure at all) would do costs real wall-clock time, even though a complexity-only
analysis says they're equivalent. Big O tells you how a cost *scales* — it was never a
promise about which of two same-class options is faster in absolute terms. That question
needs a benchmark, not an asymptotic argument (see `concept.md` §3's benchmark-doubling
technique for how to reason about the scaling side once you *do* have real timings).

## 4. Common O(n²) Mistakes That Look Like O(1)

The flip side of the section above: some operations that *look* like a cheap, constant
per-step cost are actually hiding an O(n) cost inside what appears to be "just adding one
more thing" — and doing that inside a loop silently turns an O(n)-looking loop into
O(n²) total work.

**String concatenation in a loop.** Python strings are immutable. `result = result +
next_piece` doesn't extend `result` in place — it allocates an entirely new string and
copies the *whole accumulated result* into it, every time, regardless of how small
`next_piece` is.

```python
# O(n^2) total -- each `+` copies everything accumulated so far
result = ""
for word in words:
    result = result + word

# O(n) total -- allocates once, knows the final size upfront
result = "".join(words)
```

This is the direct counterpart to `list.append`'s amortized O(1): `list.append` reuses
spare capacity in its backing buffer and only occasionally pays an O(n) resize, spread
thin enough to amortize to O(1) per call (`01-O1-constant-space-complexity.md` §2).
String `+=` pays a full copy on *every* call, with no spare capacity to reuse — so
there's nothing to amortize over, and the true cost per operation is O(n), not O(1). See
`concept.md` §5 for the full walkthrough of why one pattern amortizes and the other one
doesn't, even though both "look like" the same kind of loop.

**Why this matters for DE:** this exact pattern shows up constantly in code that builds
up a large string inside a loop — assembling a log line field by field, concatenating a
SQL query from clauses, building a JSON payload by hand instead of using a serializer.
Each individual `+` looks harmless; the O(n²) cost only becomes visible once `n` (the
number of pieces, or the size of the accumulated string) gets large enough to matter,
which is exactly the kind of thing that's invisible in a small dev dataset and painfully
visible in production.
