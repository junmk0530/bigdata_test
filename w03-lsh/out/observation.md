# Week 3 Lab Observation

## Task 1: Minhash and LSH
- Implemented single-pass Minhash signature generation and LSH candidate pair extraction following textbook §3.2–§3.4.
- Verified that signature matrix calculations and band-based candidate collisions perfectly reproduce the textbook example (`python task1_minhash.py --verify` passed).

## Task 2: Crossover Point Analysis
- Measured brute-force vs. LSH comparisons across document sizes ranging from $N = 100$ to $N = 2000$ (20x span over 6 dataset sizes).
- Confirmed quadratic scaling ($O(N^2)$) for brute-force comparisons (jumping from 4,950 at $N=100$ to nearly 2M comparisons at $N=2000$).
- Observed that while brute-force becomes computationally intractable as $N$ scales, LSH maintains linear scalability, dramatically reducing comparisons at larger scales.

## Task 3: Scalable Similarity Search
- Designed Minhash signatures ($n=160$) with LSH banding parameters ($b=80, r=2$).
- **Theoretical S-Curve Analysis**: The target Jaccard similarity threshold is $s = 0.6$. By setting $b=80$ and $r=2$, the theoretical S-curve crossover point is $(1/b)^{1/r} = (1/80)^{1/2} \approx 0.112$. Setting this threshold significantly below $0.6$ ensures high candidate capture probability for truly similar pairs.
- **Empirical Results**: Achieved **91.7% recall** while avoiding **96.51% of brute-force comparisons** (reducing candidate evaluation calls from 2.25M down to 78.4K).