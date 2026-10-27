# Week 7 — Observations

## Task 1 · k-means, and the thing that decides the answer

Over 40 seeds, random init found the three blobs 24 times. The other 16 merged two blobs and split the third, stopping at SSE ≈ 96.1 instead of 0.12 (mean 38.51). k-means++ found them all 40 times (mean 0.12).

R3: an empty cluster keeps its previous centroid, which is deterministic. An empty cluster actually happened in only 3 of the 40 random runs (seeds 22, 23, 37), all of which ended badly. Re-seeding at the farthest point instead would have rescued those 3 (16 → 13 bad runs), but it cannot touch the other 13, where no cluster ever emptied and k-means simply sat in a local optimum.

k-means++ spends distances before iteration 1: about n·k(k−1)/2 in my version, or about one n·k pass if each point's nearest-seed distance is cached. That buys a start in the right basin. I would skip it when I run many cheap restarts anyway, or when there are outliers, because d² weighting pulls seeds onto them. SSE cannot choose k because it always falls as k grows, reaching 0 at k = n, so minimising it just rewards over-splitting. The elbow or silhouette is used instead.

## Task 2 · Watch distance stop meaning anything

With 1000 points, contrast dropped below 1 at d≈50 (0.982) and below 0.5 around d≈120. Mean distance tracked sqrt(d/6), and rel.sd fell like 0.6/sqrt(d).

n barely mattered: at d=1000, contrast was 0.162 / 0.153 / 0.169 for n = 500 / 2000 / 5000. The script always samples 20,000 pairs, and n moves the extremes only like sqrt(log pairs), so d decides how hard the curse bites.

It does not threaten Week 3 MinHash LSH. P(collision) equals Jaccard regardless of vocabulary size. Real shingle sets are also structured, with near-duplicates near 1 and unrelated pairs near 0, rather than concentrated around one value.

## Task 3 · The same clustering, with far fewer distances

Per point I store two extra floats: an upper bound to its own centroid and a lower bound to the nearest other centroid (Hamerly). That is 2n numbers, plus 2k for the centroids (half the gap to the nearest centroid, and how far each moved). On bench.py this gave 1,146,949 distances instead of 10,320,000: 88.9% fewer, and 22.0 s → 3.3 s.

R5: the per-point lower bound does most of the pruning. In an instrumented 20k×20, k=12 run it skipped about 50× more points than the centroid-gap bound. Maintaining it costs no distances per point. Each iteration needs only k movement distances plus k(k−1)/2 centroid pairs, which is 78 here, about 3,300 over the run, or 0.3% of the total.

The SSE difference is exactly 0. A skipped point is proven by the triangle inequality to keep its label, and every full scan uses the baseline's order and 1e-12 tie rule, so the labels, the means and the 43 iterations are identical. The first iteration cannot prune: its 20,000 × 12 = 240,000 distances are 20.9% of my total, while the other 42 iterations averaged about 21,600 each instead of 240,000.