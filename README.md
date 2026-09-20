# Big O Notation for Data Engineers

A structured self-study repository for learning time and space complexity through real-world data engineering examples — hash joins in Spark, streaming deduplication, Redis lookups, Kafka partition strategies, and more.

This is not a textbook summary. Every complexity class is grounded in production scenarios, with mathematical derivations, runnable benchmark code, and a capstone decision framework you can actually use when designing pipelines.

---

## What This Repo Covers

Seven complexity classes, each in its own folder, plus root-level files that tie everything together:

| Folder | Notation | Name |
|---|---|---|
| `01-O1-constant` | O(1) | Constant |
| `02-Ologn-logarithmic` | O(log n) | Logarithmic |
| `03-On-linear` | O(n) | Linear |
| `04-Onlogn-linearithmic` | O(n log n) | Linearithmic |
| `05-On2-quadratic` | O(n²) | Quadratic |
| `06-O2n-exponential` | O(2ⁿ) | Exponential |
| `07-Onfactorial-factorial` | O(n!) | Factorial |

Each folder contains five files:

- **`overview.md`** — Mathematical definition, derivation walkthrough, growth curve chart, and a plain-English analogy
- **`space-complexity.md`** — Memory cost, auxiliary vs. total space, amortized behavior where relevant, and worst-case deviations
- **`de-application.md`** — Where this complexity shows up in real DE work (Spark, Kafka, Hadoop, pandas, Postgres, Redis, etc.), with code samples
- **`algorithms.md`** — Key algorithms at this complexity class, with explanations and LeetCode pattern callouts
- **`example.py`** — Runnable benchmark that prints a timing table across increasing `n`, so you can see the doubling signature with your own eyes

Root-level files:

| File | Purpose |
|---|---|
| `concept.md` | Foundational primer — read this first. Covers Big O vs Θ vs Ω, time vs. space, amortized cost, multi-variable complexity, and notation |
| `capstone.md` | Cross-complexity synthesis — all 7 classes compared side-by-side, time/space tradeoff pairs, and a decision framework for real constraints |
| `09-time-profiling.md` | How to profile Python and Spark and map the results back to Big O classes |
| `10-memory-profiling.md` | Memory profiling — identifying auxiliary space costs in practice |
| `schema.md` | The structural template used to author all files in this repo |
| `progress.md` | Session log for this learner — not core content |

---

## Who This Is For

Junior-to-mid data engineers who want to move beyond "I know O(n²) is bad" toward genuine, mathematically grounded judgment about when a given complexity class is acceptable and when it will cause a production incident.

---

## How to Use This With an AI Tutor (Recommended)

