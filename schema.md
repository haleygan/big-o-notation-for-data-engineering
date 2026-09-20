# Schema: Big O Notation Learning Materials

This file defines the folder/file structure and the expected content sections for each
file, so Part 1 (`concept.md`), Part 2 (per-folder files), Part 3 (`capstone.md`), and
Part 4 (`profiling.md`) stay consistent without re-deriving structure each time.

## Root-level files vs. per-complexity folders

```
Big O Notation/
├── schema.md                          (this file)
├── concept.md                         (foundational primer — Part 1)
├── capstone.md                        (cross-complexity comparison — Part 3)
├── 09-time-profiling.md               (post-capstone applied topics — Part 4)
├── 10-memory-profiling.md             (post-capstone applied topics — Part 4)
├── progress.md                        (this learner's session log + plan, not core content)
├── 01-O1-constant/
│   ├── 01-O1-constant-overview.md
│   ├── 01-O1-constant-space-complexity.md
│   ├── 01-O1-constant-de-application.md
│   ├── 01-O1-constant-algorithms.md
│   └── 01-O1-constant-example.py
├── 02-Ologn-logarithmic/
│   ├── 02-Ologn-logarithmic-overview.md
│   ├── 02-Ologn-logarithmic-space-complexity.md
│   ├── 02-Ologn-logarithmic-de-application.md
│   ├── 02-Ologn-logarithmic-algorithms.md
│   └── 02-Ologn-logarithmic-example.py
├── 03-On-linear/
│   ├── 03-On-linear-overview.md
│   ├── 03-On-linear-space-complexity.md
│   ├── 03-On-linear-de-application.md
│   ├── 03-On-linear-algorithms.md
│   └── 03-On-linear-example.py
├── 04-Onlogn-linearithmic/
│   ├── 04-Onlogn-linearithmic-overview.md
│   ├── 04-Onlogn-linearithmic-space-complexity.md
│   ├── 04-Onlogn-linearithmic-de-application.md
│   ├── 04-Onlogn-linearithmic-algorithms.md
│   └── 04-Onlogn-linearithmic-example.py
├── 05-On2-quadratic/
│   ├── 05-On2-quadratic-overview.md
│   ├── 05-On2-quadratic-space-complexity.md
│   ├── 05-On2-quadratic-de-application.md
│   ├── 05-On2-quadratic-algorithms.md
│   └── 05-On2-quadratic-example.py
├── 06-O2n-exponential/
│   ├── 06-O2n-exponential-overview.md
│   ├── 06-O2n-exponential-space-complexity.md
│   ├── 06-O2n-exponential-de-application.md
│   ├── 06-O2n-exponential-algorithms.md
│   └── 06-O2n-exponential-example.py
└── 07-Onfactorial-factorial/
    ├── 07-Onfactorial-factorial-overview.md
    ├── 07-Onfactorial-factorial-space-complexity.md
    ├── 07-Onfactorial-factorial-de-application.md
    ├── 07-Onfactorial-factorial-algorithms.md
    └── 07-Onfactorial-factorial-example.py
```

Files inside each complexity folder carry a `<folder-name>-` prefix (e.g.
`01-O1-constant-overview.md`) rather than a bare name (`overview.md`). This is so each
file stays self-describing once flattened out of its folder — e.g. uploaded individually
into a RAG/knowledge-base tool that doesn't preserve directory structure.

| Folder | Notation | Name |
|---|---|---|
| `01-O1-constant` | O(1) | Constant |
| `02-Ologn-logarithmic` | O(log n) | Logarithmic |
| `03-On-linear` | O(n) | Linear |
| `04-Onlogn-linearithmic` | O(n log n) | Linearithmic |
| `05-On2-quadratic` | O(n²) | Quadratic |
| `06-O2n-exponential` | O(2ⁿ) | Exponential |
| `07-Onfactorial-factorial` | O(n!) | Factorial |

## Why the split

Each complexity folder has 5 focused files instead of 3 catch-all ones:

- `overview.md` — pure conceptual intuition for this class (math + derivation + graph +
  layman example)
- `space-complexity.md` — the memory side, given real room instead of a single bullet
- `de-application.md` — the "where this shows up in real DE work" side
- `algorithms.md` / `example.py` — unchanged

The general formalism — what Big O/Θ/Ω actually mean, what amortized means, what
auxiliary space means, how multi-variable complexity works — lives once in `concept.md`.
Per-folder files *apply* the concept to that specific class; they don't re-teach it.
If a per-folder file catches itself re-explaining a general concept from scratch, that's
a sign it should link to `concept.md` instead.

## File content schema

### 0. `concept.md` (root level — Part 1, foundational, written before Part 2)

