# Memory Profiling — Reading Space Complexity in a Running Process

Sequenced after `09-time-profiling.md` and the entire Big O arc for the same reason:
a memory profiler will happily show you that a function allocated 2 GB — but whether
that's expected, alarming, or catastrophic depends on knowing that the function is
building an O(n) hash table (fine, if n is bounded) versus growing an O(n²) cartesian
product in memory (a production OOM waiting to happen). The number alone doesn't tell
you which; the space-complexity class does.

`concept.md` §4 introduced the distinction between auxiliary and total space, and every
`space-complexity.md` in the seven folders gave you the expected memory profile for each
class. This file is where you go from "I know what O(n) space means" to "I can measure
whether my pipeline is actually behaving like O(n) space or something worse."

---

## 1. What Memory Profiling Measures, and How It Differs From Space Complexity

Space complexity, like time complexity, describes the *shape of the growth curve* — how
much memory an algorithm needs as a function of input size n, asymptotically. A memory
profiler describes something different: the *actual bytes allocated*, on one specific run,
on one specific machine, at a specific moment in execution.

```
Space complexity   → the shape of the memory growth curve (O(n), O(n²), etc.)
Memory profiling   → the actual bytes in use, function by function, at one specific run
```

The two answer complementary questions, in the same way time profiling and time complexity
do (see `09-time-profiling.md` §1). Space complexity tells you how memory should scale;
a profiler tells you where the bytes are actually going right now, and lets you check
whether the two agree.

Three distinct questions come up in practice, each requiring a different tool:

1. **Which function is the biggest memory consumer?** — peak allocation per function,
   useful when you know you're over budget but don't know where the bytes are coming from.
2. **How does memory grow over the course of a run?** — memory-vs-time profile, useful
   for confirming that a streaming job really does hold O(1) auxiliary space instead of
   silently accumulating.
3. **Is any structure growing without bound?** — object-level growth tracking, useful for
   catching the specific case that `capstone.md` §5's first pitfall describes: a structure
   that looks O(1) per operation but actually accumulates because it is never cleared.

Each of these three questions has the right tool for it. Using the wrong tool for the
question gives you technically correct numbers that do not answer the thing you actually
needed to know.

---

## 2. Tool Comparison Table

| Tool | What it measures | Granularity | Overhead | When to reach for it |
|---|---|---|---|---|
| `memory_profiler` (`@profile`) | Line-by-line memory delta | Per line | High (~10x slower) | Finding which specific line allocates the most memory |
| `tracemalloc` (stdlib) | Allocation snapshots, stack traces | Per allocation | Low (~2x slower) | Pinpointing which call site owns a large allocation |
| `psutil` (stdlib-adjacent) | Process RSS / VMS over time | Process-level | Negligible | Watching total memory growth across a long run |
| `objgraph` | Object count by type, growth between snapshots | Per type | Low | Catching which object type is accumulating unexpectedly |
| `memray` (Bloomberg, Python >= 3.8) | Full allocation trace, flamegraph output | Per allocation | Medium | Detailed post-mortem of a profiled run |

`memory_profiler` and `tracemalloc` cover most production diagnostic needs without
installing anything heavy. `memray` is the right upgrade when you need a flamegraph-style
view and are comfortable with the extra dependency. `psutil` is for the simpler question
of "is the process growing over time" — process-level, no stack trace, but also
negligible overhead and zero setup.

---

## 3. Case 1 — Finding Peak Memory Consumption Per Function

### The right tool: `memory_profiler`

`memory_profiler` decorates a function and reports the incremental memory change at
every line. It answers: "which line inside this function is responsible for most of the
allocation?"

### Setup

```bash
pip install memory_profiler
```

```python
from memory_profiler import profile

@profile
def build_session_index(events: list) -> dict:
    """Build a user -> list-of-events index from a flat event list."""
    index = {}                          # O(1) to create the dict shell
    for event in events:               # O(n) iterations
        uid = event["user_id"]
        if uid not in index:
            index[uid] = []
        index[uid].append(event)       # O(1) amortized; total space O(n)
    return index

# Run it:
events = [{"user_id": i % 1_000, "ts": i} for i in range(1_000_000)]
build_session_index(events)
```

