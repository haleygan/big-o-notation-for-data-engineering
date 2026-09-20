"""
O(n!) — Factorial Time
Brute-force Traveling Salesman Problem (try every permutation of a route)
vs. the Nearest-Neighbor heuristic (greedy, O(n^2)) on the same problem.

Keep n tiny here on purpose: 10! = 3,628,800 and 15! is already past a
trillion. This is the one complexity class where "just add a zero to n"
turns a instant benchmark into a benchmark that will not finish this year.
"""

import itertools
import math
import random
import time


# --- 1. Setup: build a small random "map" of cities ------------------------

def build_distance_matrix(n: int, seed: int = 42) -> list[list[float]]:
    """Return an n x n symmetric distance matrix for n random 2D points."""
    rng = random.Random(seed)
    points = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(n)]
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                dist[i][j] = math.hypot(dx, dy)
    return dist


def tour_length(tour: tuple[int, ...] | list[int], dist: list[list[float]]) -> float:
    """Total distance of a closed loop that visits every city once."""
    total = 0.0
    n = len(tour)
    for i in range(n):
        a, b = tour[i], tour[(i + 1) % n]
        total += dist[a][b]
    return total


# --- 2. The O(n!) approach: brute-force TSP --------------------------------

def brute_force_tsp(dist: list[list[float]]) -> tuple[tuple[int, ...], float]:
    """
    Exact optimal tour, found by trying every possible ordering.

    A tour and all of its rotations describe the same physical loop, so we
    fix city 0 as the start and only permute the remaining n-1 cities.
    That's (n-1)! candidates instead of n!, but it is still factorial —
    dropping a constant-ish factor of n doesn't change the growth class,
    same "napkin method" reasoning as concept.md section 1.
    """
    n = len(dist)
    remaining = list(range(1, n))
    best_tour: tuple[int, ...] | None = None
    best_length = math.inf

    for perm in itertools.permutations(remaining):
        candidate = (0,) + perm
        length = tour_length(candidate, dist)
        if length < best_length:
            best_length = length
            best_tour = candidate

    assert best_tour is not None
    return best_tour, best_length


# --- 3. The smarter approach: nearest-neighbor heuristic, O(n^2) ----------

def nearest_neighbor_tsp(dist: list[list[float]]) -> tuple[list[int], float]:
    """
    Greedy approximation: from the current city, always hop to the closest
    unvisited city. Not guaranteed optimal, but it scales to thousands of
    cities where brute force could never finish, and in practice it lands
    within a small percentage of the true optimum.
    """
    n = len(dist)
    unvisited = set(range(1, n))
    tour = [0]
    current = 0

    while unvisited:
        nxt = min(unvisited, key=lambda city: dist[current][city])
        tour.append(nxt)
        unvisited.remove(nxt)
        current = nxt

    return tour, tour_length(tour, dist)


# --- 4. Benchmark: same problem, two complexity classes --------------------

def benchmark() -> None:
    header = (
        f"{'n':>3} | {'brute force O(n!)':>18} | {'nearest neighbor O(n^2)':>24} "
        f"| {'bf tour len':>12} | {'nn tour len':>12} | {'nn gap':>7}"
    )
    print(header)
    print("-" * len(header))

    for n in range(4, 11):  # stop at 10 -- 9! = 362,880 already takes a beat
        dist = build_distance_matrix(n)

        start = time.perf_counter()
        _, bf_length = brute_force_tsp(dist)
        bf_time = time.perf_counter() - start

        start = time.perf_counter()
        _, nn_length = nearest_neighbor_tsp(dist)
        nn_time = time.perf_counter() - start

        gap_pct = (nn_length - bf_length) / bf_length * 100

        print(
            f"{n:>3} | {bf_time:>15.6f}s  | {nn_time:>21.6f}s  "
            f"| {bf_length:>12.2f} | {nn_length:>12.2f} | {gap_pct:>6.1f}%"
        )


if __name__ == "__main__":
    benchmark()


# --- 5. Takeaway ------------------------------------------------------------
#
# The brute-force column grows so fast it stops being a smooth curve and
# starts looking like a step function: n=8 to n=9 alone multiplies the
# permutation count by 9x, n=9 to n=10 multiplies it by another 10x. By
# n=10 brute force is already doing ~362,880 full tour evaluations for a
# problem nearest-neighbor solves in ~10 comparisons.
#
# The nearest-neighbor tour is usually only a few percent longer than the
# true optimum (see the "nn gap" column) -- and it would still finish in
# milliseconds at n=1,000, a size where brute force is not "slow," it is
# physically impossible to complete before the heat death of anything.
# That gap is the entire reason production routing systems (delivery
# routing, ride-share dispatch, chip-layout tools) use heuristics, local
# search (2-opt), or metaheuristics instead of brute force the moment n
# crosses roughly a dozen.
