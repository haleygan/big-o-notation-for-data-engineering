# O(2ⁿ) — Space Complexity

## Typical Space Cost

Here's the gotcha that makes this class worth its own careful read: **time and space diverge
harder in O(2ⁿ) algorithms than almost anywhere else in this path.**

- **Naive recursive Fibonacci** costs `O(2ⁿ)` time (loose bound; tight bound `Θ(φⁿ)`, per
  `overview.md`) but only **`O(n)` auxiliary space**. Why: recursion is depth-first. At any
  single instant, only one root-to-leaf path sits on the call stack — the stack frame for
  `fib(n)` calls `fib(n-1)`, which calls `fib(n-2)`, ... down to the base case, and that chain
  is at most `n` frames deep. Once a branch returns, its stack frame is popped and reused for
  the next branch. The *time* cost balloons because the same sub-problems get **revisited**
  or the call tree branches; the *space* cost doesn't, because revisits never happen
  **simultaneously** — they happen one after another, and the stack only ever holds one path
  at a time (concept.md §4's auxiliary space idea: the recursion stack is the extra memory
  beyond the input here).
- **Power set / subset generation** is more nuanced, because it depends on what you *do* with
  the output:
  - If you need all `2ⁿ` subsets materialized at once (e.g. return one big list of lists),
    that's **`O(n·2ⁿ)`** space — `2ⁿ` subsets, up to `n` elements each.
  - If you only need to *visit* each subset once and can discard it immediately (a generator
    that `yield`s one subset at a time, or a callback-style walk), auxiliary space collapses
    back down to **`O(n)`** — just the recursion depth / bitmask counter — even though total
    *time* is still `Θ(2ⁿ)`, because you still have to visit every subset once. This is a
    genuinely useful pattern at DE scale: never materialize a combinatorial result set you
    don't have to hold in memory all at once. Stream it.

## Amortized Behavior

Concept.md §5's amortized story (dynamic array doubling, hash table resize) doesn't really
apply here, and it's worth being explicit about *why not*, rather than force-fitting it.
Amortized analysis is about a **sequence of operations reusing the same structure over time** —
most operations are cheap, occasionally one is expensive, and averaged over the whole sequence
it comes out cheap. Naive exponential recursion isn't shaped like that at all: every one of the
`~2ⁿ` calls does a uniformly small, cheap unit of work (one comparison, one addition, two
recursive dispatches). Nothing is "occasionally expensive" — the total is expensive purely
because there are exponentially *many* cheap calls, not because a few individual ones are slow.
There's no sequence to average over; there's just a lot of redundant work. So "amortized
O(2ⁿ)" isn't a meaningful thing to say — it's just `Θ(φⁿ)`, plainly, every time.

(If you want the closest thing to an amortized-flavored story in this territory, it's
memoization below — trading space so each distinct sub-problem is paid for exactly once,
instead of every time it's re-encountered.)

## Local Time/Space Tradeoff

This is the main event for this folder: the same problem, naive Fibonacci vs. memoized
Fibonacci, sitting at two different points on the time/space curve.

| Approach | Time | Space | What changed |
|---|---|---|---|
| Naive recursive | `O(2ⁿ)` (tight: `Θ(φⁿ)`) | `O(n)` | No memory of past calls — every sub-problem re-solved from scratch, every time it's hit |
| Memoized (top-down, dict cache) | `O(n)` | `O(n)` | Each of the `n` distinct sub-problems (`fib(0)` … `fib(n)`) solved once, cached, reused |
| Tabulated (bottom-up, array) | `O(n)` | `O(n)` | Same idea, iterative — build the array up from `fib(0)` |
| Tabulated, rolling variables | `O(n)` | `O(1)` | Fibonacci only ever needs its *last two* values — special to this recurrence's shape |

Why memoization works: there are only `n` **distinct** sub-problems in `fib(n)` — `fib(0)`
through `fib(n)`. Naive recursion doesn't know that; it treats `fib(k)` as a brand-new problem
every single time it's requested, no matter how many times before. Memoization is just: the
first time you solve `fib(k)`, write the answer down (a `dict` or array — concept.md §4 literally
lists "a hash map" as its example of auxiliary space); every subsequent request for `fib(k)`
becomes an `O(1)` lookup instead of a fresh sub-recursion. With `n` distinct sub-problems at
`O(1)` marginal cost each (once their own recursive dependencies resolve), total time collapses
from exponential to linear — you drop a **full complexity class** by paying for an `O(n)` cache
you didn't need before.

That's the trade, stated plainly: **you deliberately spend O(n) space you weren't spending, to
buy back an entire time-complexity class.** This is one of the highest-leverage trades in all of
computer science, and it's why "should I cache this?" is often the right first question when a
recursive solution feels too slow — not "can I make the recursion cleverer," but "am I solving
the same sub-problem more than once, and can I afford to remember the answer?"

One more layer, specific to Fibonacci: because `fib(n)` only ever depends on its immediate two
predecessors (`fib(n-1)` and `fib(n-2)`), you can go further and drop space to `O(1)` by keeping
just the last two running values instead of a full `n`-sized cache. That squeeze is special to
*this* recurrence's shape, though — it doesn't generalize. A recursion like edit-distance or
0/1 knapsack needs its *entire* table of prior sub-results (not just "the last two"), so those
stay at `O(n)` or `O(n·m)` space even after memoizing. Don't walk away assuming every memoized
recursion can be squeezed to `O(1)` — Fibonacci is the easy case.

## Worst-Case Space Deviation

No deviation here, and that's worth calling out as its own small lesson. Naive Fibonacci's
recursion always walks straight down through `fib(n-1)` calls to the base case, so stack depth
is *exactly* `n` for any input of size n — there's no numeric input value that pushes it deeper
or shallower, unlike quicksort's recursion stack (05-On2-quadratic), which degrades from
`O(log n)` average depth to `O(n)` worst-case depth on adversarial pivots. Same story for
recursive power-set generation: depth is always `O(n)`, one stack frame per element decided.

The one place space genuinely *can* blow up unexpectedly in this class isn't an adversarial
input at all — it's the materialization choice from the section above. Forgetting to stream
subsets and instead collecting all `2ⁿ` of them into one in-memory list is the practical
"worst case" here, and it's a design decision, not something the data forced on you.

## Cross-Link

See root `capstone.md` for how this class's time/space profile — including the memoization
trade above — lines up against the other 6 classes, and where "spend space to drop a
complexity class" shows up again as a general strategy-picking pattern.