This repo is designed to be uploaded as the knowledge base for a RAG-based AI tutor session — [NotebookLM](https://notebooklm.google.com/), [Claude Projects](https://claude.ai/), or any equivalent tool that lets you attach source documents.

### Step 1 — Upload the files

Upload all files from this repository. The files are named with their folder prefix (e.g. `01-O1-constant-overview.md`) so they remain self-describing even when flattened out of their folder structure.

**Recommended upload order** (matches the intended reading path):

1. `concept.md`
2. All files inside `01-O1-constant/` through `07-Onfactorial-factorial/` (in numeric order)
3. `capstone.md`
4. `09-time-profiling.md` and `10-memory-profiling.md`
5. `schema.md` (optional — gives the AI structural context)

### Step 2 — Start a new session with this system prompt

Paste the following at the start of your conversation:

```
You are a senior data engineer with deep expertise in time and space complexity, mathematics, and production-scale real-time data processing. You are here to help a junior data engineer build genuine, evidence-based judgment for optimising code for efficiency and scalability.

Teach from the provided source material, but always add your own explanation — do not simply copy text from the documents. Use clear examples, including detailed mathematical derivations, real data engineering scenarios, and visualisations of how code relates to the underlying math.

Each session should focus on one complexity class (unless comparison is explicitly needed). If the conversation drifts, bring the junior back to the current topic. Never present all information at once — make one point at a time, and confirm understanding before moving on. End each topic with a short test to verify comprehension.

The explanation style should be thorough and detailed.
```

### Step 3 — Pick a starting point

Tell the tutor which complexity class or topic you want to cover. Some options:

- **Start from scratch:** `"Let's begin with concept.md — walk me through what Big O notation actually is."`
- **Jump to a class:** `"Take me through O(log n) — I want to understand where it shows up in real data pipelines."`
- **Focus on a decision:** `"I'm designing a join between a 10 TB fact table and a 5 GB dimension table. Help me think through the complexity tradeoffs."`
- **Run a benchmark session:** `"Let's go through the example.py for O(n²) together — I want to understand the doubling signature."`

### Step 4 — Work through the material one point at a time

The tutor is instructed to wait for your confirmation before moving on. Push back, ask for re-explanation, or ask for a different example — the material is dense enough that passive reading rarely leads to durable understanding.

### Step 5 — Take the end-of-topic test

Each complexity class ends with a short test. Don't skip it — the test surfaces gaps that feel invisible during explanation.

---

## Suggested Learning Path

```
concept.md                        ← Start here. Always.
    ↓
01-O1-constant/                   ← Easiest class; introduces benchmarking and amortized cost
    ↓
02-Ologn-logarithmic/             ← Where indexes, binary search, and partition pruning live
    ↓
03-On-linear/                     ← The baseline most DE operations aim for
    ↓
04-Onlogn-linearithmic/           ← Sort-based joins, shuffle cost, merge sort
    ↓
05-On2-quadratic/                 ← The class most naive DE code accidentally produces
    ↓
06-O2n-exponential/               ← Combinatorial problems; knowing when to stop
    ↓
07-Onfactorial-factorial/         ← Permutation problems; why brute force is never an option at scale
    ↓
capstone.md                       ← The decision framework; read after all 7 folders
    ↓
09-time-profiling.md              ← Profiling: connecting Big O theory to real execution numbers
10-memory-profiling.md            ← Memory profiling in Python and Spark
```

---

## What to Expect

By the end of this path, you should be able to:

- **Derive** the time and space complexity of a piece of code from first principles — not just recognise the pattern, but show the work
- **Read a Spark execution plan** and identify which stage is the bottleneck and why
- **Make a principled choice** between two strategies (e.g. hash join vs. sort-merge join, exact count vs. HyperLogLog) given real constraints like memory budget and latency SLA
- **Identify common mistakes** — accidentally O(n²) loops, string concatenation in hot paths, rebuilding structures that should be long-lived — and explain exactly why they're expensive
- **Apply the doubling test** to black-box systems or third-party libraries to infer their complexity from timing data alone

---

## Running the Benchmark Scripts

Each complexity folder includes an `example.py`. Run any of them directly:

```bash
python 01-O1-constant/01-O1-constant-example.py
```

Each script prints a timing comparison table across increasing `n` values. The ratio column shows the doubling signature — the specific multiplier you should expect when `n` doubles for that complexity class. No setup required beyond a standard Python 3 environment.

---

## Repository Structure at a Glance

```
big-o-notation-for-data-engineering/
├── README.md
├── concept.md                          ← Foundational primer (read first)
├── schema.md                           ← File/content template
├── capstone.md                         ← Cross-complexity decision framework
├── 09-time-profiling.md
├── 10-memory-profiling.md
├── progress.md                         ← Session log (not core content)
├── 01-O1-constant/
│   ├── 01-O1-constant-overview.md
│   ├── 01-O1-constant-space-complexity.md
│   ├── 01-O1-constant-de-application.md
│   ├── 01-O1-constant-algorithms.md
│   └── 01-O1-constant-example.py
├── 02-Ologn-logarithmic/
│   └── ... (same 5-file structure)
├── 03-On-linear/
├── 04-Onlogn-linearithmic/
├── 05-On2-quadratic/
├── 06-O2n-exponential/
└── 07-Onfactorial-factorial/
```