Run with:

```bash
python -m memory_profiler your_script.py
```

### Reading the output

```
Line #    Mem usage    Increment   Occurrences   Line Contents
==============================================================
     5     52.3 MiB     52.3 MiB           1   @profile
     6                                         def build_session_index(events):
     7     52.3 MiB      0.0 MiB           1       index = {}
     8     52.3 MiB      0.0 MiB           1       for event in events:
     9    140.7 MiB     88.4 MiB     1000000           uid = event["user_id"]
    10    140.7 MiB      0.0 MiB      999000           if uid not in index:
    11    140.7 MiB      0.0 MiB        1000               index[uid] = []
    12    205.3 MiB     64.6 MiB     1000000           index[uid].append(event)
    13    205.3 MiB      0.0 MiB           1       return index
```

The three columns that matter:

- **Mem usage** — process RSS at the time that line executes. This is cumulative: it
  includes everything allocated before this line. Reading this column top-to-bottom gives
  you the memory trajectory through the function.
- **Increment** — the *marginal* allocation this line caused. This is the column that
  tells you *where the bytes came from* — look for the largest values here, not in
  "Mem usage". In the output above, line 9 (reading each event's `user_id` field,
  triggering the iteration body) added 88.4 MiB; line 12 (appending events into the
  index) added another 64.6 MiB.
- **Occurrences** — how many times that line ran. A line with a small increment *per
  occurrence* but millions of occurrences can still dominate total allocation — 88.4 MiB
  across 1,000,000 iterations is roughly 88 bytes per event, consistent with the event
  dict size.

Common misread: fixating on the highest "Mem usage" line (which just reflects whatever
happened before it) instead of the highest "Increment" line (which is actually responsible
for the allocation). The highest "Mem usage" line is not the culprit — the line with the
highest "Increment" is.

### Connection to space complexity

The output above is consistent with the O(n) space profile `03-On-linear-space-complexity.md`
§1 describes for a hash-join build step: the index holds one entry per distinct key (1,000
user IDs), but the event references inside each list total n = 1,000,000, so the dominant
allocation is proportional to n. If you ran the same function at 2n events and the total
increment roughly doubled, that confirms O(n) auxiliary space — the doubling test for
memory, covered in §6 below.

### DE pipeline example: Spark executor-side groupBy

When Spark executes a `groupBy().agg()` on a partition, the executor builds an in-memory
hash map of group keys to partial aggregates. If the partition contains n rows with m
distinct keys, the hash map holds m entries; partial aggregate state per group is often
a small constant. For well-distributed data, m is much smaller than n and the auxiliary
space per executor is O(m), roughly constant relative to n. Under severe key skew — a
single key holding a large fraction of rows — one executor's hash map must hold that key's
entire partial state, and the aggregate values (say, collecting all values for a
`collect_list`) can grow to O(n) for that one key alone. That is the executor-level OOM
`capstone.md` §3's hash-join discussion warns about. `memory_profiler` on a representative
Python groupBy simulation will show you exactly which line — the aggregation accumulation
line — is responsible for that growth, before you push it to a cluster.

---

## 4. Case 2 — Tracking Memory Growth Over Time During a Run

### The right tool: `tracemalloc` (Python stdlib)

`tracemalloc` takes snapshots of the memory allocator at arbitrary points in your code
and lets you compare them. It answers: "between checkpoint A and checkpoint B, how much
additional memory was allocated, and which call sites are responsible?"

### Setup

No installation required — `tracemalloc` is in the Python standard library since 3.4.

```python
import tracemalloc

tracemalloc.start()

snapshot_before = tracemalloc.take_snapshot()

# --- the code being measured ---
def consume_kafka_partition(records: list) -> list:
    """Streaming transform: filter, enrich, and return records."""
    output = []
    for record in records:
        if record.get("event_type") == "click":
            record["processed"] = True
            output.append(record)        # accumulates matching records only
    return output

records = [{"event_type": "click" if i % 3 == 0 else "view",
            "id": i} for i in range(500_000)]
result = consume_kafka_partition(records)
# --------------------------------

snapshot_after = tracemalloc.take_snapshot()
tracemalloc.stop()

# Compare the two snapshots
top_stats = snapshot_after.compare_to(snapshot_before, "lineno")
print("=== Top 10 memory growth between snapshots ===")
for stat in top_stats[:10]:
    print(stat)
```