The primer everything else assumes has been read. Written once, directly, not
parallelized — later files reference it by name, so it must exist and be stable first.

1. **What Big O notation actually is** — formal definition, asymptotic upper bound, the
   "drop constants and lower-order terms" rule and why that's valid (numeric example of
   why the constant stops mattering at large n)
2. **Big O vs Θ vs Ω** — upper bound / tight bound / lower bound, mapped to
   worst-case / average-case / best-case; note where colloquial usage ("this is O(n)")
   is really claiming Θ(n)
3. **Time complexity** — what "time" means here (operation counts, not wall-clock), the
   general method for deriving it from code (identify the basic operation, count
   relative to input size n, simplify to the dominant term)
4. **Space complexity** — auxiliary space vs. total space, in-place vs. extra structure,
   derived the same way as time complexity
5. **Amortized complexity** — why a sequence of operations can have a good average cost
   even when one operation in the sequence is expensive (this is distinct from
   average-case — amortized is about a sequence on the same structure, not about typical
   input shape). Canonical example: dynamic array / list doubling, walked through
   aggregate-method style (sum the resize costs across a sequence of n appends, show it
   totals O(n), so it's O(1) per append on average). Second example: hash table resize
6. **Multi-variable complexity** — when input isn't one `n` (e.g. joining dataset A of
   size `n` against dataset B of size `m` → nested-loop O(n·m), hash join O(n+m), sort-
   merge O(n log n + m log m)); flag this early since DE problems are rarely
   single-input and O(n·m) vs O(n+m) behave very differently when one side is huge and
   the other tiny
7. **Notation cheat sheet** — quick table: symbol, name, meaning, example
8. **Why this matters for choosing a data processing strategy** — ties back to the
   path's stated goal; previews the rest of the path (7 complexity folders + capstone)

### 1. `overview.md`

