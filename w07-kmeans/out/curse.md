# Task 2 · Watch Distance Stop Meaning Anything

Uniform points in the unit cube [0,1]^d, 20,000 random pairs per row.

## A2 · Contrast against dimension

| dim | points | mean | min | max | contrast | rel.sd | mean / sqrt(d/6) |
|----:|------:|------:|------:|------:|--------:|------:|------:|
| 2    | 1000 | 0.521  | 0.003  | 1.326  | 488.582 | 0.476 | 0.903 |
| 5    | 1000 | 0.884  | 0.111  | 1.687  | 14.257  | 0.282 | 0.968 |
| 10   | 1000 | 1.274  | 0.438  | 2.159  | 3.925   | 0.193 | 0.987 |
| 20   | 1000 | 1.815  | 0.821  | 2.670  | 2.253   | 0.135 | 0.994 |
| 50   | 1000 | 2.867  | 1.909  | 3.785  | 0.982   | 0.083 | 0.993 |
| 100  | 1000 | 4.068  | 3.206  | 4.954  | 0.545   | 0.060 | 0.996 |
| 200  | 1000 | 5.776  | 4.871  | 6.682  | 0.372   | 0.041 | 1.000 |
| 500  | 2000 | 9.126  | 8.099  | 10.176 | 0.256   | 0.026 | 1.000 |
| 1000 | 2000 | 12.909 | 11.970 | 13.806 | 0.153   | 0.019 | 1.000 |

## A3 · What happens to contrast

Contrast collapses: 488 at d=2, 3.9 at d=10, 0.15 at d=1000. At d=2 the closest pair
is almost on top of each other (min 0.003), so the farthest pair is hundreds of
times farther. By d=1000 the farthest pair is only 15% farther than the closest.

- Below **1** at about **d = 50** (0.982): the farthest pair is now less than twice
  as far as the nearest.
- Below **0.5** between d = 100 (0.545) and d = 200 (0.372), roughly **d ≈ 120**.

## A4 · How the mean grows

It is not linear in d. It grows like **sqrt(d)**. For two uniform points the
expected squared distance is d/6, because each coordinate contributes
E[(x−y)²] = 1/6. So the mean distance is about sqrt(d/6) ≈ 0.41·sqrt(d).

The last column checks this. The ratio is 1.000 from d=200 on. It falls below 1 at
small d (0.90 at d=2) because E[sqrt(X)] < sqrt(E[X]) (Jensen), and that gap
only matters while the spread is large relative to the mean. Doubling d multiplies
the mean by about 1.41, not 2. For example, 100 → 200 gives 4.068 → 5.776, ×1.42.

## A5 · Relative standard deviation

rel.sd falls as about **0.6 / sqrt(d)**. rel.sd·sqrt(d) is 0.61 at d=10, 0.60 at d=100
and 0.60 at d=1000. Distances concentrate around their mean, which keeps growing,
while the spread stays roughly constant in absolute terms.

**rel.sd is the better measure** of "distance stopped meaning anything". It
describes the whole distribution, it is a stable estimate, and it does not depend
on n. Contrast depends only on two extreme values (one minimum, one maximum),
so it is noisy and is affected by how many pairs were looked at (see A6). Contrast
is the more intuitive number for nearest-neighbour search, but rel.sd is the more
reliable one.

## A6 · Does contrast depend on n?

| dim | n = 500 | n = 2000 | n = 5000 |
|----:|------:|------:|------:|
| 500  | 0.215 | 0.256 | 0.221 |
| 1000 | 0.162 | 0.153 | 0.169 |

In these runs **n barely matters**, and the differences have no direction. They
are sampling noise. The reason is the script: it always samples a fixed 20,000
pairs, so the min and max come from 20,000 pairs whatever n is. n only changes
which points those pairs are drawn from.

In principle n does matter. With all n(n−1)/2 pairs, the minimum gets smaller
and the maximum larger as n grows, so contrast rises with n. This matters a lot at
low d: at d=2 more points pack closer and the min goes to 0. At high d the effect is
weak, because the extremes of a concentrated distribution move only like
sqrt(log(pairs)). So n affects where the curse starts, but d dominates how
strongly it bites.

## A7 · Machine and timing

- Machine: Windows-11-10.0.26200-SP0, Intel64 Family 6 Model 197 Stepping 2 (GenuineIntel), Python 3.14.3
- Largest run: d = 1000, n = 5000 (19,995 pairs), **2.26 s**. Most of the time is the 20,000 distances of 1000 terms each (d × pairs). n adds a smaller cost for generating n × d coordinates.

## A8 · Does this threaten Week 3 LSH on Jaccard?

**Not in general.** MinHash LSH does not compare raw distances. The probability
that two sets agree on one MinHash value **equals their Jaccard similarity**, and
that holds however large the shingle vocabulary is. The signature length and the
banding (b, r) do not grow with the dimension of the underlying space.

The curse in this task is about **unstructured** data: uniform independent
coordinates, where every pair looks equally far apart. Shingle sets are sparse
and structured. Near-duplicate documents share most shingles (Jaccard close to 1),
and unrelated ones share almost none (close to 0), so the similarities do not
concentrate around one value.

LSH would fail only when the data itself is like this task: all pairs have nearly
the same Jaccard similarity. Then no banding can separate "similar" from
"not similar". That is a property of the data, not of high dimension.