### Reading the output

```
=== Top 10 memory growth between snapshots ===
example.py:14: size=18.3 MiB (+18.3 MiB), count=166667 (+166667), average=115 B
example.py:12: size=0.9 MiB (+0.9 MiB), count=500000 (+500000), average=1 B
```

The columns:

- **size** — total bytes currently alive (not freed) that were allocated by this line.
- **+size** — the *delta* since the previous snapshot. This is the primary signal for
  growth tracking: a large positive delta means this line allocated memory that has not
  yet been freed.
- **count / +count** — number of live Python objects allocated by this line. A high count
  with a small per-object size adds up: 166,667 objects at 115 bytes each is the 18.3 MiB
  in the first row.
- **average** — bytes per object. Cross-check against what you would expect from the
  object's structure: a small dict with two string keys and an integer value typically
  occupies 200-350 bytes in CPython; if you're seeing much more, a nested structure is
  likely.

In the output above, line 14 (`output.append(record)`) is responsible for all 18.3 MiB
of net growth — the filtered records being collected into `output`. If the job were truly
streaming (generator, no `output` list), the +size delta at that line would be near zero,
which is the O(1) auxiliary space profile `01-O1-constant-space-complexity.md` §3a describes
for the generator pattern.

To track growth *over time* rather than between two static snapshots, take snapshots in a
loop:

```python
import tracemalloc

tracemalloc.start()
for batch_num, batch in enumerate(batches):
    process(batch)
    if batch_num % 100 == 0:
        snapshot = tracemalloc.take_snapshot()
        stats = snapshot.statistics("lineno")
        current_mb = sum(s.size for s in stats) / 1_048_576
        print(f"batch {batch_num:>6}  current: {current_mb:.1f} MiB")
tracemalloc.stop()
```

A flat or slowly-declining line confirms the job is holding O(1) steady-state memory
between batches. A consistently rising line — even a slow one — indicates accumulation.
"Slowly rising" is not "probably fine." At scale, slow linear growth over 10,000 batches
is a guaranteed OOM.

### Connection to space complexity

`tracemalloc` snapshot comparison is how you verify empirically whether a function that
*should* be O(1) auxiliary space actually is. If the +size delta per snapshot grows
proportionally to n (the batch size), you have found an O(n) accumulation that the code
structure was trying to avoid. If the delta is roughly constant across batches, the
streaming guarantee holds. This maps directly to the two-column reality in
`03-On-linear-space-complexity.md` §1: "O(1) if streaming-through, O(n) if remembering."
Profiling is the tool for checking which one you actually got.

### DE pipeline example: a Kafka consumer that silently accumulates

A Kafka consumer processes events in micro-batches and applies deduplication:

```python
seen_ids = set()   # module-level — persists across batches

def process_batch(batch):
    for event in batch:
        if event["id"] not in seen_ids:
            seen_ids.add(event["id"])
            emit(event)
```

