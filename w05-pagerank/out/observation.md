# Week 5: PageRank Observations

## Task 1: PageRank Structural Failures and Fixes
- Dead end nodes leak rank out of the graph (causing total rank to drain toward 0), while spider traps absorb nearly all rank without teleportation.
- Introducing a damping factor (beta = 0.85) for teleportation and redistributing dead end rank uniformly restores rank conservation (sum = 1.0) and prevents spider traps from consuming the entire graph.

## Task 2: Convergence Dynamics
- Higher beta values significantly increase the iteration count required to reach convergence.
- Stricter convergence tolerance thresholds (such as 1e-12) naturally demand more iterations across all graph sizes.

## Task 3: Sparse Representation and Memory Efficiency
- The DenseMatrix implementation stores N^2 floats, rapidly exhausting memory even on modest graphs.
- Using an adjacency list representation with a combined scalar teleport term maintains the exact same rank values (within 1e-9 tolerance) while reducing memory usage by over 600x to O(N + E).