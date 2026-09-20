# Profiling — Reading the Constants Behind Big O

> **Status: stub.** Parked during teaching until the 7 complexity folders and
> `capstone.md` are fully covered — see `progress.md` for why and when this gets filled
> in. Section 1 below is safe to read any time; sections 2-4 are placeholders until the
> dedicated session.

`schema.md` (Part 4) covers why this is sequenced last: profiling only means something
once you already have the vocabulary to interpret what its numbers are telling you.

---

## 1. What Profiling Measures, and How It Differs From Big O

Big O and profiling answer two different questions, and it's worth being precise about
which one you're asking:

```
Big O       → the shape of the growth curve (how does cost scale as n grows?)
Profiling   → the actual constants inside that shape, for one specific run
              (where is the time actually going, right now, on this hardware?)
```

Neither replaces the other. Big O tells you an algorithm is O(n²) — it does not tell you
whether that O(n²) job takes 4 milliseconds or 4 hours; that depends on the constant
factor, and the constant factor is exactly what `concept.md` §1 said Big O deliberately
throws away. Profiling is how you recover it: it measures real elapsed time (or calls,
or memory) for a real execution, function by function.

This is also why profiling comes *after* the complexity vocabulary, not before: a
profiler will happily tell you "this function took 40% of total runtime" — but knowing
whether that's a problem, and what to do about it, requires knowing whether that
function's cost is O(1) per call (so 40% just means it's called a lot, which might be
fine) or O(n²) per call (so 40% means it's the actual bottleneck that will get worse as
data grows). The number alone doesn't tell you which; the complexity class does.

A useful frame carried over from `concept.md` §3's benchmark-doubling technique: a
doubling test tells you *which complexity class* a black-box operation belongs to;
profiling tells you *where inside that operation* the time is actually spent. They're
complementary diagnostics, run in that order.

---

## 2. Reading `cProfile` Output

*(To be filled in during the dedicated profiling session — see `progress.md` Session 9.)*

Will cover: the `ncalls` / `tottime` / `cumtime` columns and what each one actually
answers, how to spot a function that's expensive per-call versus one that's merely
called from everywhere (high `cumtime`, low `tottime`), and a worked example profiling
one of the `example.py` benchmarks already written in the 7 complexity folders.

## 3. Reading a Spark Execution Plan

*(To be filled in during the dedicated profiling session.)*

Will cover: `df.explain()` output, how a physical plan's stages (scan, shuffle, sort,
join strategy) map back to the join and sort strategies already covered in
`03-On-linear`, `04-Onlogn-linearithmic`, and `capstone.md` §3 — i.e. how to look at a
real query plan and identify which side of the hash-join-vs-sort-merge-join tradeoff
Spark's planner actually chose, and why.

## 4. Mapping Profiling Results Back to Big O Complexity Classes

*(To be filled in during the dedicated profiling session.)*

Will cover: given a profiled function's timings across a few different input sizes, how
to recognize which complexity-class growth pattern the numbers actually match (tying
back to `concept.md` §3's doubling-test table), and what to do when the observed pattern
*doesn't* match what the code should theoretically be doing — usually the more useful
signal, since it means something other than the "obvious" algorithm is dominating the
cost.