The intention is O(1)-per-event amortized cost for the set lookup. But `seen_ids` is
never cleared: every distinct event ID ever processed is retained for the lifetime of the
process. On an unbounded stream, this is O(n) space where n is the total number of
distinct event IDs ever seen — growing without bound until the process OOMs. A
`tracemalloc` loop around the batch-processing call will show +size growing batch after
batch, eventually making this visible. The fix is one of: clear `seen_ids` after each
time window, bound its maximum size with a TTL-aware structure such as an LRU cache, or
switch to a Bloom filter (`capstone.md` §3's Bloom filter pairing) if occasional false
positives are acceptable.

---

## 5. Case 3 — Catching Unbounded Accumulation

### The right tool: `objgraph`

`objgraph` tracks the *count of live Python objects by type* and can compare two points
in time to show which types grew. It answers: "which object type is accumulating, and
what is holding a reference to it?" — the question `tracemalloc` does not answer directly
because tracemalloc tracks allocation sites, not reference chains.

### Setup

```bash
pip install objgraph
```

```python
import objgraph, gc

def checkpoint(label: str) -> None:
    """Print the top growing types since the last gc.collect."""
    gc.collect()
    print(f"\n=== {label} ===")
    objgraph.show_growth(limit=10)

# Simulate a leaking pipeline stage
accumulated_state = []   # bug: never cleared

def process_event(event):
    accumulated_state.append(event)   # grows without bound
    return {"result": event["value"] * 2}

checkpoint("before")

for i in range(50_000):
    process_event({"id": i, "value": i * 1.5, "metadata": "x" * 50})

checkpoint("after 50k events")
```

### Reading the output

```
=== before ===
(no significant growth)

=== after 50k events ===
dict          50001  +50001
float         50000  +50000
str           50000  +50000
```

The format is: `type  current_count  +delta_since_last_checkpoint`. Read it as:

- **type** — the Python object type accumulating. `dict` is the most common signal in a
  DE pipeline: every event appended to `accumulated_state` is a dict, and this output
  shows exactly 50,001 new live dicts — one per event, plus the list itself.
- **+delta** — the count *increase* since the previous `show_growth()` call. A large
  positive delta that persists across checkpoints (not just a transient spike) is
  accumulation. A delta that returns near zero after the processing function returns means
  the objects were allocated and freed correctly — no leak.
- Cross-reference the type against the code: 50,000 `float` + 50,000 `str` is consistent
  with each event dict containing one float (`value * 1.5`) and one string (`metadata`).
  If you see an unexpected type — `frame`, `weakref`, or a custom class — with a large
  delta, that is the signal to investigate: something is retaining a reference that should
  have been released.

For finding *what* is holding the references, `objgraph` provides `show_backrefs()`:

```python
# After identifying the leaking type:
sample_objects = objgraph.by_type("dict")[:3]
objgraph.show_backrefs(sample_objects, max_depth=3)
# Renders a PNG reference graph — shows the reference chain keeping these objects alive
```

### Connection to space complexity

Unbounded accumulation is always the signature of a space complexity class that is higher
than intended. The common patterns:

| Observed growth in objgraph | What space complexity it maps to |
|---|---|
| Count grows proportionally to total events processed | O(n) — expected if storing full history; a bug if only a window was intended |
| Count grows faster than n (accelerating delta) | O(n²) or worse — a list-of-lists or Cartesian intermediate growing without being flushed |
| Count grows per unique key, unbounded over distinct keys | O(k) where k is key cardinality — expected for a full index, a bug for a cache without eviction |
| Count flat or returns to baseline after each batch | O(1) auxiliary — the desired streaming behavior |

The accelerating-delta case deserves emphasis. If `show_growth()` reports a delta that is
itself growing across equally-sized batches (e.g., +10,000, then +20,000, then +40,000),
the accumulation is not linear — something quadratic or worse is building up in memory.
This is the in-memory analogue of the O(n²) time signature from `concept.md` §3's
doubling test: the ratio between successive deltas is the memory-side version of the
~4x ratio that identifies O(n²) time.

### DE pipeline example: a feature store cache with no eviction

```python
# In a feature engineering stage — runs once per batch row
_feature_cache = {}   # module-level, lives for the process lifetime

def get_features(user_id: str, timestamp: int) -> dict:
    key = (user_id, timestamp)   # every distinct (user, timestamp) pair is a unique key
    if key not in _feature_cache:
        _feature_cache[key] = compute_expensive_features(user_id, timestamp)
    return _feature_cache[key]
```

The intent is O(1) per lookup (serve from cache). The reality: because `timestamp` varies
per event, the cache key `(user_id, timestamp)` is almost always unique — the cache misses
on every call and accumulates one entry per row. For a 100M-row batch, that is 100M dict
entries in `_feature_cache`, which is O(n) space from a structure that was supposed to be
a constant-size optimization. `objgraph.show_growth()` will show `tuple` and `dict` counts
rising in lockstep with rows processed, pointing directly to the cache structure.

The fix is either to key only on `user_id` (if features do not vary by timestamp), to
use a bounded cache with `functools.lru_cache(maxsize=N)` for LRU eviction, or to
precompute and join features in a dedicated stage rather than caching per-row lookups
inside the processing loop. The caching-vs-complexity framing is exactly `capstone.md`
§3's memoization pairing in reverse: where that pairing deliberately *spends* O(n) space
to buy O(n) time instead of O(2^n), this anti-pattern accidentally *accumulates* O(n)
space for no benefit beyond the first lookup.

---

## 6. Doubling Test for Space Complexity

The doubling test from `concept.md` §3 works for memory, not just time. Run your
function at n, then at 2n, then at 4n, and measure the peak auxiliary memory at each
size. The ratio of successive measurements identifies the space complexity class using
the same signature table used for time:

| Space class | Memory ratio when n doubles |
|---|---|
| O(1) | Flat — near 1.0x |
| O(log n) | Barely changes — adds a small constant (roughly log2(2) = 1 extra unit) |
| O(n) | ~2x |
| O(n log n) | Slightly more than 2x |
| O(n^2) | ~4x |
| O(n * m) where m is fixed | ~2x (grows with n, not with m) |
| O(n * m) where m also scales with input | ~4x (both inputs double) |

### Setup

```python
import tracemalloc

def measure_peak_memory(fn, *args) -> float:
    """Return peak memory (MiB) allocated during fn(*args)."""
    tracemalloc.start()
    fn(*args)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1_048_576

def build_join_table(n: int) -> dict:
    """Build side of a hash join over n rows — expected O(n) space."""
    return {i: f"val_{i}" for i in range(n)}

sizes = [10_000, 20_000, 40_000, 80_000, 160_000]
print(f"{'n':>10}  {'Peak MiB':>12}  {'Ratio':>8}")
prev = None
for n in sizes:
    peak = measure_peak_memory(build_join_table, n)
    ratio = f"{peak / prev:.2f}x" if prev else "—"
    print(f"{n:>10}  {peak:>12.2f}  {ratio:>8}")
    prev = peak
```

### Reading the output

```
         n      Peak MiB     Ratio
     10000          1.23         —
     20000          2.45      1.99x
     40000          4.88      1.99x
     80000          9.73      1.99x
    160000         19.41      1.99x
```

The ~2x ratio at every doubling step is the O(n) memory signature. If the ratio column
instead approached ~4x, the space complexity would be O(n²). If it approached ~1x, you
have confirmed O(1) auxiliary space — a streaming job that does not accumulate despite
processing n inputs.

The ratio column is the direct memory-side equivalent of the time doubling signatures
in `concept.md` §3. The two tables are the same table, applied to two different
resources. A job that shows ~2x time ratio and ~2x memory ratio at every doubling is
behaving as O(n) in both dimensions — which, for most data pipeline stages, is the
target profile.

### Caveats

The same two caveats from `concept.md` §3's doubling test apply here:

- **Small n swamps signal with constant-factor overhead.** At n = 100, Python's
  interpreter itself, the function call frame, and the argument objects dwarf the
  algorithm's actual allocation. Start the doubling test at a size where the algorithm's
  own allocation clearly dominates — usually n >= 10,000 for lightweight objects, larger
  for heavily-structured ones.
- **The ratio tells you the class, not the algorithm.** A 2x ratio confirms O(n) space
  but is consistent with any O(n) implementation. If you need to know *which* O(n)
  structure is responsible for the memory, follow up with `tracemalloc` (Case 2 above)
  or `objgraph` (Case 3 above).

---

## 7. Output Reading Strategy — A Decision Order

Given a real memory problem — OOM, unexpected memory growth, a process ballooning beyond
its container limit — here is a reliable order of operations. The order matters: it goes
from cheap and broad to expensive and narrow.

**Step 1 — Confirm growth is real and measure the rate (process-level RSS).**
Before instrumenting code, use `psutil` or a simple `/proc/self/status` read to verify
the process RSS is genuinely growing, and at what rate. This filters out false alarms
where a one-time allocation on startup looks alarming but never grows again.

```python
import psutil, os
proc = psutil.Process(os.getpid())
print(f"RSS: {proc.memory_info().rss / 1_048_576:.1f} MiB")
```

**Step 2 — Run a doubling test (§6) to identify the space complexity class.**
Before instrumenting individual functions, knowing the class tells you what scale of
problem you are looking at. O(n) growing linearly is a different engineering problem from
O(n²) growing quadratically — the fix is different, and the urgency is very different.

**Step 3 — Use `tracemalloc` snapshots to identify the allocating call site (Case 2 §4).**
`compare_to()` between two snapshots narrows the problem to a line of code. This is the
"where in the code is it coming from" question.

**Step 4 — Use `objgraph.show_growth()` to identify the accumulating object type
(Case 3 §5).** If step 3 points to a line that allocates a type that should be
short-lived, `objgraph` tells you which type is staying alive. `show_backrefs()` shows
the reference chain keeping it alive.

**Step 5 — Use `memory_profiler` to understand the per-line allocation inside a single
function (Case 1 §3).** This is most useful once you have already narrowed the problem
to one function — it is line-level, so it is expensive and verbose to run on the whole
codebase.

This ordering mirrors the advice in `09-time-profiling.md` §4 for time profiling: confirm
that the problem exists, identify its complexity class from growth behaviour, then narrow
to the specific site. Running `memory_profiler` on an entire codebase before you know
which function is the problem is the memory equivalent of reading a full Spark execution
plan before confirming that the job is even slow.

---

## 8. End-of-Session Test

The four-question format from `progress.md` §4 — identify, fix, scenario, tricky claim.

---

**Question 1 — Identify the space complexity.**

```python
def build_pair_index(records: list) -> dict:
    index = {}
    for r in records:
        key = r["a"]
        if key not in index:
            index[key] = []
        for other in records:          # nested loop over the full list
            if other["a"] == key:
                index[key].append(other["b"])
    return index
```

`records` has n entries. What is the space complexity of `build_pair_index`, and what is
the time complexity? Which profiling tool from this file would best confirm the space
complexity class empirically, and what ratio would you expect to see in a doubling test?

---

**Question 2 — Fix the code.**

A Kafka consumer processes sensor events. After a week in production the process is
OOM-killed every three days. The relevant code:

```python
import time

event_log = []         # module-level

def handle_event(event: dict) -> None:
    enriched = {**event, "processed_at": time.time()}
    event_log.append(enriched)
    if len(event_log) % 10_000 == 0:
        flush_to_s3(event_log[-10_000:])
```

Identify the space complexity class of `event_log` over the lifetime of this process.
Rewrite the function so that auxiliary space is O(1) across batches — flush and release
each batch completely — while preserving the flush-every-10,000 behavior. What
`objgraph` output would have revealed the bug before it reached production?

---

**Question 3 — Real scenario.**

You are building a daily batch job that joins a 200M-row fact table against a 500-row
config table. The job runs on a single machine with 16 GB RAM. A colleague's
implementation builds the full join in memory as a Python dict-of-lists before writing
any output. A `memory_profiler` run shows the peak hitting 14 GB at the merge step.

Using the space complexity vocabulary from this course:

- What is the space complexity of the colleague's approach, expressed in terms of the
  two input sizes n (fact rows) and m (config rows)?
- What is the memory floor you should expect for *any* correct implementation of this
  join, and why?
- Propose an alternative strategy from the join strategies in `concept.md` §6 and
  `capstone.md` §3 that reduces auxiliary space, and state what space complexity it
  achieves.

---

**Question 4 — Tricky claim.**

A teammate runs a doubling test on a new aggregation function and reports:

> "The ratio column showed 1.9x at n = 1,000 and 2.1x at n = 10,000. Sometimes it is
> below 2x, so I think the space complexity might be sub-linear — maybe O(log n)?"

Identify what is correct in this observation and what is wrong. What does a ratio
fluctuating between 1.9x and 2.1x actually tell you? At what n values would you start
trusting a doubling-test ratio for a function that allocates simple Python dicts, and
why does the answer differ from what you would use for a time-based doubling test?
