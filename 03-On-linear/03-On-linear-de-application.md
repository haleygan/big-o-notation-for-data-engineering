# O(n) — In Data Engineering

Linear time is the workhorse complexity of data engineering. Most pipelines, at their
core, are "touch every record once" — the question is rarely "can I avoid this," it's
"am I paying O(n) once, or accidentally paying it n times over" (more on that in §3).

## 1. DE Technology Examples

| Technology | Operation | Why this complexity | Minimal code sample |
|---|---|---|---|
| Kafka | Consumer draining a partition | Every message must be delivered to the consumer exactly once — no shortcut, no early exit | `for msg in consumer: process(msg)` |
| Spark | `.map()` / full-column transform over a DataFrame | One operation applied per row, independent of the others | `df.withColumn("upper", upper(col("name")))` |
| pandas | `.apply()` / column-wide aggregation | Visits every row once to transform or reduce | `df["total"] = df["amount"].apply(add_tax)` |
| Postgres | Sequential scan (`Seq Scan`) | No usable index — the planner must read every row/page to find matches | `EXPLAIN SELECT * FROM orders WHERE lower(email) = 'a@b.com';` |
| Python (builtin) | `x in list`, `sum(list)` | Under the hood, a linear scan through the underlying array | `found = target in my_list` |
| DuckDB / Spark / Postgres | Hash join build + probe phase | Building the hash side is O(n), probing is O(m) — additive, not multiplicative | `SELECT * FROM a JOIN b ON a.key = b.key;` (planner picks Hash Join) |
| Hadoop MapReduce | Map phase | Each input record is transformed independently, once, by a mapper | `map(record) -> emit(key, value)` |

## 2. Where It Naturally Emerges

- **Full table scans.** No usable index, or the query wraps the column in a function
  (`WHERE lower(email) = ...`) or does a leading-wildcard `LIKE '%foo'` — the planner
  can't binary-search an index, so it reads every row.
- **Log / event processing.** Parsing, validating, and enriching each line or message —
  a classic ETL row-by-row transform, whether it's a Spark job, a Kafka Streams
  application, or a plain Python script over a file.
- **Streaming consumers.** Anything that must process every event exactly once (Kafka,
  Kinesis, Pub/Sub) is linear by construction — you can't "skip ahead" in an event stream
  without losing data.
- **Deduplication.** Scanning a batch or stream once while checking membership in a hash
  set — O(n) time, and (per `space-complexity.md`) O(n) auxiliary space for the set
  itself.
- **Cache/index warm-up.** Iterating every row once to populate a lookup structure
  (building a hash map, priming an in-memory cache) before serving lookups against it.
- **Hash join build phase.** Any join strategy where the engine builds a hash table over
  one side of the join before probing — the build phase alone is linear in that side's
  size.

## 3. A Note Instead Of "Common Mistakes"

The schema's "common mistakes → exceptions" section is mainly about complexities *worse*
than this one (O(n²) and up) — where a design mistake produces the bad complexity in the
first place. O(n) is usually the thing you *want*: it's the honest, unavoidable cost of
touching every record once.

The practical trap that belongs here isn't "using O(n)" — it's **accidentally paying for
it more than once**. A single linear scan is fine. A linear scan *called from inside
another loop* — checking `if row in some_list` (O(n) membership check on a plain list)
once per row of a different table — silently turns an O(n) operation into O(n²) without
anyone writing a nested loop on purpose. That's the actual failure mode to watch for in
review: an innocent-looking `in` check, `.index()` call, or repeated `.apply()` inside a
loop, each cheap in isolation, adding up because it's re-run n times. See
`05-On2-quadratic/05-On2-quadratic-de-application.md` for the full writeup of that mistake and when it's
still an acceptable tradeoff (small, bounded n).
