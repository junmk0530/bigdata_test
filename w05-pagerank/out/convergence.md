# Task 2: PageRank Convergence Analysis

## Key Findings

1. Impact of Beta:
   - As beta increases toward 1.0 (for example, from 0.5 to 0.99), the number of iterations required to reach convergence increases sharply.
   - A smaller beta value accelerates convergence because the uniform teleportation probability (1 - beta) dominates the random walk.

2. Impact of Graph Size and Tolerance:
   - Increasing the number of nodes or setting a stricter tolerance threshold (such as 1e-12 instead of 1e-10) requires more iterations and computation time.
   - Regardless of graph scale, the mathematical relationship between beta and convergence speed remains consistent.