1. **Header** — complexity notation + name (e.g. `# O(n) — Linear Time`)
2. **Mathematical definition** — the class-specific formal complexity and growth curve
   behavior as n → ∞. Apply (don't re-teach — link to `concept.md` §2) the Big O vs Θ vs
   Ω distinction to this class's canonical algorithm(s): what the worst/average/best
   case actually is, and one concrete input shape that pushes it off its typical case
   (e.g. quicksort degrading to O(n²) on sorted/adversarial input, hash lookups
   degrading on collisions)
3. **Derivation walkthrough** — step-by-step: start from a code loop/algorithm, count
   operations, simplify to the Big O term
4. **Visual graph** — growth curve chart (mermaid `xychart-beta` or ASCII plot) comparing
   this complexity against neighboring ones on the same axes
5. **Layman explanation** — plain-English analogy using a simple file example (e.g.
   searching/reading/sorting lines in a text file)

### 2. `space-complexity.md`

1. **Header** — e.g. `# O(n) — Space Complexity`
2. **Typical space cost** — the O() memory cost of the canonical approach(es) in this
   class: in-place vs. needing an extra structure, and why
3. **Amortized behavior** (only where actually relevant to this class's canonical
   structure — e.g. dynamic array doubling and hash table resize belong in
   `01-O1-constant`) — apply `concept.md` §5's general explanation to this specific
   structure; don't re-derive the general concept here
4. **Local time/space tradeoff** — within this same complexity class, is there a variant
   that trades more memory for better time, or vice versa?
5. **Worst-case space deviation** (where relevant) — does the space cost degrade on the
   same adversarial input that degrades time (e.g. quicksort's recursion stack going
   from O(log n) average to O(n) worst-case on bad pivots)? Tie this back to the
   worst-case note in `overview.md` §2 — same root cause, two symptoms
6. **Cross-link** — one line pointing to root `capstone.md` for how this class's
   time/space profile compares against the other 6

### 3. `de-application.md`

1. **Header** — e.g. `# O(n) — In Data Engineering`
2. **DE technology examples** — table: `Technology | Operation | Why this complexity |
   Minimal code sample`. Mix modern + old (Kafka, Spark, Hadoop, pandas, Java
   collections, Postgres indexes, etc.), one short code snippet per row
3. **Where it naturally emerges** — realistic data engineering scenarios/pipelines that
   land on this complexity by default
4. **Common mistakes → exceptions** (only meaningful for O(n²) and worse) — what design
   mistake typically produces this complexity, and when it's still an acceptable
   tradeoff (e.g. small bounded n, one-off batch job)

### 4. `algorithms.md`

1. **Algorithm index** — bullet list: algorithm name + one-line description, all
   algorithms in this file that achieve/relate to this complexity
2. For **each algorithm**:
   - Background/context (what problem it solves, why it exists)
   - Code sample with inline/below walkthrough (line-by-line or block-by-block)
   - Reference link (docs, paper, Wikipedia, or canonical source) if one exists
3. **LeetCode pattern callout** — pattern name (e.g. two-pointer, sliding window,
   divide-and-conquer), how to recognize it in a problem statement, 2-3 example problem
   names/types that use this pattern at this complexity

### 5. `example.py`

1. Imports + timing utility (`time` or `timeit`)
2. Function implementing *this* complexity for a given problem
3. Function implementing a contrasting/better complexity for the *same* problem
4. Benchmark loop across increasing `n`, printing a timing comparison table
5. Short comment block summarizing the takeaway (when the gap starts to matter)

### 6. `capstone.md` (root level, not inside a subfolder — Part 3)

Written after all 7 subfolders exist, since it synthesizes them rather than introducing
new material. This is the "how do I actually decide" file the whole learning path builds
toward. Reads each folder's `space-complexity.md` (not `overview.md`) for the space side.

1. **Master comparison table** — all 7 complexities as rows: notation, name, typical time
   growth, typical space growth, canonical algorithm(s), one representative DE technology
2. **Combined growth chart** — all 7 curves plotted together (mermaid `xychart-beta` or
   ASCII), so the gap between classes is visible at a glance rather than inferred across
   7 separate files
3. **Time/space tradeoff, cross-class** — the core section. Concrete DE-relevant pairs,
   each showing the same problem solved two ways at a different point on the time/space
   curve, and *why* a real system picks one over the other:
   - hash join (O(n) time, O(n) extra space) vs. sort-merge join (O(n log n) time, ~O(1)
     extra space) — why Spark chooses based on whether the smaller side fits in memory
   - exact distinct count (O(n) space) vs. approximate sketch like HyperLogLog (O(1)
     space, small accuracy loss) — why streaming systems default to the latter at scale
   - in-place sort — quicksort's O(log n) recursion-stack space is the *average* case;
     on adversarial pivots it degrades to O(n) stack depth, same root cause as its
     O(n²) worst-case time (see `05-On2-quadratic/05-On2-quadratic-space-complexity.md`) — vs. merge
     sort's guaranteed O(n) space regardless of input. Frame as "average-case-efficient
     but no guarantee" vs. "worse average, but a hard ceiling"
   - memoization/caching — deliberately spending O(n) space to pull an algorithm down a
     time class
   (agent may add more pairs if a clearer DE example exists; keep each pair concrete and
   code-free — this file is decision-level, not implementation-level, so it cross-links
   the code details rather than repeating them)
4. **Decision framework** — a checklist or decision tree: given constraints (data volume,
   memory budget, latency SLA, batch vs. streaming, single-node vs. distributed), what
   complexity target should you aim for and what does that rule out
5. **Common strategy-picking pitfalls** — e.g. optimizing time complexity while ignoring
   a memory budget that will OOM in production; over-engineering a low-complexity
   solution for an n that will never be large enough to matter

### 7. `09-time-profiling.md` and `10-memory-profiling.md` (root level — Part 4, post-capstone applied topics)

Not part of the core 3-part arc. Parked deliberately: profiling only means something
once the reader already has the Big O vocabulary to interpret what a profiler's numbers
*mean* — it gives you the exact constants behind a complexity class, not the complexity
class itself. Written after `capstone.md`, once the 7 folders and the decision framework
are already in place.

1. **What profiling measures, and how it differs from Big O** — Big O is the shape of
   the growth curve; profiling gives the actual constants inside that shape for a
   specific run on specific hardware. Neither replaces the other: Big O tells you how a
   cost scales, profiling tells you where the time is actually going right now.
2. **Reading `cProfile` output** — what the columns mean (`ncalls`, `tottime`,
   `cumtime`), how to spot the function actually worth optimizing vs. one that's just
   called from everywhere
3. **Reading a Spark execution plan** — `explain()` output, how a DAG of stages maps
   back to the join/sort/shuffle strategies covered across the 7 folders and
   `capstone.md`
4. **Mapping profiling results back to Big O complexity classes** — given a profile
   showing time growing with input size, which complexity class does the growth pattern
   match, and does that match what the code *should* be doing

## Non-goals

This schema only prescribes structure. It does not contain the actual explanations —
`concept.md` is written in Part 1, the per-folder files in Part 2, and the cross-class
synthesis in `capstone.md` in Part 3, all using this schema as the template.

Profiling is explicitly out of scope for Parts 1-3. It depends on the reader already
having the full Big O vocabulary (`concept.md`) and the cross-class decision framework
(`capstone.md`) to be useful — introducing it earlier would mean explaining "here's a
number, but you don't yet have the framework to know if it's good or bad." It's covered
separately in Part 4 (`profiling.md`, item 7 above).
