cat << 'EOF' > out/explosion.md
# Task 2: Combinatorial Explosion Analysis

## Key Observations

1. Impact of Lowering Support Threshold:
   - As the support threshold decreases, the number of frequent singletons passing pass one increases linearly.
   - However, the number of candidate pairs generated in pass two grows combinatorially, causing peak counters and memory usage to spike rapidly.

2. Resource Bottlenecks:
   - Setting support thresholds too low leads to severe memory pressure and excessive computation time, demonstrating the physical scaling limits of standard A-Priori on a single machine.
EOF