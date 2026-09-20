# Progress — Teaching Session Log & Plan

Living document. Update after every session: move newly-completed topics into §1, and
adjust §3 if a session runs long, short, or surfaces a new topic that needs folding into
the reference files (see `learning.md`'s Part 2/3 pattern for how that folding-in works).

Not part of the core Big O content (`concept.md` → 7 folders → `capstone.md` →
`09-time-profiling.md` and `10-memory-profiling.md`) — this file is about *this specific learner's* path through it, not the
subject matter itself.

---

## 1. Sessions Completed

**Session 1 + 2** (2026-08-18 report) — `concept.md` §1-§5 in full, plus `01-O1-constant`
in full depth. Taught in this order, listed so a future session can resume without
repetition:

| # | Topic | Reference |
|---|---|---|
| 1 | Time complexity — operations vs. wall-clock seconds | `concept.md` §3 |
| 2 | Basic operation — the unit of work that scales with n | `concept.md` §3 |
| 3 | Counting operations — fraud-check walkthrough | `concept.md` §3 |
| 4 | Big O — dropping constants and multipliers | `concept.md` §1 |
| 5 | Napkin method — simplifying f(n) to a Big O class | `concept.md` §1 |
| 6 | Deriving exact f(n) before simplifying | `concept.md` §3 |
| 7 | Big O vs Θ vs Ω — upper, tight, lower bounds | `concept.md` §2 |
| 8 | Best / worst / average case — fraud check as worked example | `concept.md` §2 |
| 9 | `if` early-exit vs. `continue` vs. no-skip — how each changes the bound | `concept.md` §2 |
| 10 | O(1) — array index access, memory address formula | `01-O1-constant-overview.md` |
| 11 | O(1) — hash table lookup, collisions, load factor | `01-O1-constant-overview.md` |
| 12 | O(1) — cardinality's effect on hash table worst case | `01-O1-constant-overview.md` |
| 13 | O(1) growth curve vs. O(log n), O(n), O(n²) | `01-O1-constant-overview.md` |
| 14 | O(1) real DE examples — dict lookup, Redis, Spark broadcast, streaming dedup | `01-O1-constant-de-application.md` |
| 15 | Preprocessing tradeoff — pay O(n) once, get O(1) forever | `01-O1-constant-de-application.md` |
| 16 | `list` vs `set` — why membership check is O(n) vs O(1) | `01-O1-constant-overview.md` |
| 17 | Space complexity — total vs. auxiliary space | `concept.md` §4 |
| 18 | What makes a change O(1) vs O(n) in space — mutation vs. new structure | `concept.md` §4 |
| 19 | Per-operation vs. pipeline-level auxiliary space — scope of measurement | `concept.md` §4 |
| 20 | Nested structures — O(n×m) space explosion | `concept.md` §4 |
| 21 | Generator pattern — `yield` for O(1) per-event auxiliary space | `01-O1-constant-space-complexity.md` §3a |
| 22 | Amortized complexity — definition, aggregate-method derivation | `concept.md` §5 |
| 23 | `list.append` resize mechanic — amortized O(1), geometric series | `01-O1-constant-space-complexity.md` §2 |
| 24 | List concat `+` — O(n) per call, O(n²) total, O(n) amortized/op | `01-O1-constant-example.py` |
| 25 | Amortized formula — total cost / n operations | `concept.md` §5 |
| 26 | Live benchmark — set O(1) vs list O(n); append O(1) vs concat O(n²) | `01-O1-constant-example.py` |
| 27 | Benchmark doubling signature — n doubling → time response by class | `concept.md` §3 |
| 28 | `set.add` vs `list.append` — same O(1) amortized, different constant factor | `01-O1-constant-de-application.md` §3 |
| 29 | String concatenation — same O(n²) pattern as list concat | `01-O1-constant-de-application.md` §4, `concept.md` §5 |
| 30 | Profiling — introduced briefly, parked for dedicated session | `09-time-profiling.md` (stub) |

All 30 topics above are now represented in the reference files (items 27-29 and the
generator pattern were added to `concept.md` / `01-O1-constant` after the session, since
they came up live and weren't in the original draft).

**Not yet covered:** `concept.md` §6 (Multi-variable complexity) is the one remaining gap
in the foundational primer — first item in Session 3 below.

---

## 2. Student Knowledge Profile

**Strengths:**
- Independent mathematical reasoning — derives conclusions before being told
- Catches instructor errors (caught a wrong `continue` vs `return` table entry; caught a
  `return False` operation-count omission)
- Connects concepts forward unprompted (identified the space consequence of a `set()`
  solution without being asked)
- Multi-variable thinking — naturally uses distinct variable names (u, t, c, f) instead
  of overloading `n`, ahead of `concept.md` §6 being formally taught
- Production thinking — asks "is this worth it in practice?" not just "what's the
  theory?"

**Areas to reinforce:**
- Notation precision — occasionally writes `O(n) = n²` instead of `O(n²)`; wrote
  `seen_events = ()` (a tuple) when meaning `set()`
- Distinguishing per-operation cost from pipeline-level cost — needed clarification on
  preprocessing O(n) + lookup O(1) as a combined cost, not two separate claims
- Multi-variable notation — wrote O(n²) for what was actually O(n×m) (a nested loop over
  two differently-sized inputs) — understands the concept, notation habit needs a pass
  once §6 is formally taught

**Teaching style that's working — keep doing this:**
- One concept at a time, explicit confirmation before moving on
- Numerical evidence before the formal rule — show real numbers first, derive the rule
  after
- Real production examples grounded in DE — fraud detection, Kafka streams, Spark joins
- Benchmarks with actual printed output — real timing numbers cement the theory faster
  than the proof does
- Let the student derive before confirming — ask "what do you think?" before explaining

---

## 3. Session Plan

### Session 3 — Next — Multi-Variable Complexity + O(log n)

| Order | Topic | Source | Est. time |
|---|---|---|---|
| 1 | §6 Multi-variable complexity — O(n×m) vs O(n+m), variables differing by orders of magnitude | `concept.md` §6 | 20 min |
| 2 | O(log n) overview — mathematical definition, halving derivation, log₂(n) table | `02-Ologn-logarithmic-overview.md` | 20 min |
| 3 | O(log n) algorithms — binary search, step by step | `02-Ologn-logarithmic-algorithms.md` | 20 min |
| 4 | O(log n) DE application — Postgres B-tree index, why indexes exist | `02-Ologn-logarithmic-de-application.md` | 15 min |
| 5 | O(log n) space complexity | `02-Ologn-logarithmic-space-complexity.md` | 10 min |
| 6 | O(log n) benchmark — run `example.py`, read the doubling signature | `02-Ologn-logarithmic-example.py` | 10 min |
| 7 | End-of-session test — O(log n) | — | 15 min |

### Session 4 — O(n), Linear Time

| Order | Topic | Source |
|---|---|---|
| 1 | Overview — derivation, when a full scan is unavoidable | `03-On-linear-overview.md` |
| 2 | Algorithms — linear scan, hash join build+probe | `03-On-linear-algorithms.md` |
| 3 | DE application — Kafka consumer, pandas `.apply()` | `03-On-linear-de-application.md` |
| 4 | Space complexity — streaming O(1) vs. accumulating O(n); generator-pattern cross-link | `03-On-linear-space-complexity.md` |
| 5 | Benchmark | `03-On-linear-example.py` |
| 6 | End-of-session test | — |

### Session 5 — O(n log n), Linearithmic Time

| Order | Topic | Source |
|---|---|---|
| 1 | Overview — why sorting costs n log n, not n | `04-Onlogn-linearithmic-overview.md` |
| 2 | Algorithms — merge sort derivation | `04-Onlogn-linearithmic-algorithms.md` |
| 3 | DE application — Spark `SortMergeJoinExec` | `04-Onlogn-linearithmic-de-application.md` |
| 4 | Space complexity | `04-Onlogn-linearithmic-space-complexity.md` |
| 5 | Benchmark | `04-Onlogn-linearithmic-example.py` |
| 6 | End-of-session test | — |

### Session 6 — O(n²), Quadratic Time

| Order | Topic | Source |
|---|---|---|
| 1 | Overview — nested-loop derivation, when it appears | `05-On2-quadratic-overview.md` |
| 2 | Algorithms — nested-loop join, naive all-pairs dedup | `05-On2-quadratic-algorithms.md` |
| 3 | DE application — Postgres nested-loop join, when it's acceptable | `05-On2-quadratic-de-application.md` |
| 4 | Space complexity — quicksort's worst-case stack-depth deviation | `05-On2-quadratic-space-complexity.md` |
| 5 | Benchmark | `05-On2-quadratic-example.py` |
| 6 | End-of-session test | — |

### Session 7 — O(2ⁿ) and O(n!) — Exponential and Factorial Time

Cover both in one session — same conceptual framing: "the point where more compute stops
being a viable answer."

| Order | Topic | Source |
|---|---|---|
| 1 | O(2ⁿ) overview — naive recursion, power set | `06-O2n-exponential-overview.md` |
| 2 | O(2ⁿ) DE application — SQL `GROUP BY CUBE` | `06-O2n-exponential-de-application.md` |
| 3 | O(n!) overview — permutation search, TSP | `07-Onfactorial-factorial-overview.md` |
| 4 | O(n!) DE application — Postgres join-order search | `07-Onfactorial-factorial-de-application.md` |
| 5 | Combined benchmark — all 7 classes on one chart | `capstone.md` §2 |
| 6 | End-of-session test — both classes | — |

### Session 8 — Capstone: Strategy Selection Framework

| Order | Topic | Source |
|---|---|---|
| 1 | Master comparison table — all 7 classes side by side | `capstone.md` §1 |
| 2 | Time/space tradeoff pairs — hash join vs. sort-merge, exact vs. sketch, exact-set vs. Bloom filter | `capstone.md` §3 |
| 3 | Decision framework — the 6-question checklist | `capstone.md` §4 |
| 4 | Common pitfalls — OOM, over-engineering, adversarial input | `capstone.md` §5 |
| 5 | Final capstone test — full decision scenario | — |

### Session 9 — Completed — Time Profiling

| Order | Topic | Source |
|---|---|---|
| 1 | What profiling measures vs. Big O — the two complementary diagnostics | `09-time-profiling.md` §1 |
| 2 | Reading `cProfile` output — `ncalls`, `tottime`, `cumtime`, spotting the real bottleneck | `09-time-profiling.md` §2 |
| 3 | Reading a Spark execution plan — `explain()` DAG, mapping stages back to join/sort strategies | `09-time-profiling.md` §3 |
| 4 | Mapping profiling results back to Big O classes — growth pattern recognition | `09-time-profiling.md` §4 |

### Session 10 — Next — Memory Profiling

| Order | Topic | Source | Est. time |
|---|---|---|---|
| 1 | What memory profiling measures vs. space complexity — complementary diagnostics | `10-memory-profiling.md` §1 | 10 min |
| 2 | Tool comparison — `memory_profiler`, `tracemalloc`, `psutil`, `objgraph`, `memray` | `10-memory-profiling.md` §2 | 10 min |
| 3 | Case 1: Finding peak memory per function — `@profile`, reading Increment vs. Mem usage | `10-memory-profiling.md` §3 | 20 min |
| 4 | Case 2: Tracking memory growth over a run — `tracemalloc` snapshots and loop | `10-memory-profiling.md` §4 | 20 min |
| 5 | Case 3: Catching unbounded accumulation — `objgraph.show_growth()`, reference chains | `10-memory-profiling.md` §5 | 20 min |
| 6 | Doubling test for space complexity — memory ratio table, setup, reading the ratio column | `10-memory-profiling.md` §6 | 15 min |
| 7 | Output reading strategy — the five-step decision order | `10-memory-profiling.md` §7 | 10 min |
| 8 | End-of-session test — four questions | `10-memory-profiling.md` §8 | 15 min |

---

## 4. Test Bank Pattern

The four-question format from Session 2's end-of-session test worked well — reuse it for
every session going forward:

1. **Identify complexity** — given code, derive f(n) then simplify to a Big O class
2. **Fix the code** — given an inefficient implementation, rewrite to a better complexity
3. **Real scenario** — given a production problem description, choose the right data
   structure/strategy and justify it
4. **Tricky statement** — given a colleague's claim, identify what's correct and what's
   missing

This reliably covers recognition, application, production judgment, and edge-case
awareness in one pass.
