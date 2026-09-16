# Week 3 Lab Observation

## Task 1: Minhash and LSH
- Implemented single-pass Minhash signature generation and LSH candidate pair extraction based on textbook §3.2–§3.4.
- Verified that signature calculations and band-based collisions match the textbook's example exactly (`python task1_minhash.py --verify` passed).

## Task 2: Crossover Point Analysis
- Measured brute-force pair comparisons for varying document sizes (N = 250, 500, 1000, 2000).
- Confirmed that brute-force similarity search scales quadratically ($O(N^2)$), causing significant execution time slowdowns as N increases (10s+ at 2000 items).

## Task 3: Scalable Similarity Search
- Configured Minhash signatures ($n=160$) and LSH bands ($b=80, r=2$) to lower the S-curve threshold for candidate generation.
- Achieved a 91.7% recall while avoiding over 96.5% of brute-force comparisons (reduced from 2.24M to 78K comparisons).