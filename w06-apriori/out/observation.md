# Week 6: A-Priori and PCY Observations

## Task 1: A-Priori and Pass Two Constraints
- The monotonicity property guarantees that a pair cannot be frequent unless both of its individual items are frequent in pass one.
- Filtering out infrequent items in pass one drastically reduces candidate pair generation, avoiding the brute-force enumeration of all item combinations.

## Task 2: Combinatorial Explosion under Low Thresholds
- Lowering the support threshold exponentially increases the number of surviving singletons and candidate pairs in pass two.
- As threshold decreases, memory consumption and candidate counters spike rapidly, demonstrating the physical scaling limits of standard A-Priori.

## Task 3: Memory Efficiency with PCY Algorithm
- By hashing item pairs into a bucket array during pass one and compressing frequent buckets into a bitmap, PCY filters out candidate pairs prior to pass two.
- This dual-filtering approach reduced peak pair counters by over 97% while producing the exact same set of frequent pairs as baseline A-Priori.