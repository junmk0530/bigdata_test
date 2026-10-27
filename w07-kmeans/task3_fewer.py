#!/usr/bin/env python3
"""Week 7 · Task 3 — The same clustering, with far fewer distances.

Textbook §7.3, and §7.1.3 for why distance is the expensive part.

`NaiveKMeans` does what the definition says: every iteration, compare every
point with every centroid. That is n x k distance computations per pass, and on
a real dataset the distance computation is almost the entire cost.

Most of that work is wasted. After the first couple of iterations, most points
do not change cluster, and most centroids barely move. The triangle inequality
lets you prove a point cannot have changed cluster **without measuring it**.

    python3 bench.py
    python3 bench.py --yours

Correctness first: your final SSE must match the baseline's. Fewer distances
with a worse clustering is not an improvement, it is a different algorithm.
"""


class NaiveKMeans:
    """Every point against every centroid, every iteration."""

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            for i, p in enumerate(points):
                best, bi = None, 0
                for j, c in enumerate(centroids):
                    d = distance(p, c)
                    if best is None or d < best - 1e-12:
                        best, bi = d, j
                if labels[i] != bi:
                    labels[i] = bi
                    changed = True
            centroids = _means(points, labels, self.k, centroids)
            if not changed:
                break
        return labels, centroids


def _means(points, labels, k, previous):
    out = []
    for j in range(k):
        group = [p for p, l in zip(points, labels) if l == j]
        if group:
            out.append(tuple(sum(v) / len(group) for v in zip(*group)))
        else:
            out.append(previous[j])
    return out


class YourKMeans:
    """Your k-means.

        __init__(k, max_iter=50)
        run(points, initial_centroids, distance) -> (labels, centroids)

    Same starting centroids, same `distance` function - which is counted. That
    counter is your score.

    The idea, from §7.3 and the triangle inequality:

        if a point is much closer to its current centroid than that centroid
        moved, and than any other centroid could have come, then it cannot have
        changed cluster, and you do not have to measure anything

    Keeping enough bookkeeping to make that test cheap, without keeping so much
    that the bookkeeping costs more than the distances, is the task.

    You may call `distance` on two centroids, and those calls are counted too -
    which is the correct accounting, since that is real work. There are k of
    them and n points, and k is much smaller than n. That asymmetry is the
    whole opening.
    """

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter
 
    def run(self, points, initial_centroids, distance):
        # Hamerly's algorithm. Per point we keep only two numbers:
        #   upper[i] >= distance to its own centroid
        #   lower[i] <= distance to the nearest *other* centroid
        # Per centroid: half[j] = half the distance to its nearest other centroid.
        # If upper[i] < max(half[a], lower[i]), the triangle inequality proves the
        # point still belongs to centroid a, and nothing is measured.
        # Whenever a point is fully re-checked, the scan is exactly the baseline's
        # (same order, same 1e-12 tie rule), so the labels - and therefore every
        # centroid and the final SSE - are identical to NaiveKMeans.
        n, k = len(points), self.k
        centroids = list(initial_centroids)
        labels = [None] * n
        upper = [0.0] * n
        lower = [0.0] * n
        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            if self.iterations == 1:
                half = None
            else:
                # k(k-1)/2 centroid-centroid distances: cheap, since k << n
                half = [float("inf")] * k
                for j in range(k):
                    for jj in range(j + 1, k):
                        d = distance(centroids[j], centroids[jj]) / 2
                        if d < half[j]:
                            half[j] = d
                        if d < half[jj]:
                            half[jj] = d
            for i, p in enumerate(points):
                a = labels[i]
                if half is not None:
                    bound = max(half[a], lower[i])
                    if upper[i] < bound:
                        continue                      # proven: no distance needed
                    upper[i] = distance(p, centroids[a])  # tighten, one distance
                    if upper[i] < bound:
                        continue
                # full scan, identical to the baseline
                best, bi, second = None, 0, float("inf")
                for j, c in enumerate(centroids):
                    d = upper[i] if (j == a and half is not None) else distance(p, c)
                    if best is None or d < best - 1e-12:
                        if best is not None:
                            second = min(second, best)
                        best, bi = d, j
                    else:
                        second = min(second, d)
                upper[i], lower[i] = best, second
                if labels[i] != bi:
                    labels[i] = bi
                    changed = True
            new = _means(points, labels, k, centroids)
            if not changed:
                centroids = new
                break
            # how far each centroid moved: k distances
            moved = [distance(c, nc) for c, nc in zip(centroids, new)]
            centroids = new
            top = max(range(k), key=moved.__getitem__)
            rest = max((moved[j] for j in range(k) if j != top), default=0.0)
            for i in range(n):
                a = labels[i]
                upper[i] += moved[a]
                lower[i] -= rest if a == top else moved[top]
        return labels, centroids