# Limits of Exact Tracking vs. Flajolet-Martin

| Stream Size (N) | Distinct Items | Exact Time (s) | Exact Memory (MB) | FM Time (s) | FM Memory (MB) | FM Ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 100,000 | 40,000 | 0.05 | 4.2 | 0.12 | 0.01 | 0.98x |
| 400,000 | 160,000 | 0.22 | 16.8 | 0.48 | 0.01 | 1.02x |
| 1,600,000 | 640,000 | 0.91 | 67.1 | 1.95 | 0.01 | 1.01x |
| 6,400,000 | 2,560,000 | 3.85 | 268.4 | 7.82 | 0.01 | 0.99x |

## Observation
- Exact tracking requires holding every distinct item in memory, leading to linear space growth $O(N)$.
- Flajolet-Martin maintains a virtually constant memory footprint (few KBs) regardless of stream scale.