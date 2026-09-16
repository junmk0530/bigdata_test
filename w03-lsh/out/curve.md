# Timing and Comparison Curve

| Size (N) | Brute-force Time | Brute-force Comparisons | LSH Time | LSH Comparisons |
|---:|---:|---:|---:|---:|
| 100 | 0.03s | 4,950 | 0.47s | 159 |
| 250 | 0.17s | 31,125 | 1.15s | 1,058 |
| 500 | 0.68s | 124,750 | 2.34s | 4,609 |
| 1000 | 2.61s | 499,500 | 4.74s | 18,389 |
| 1600 | 6.33s | 1,279,200 | 7.64s | 45,819 |

## Crossover Observation
- Brute-force search shows quadratic growth ($O(N^2)$) in candidate comparisons.
- LSH significantly reduces total comparisons (e.g., from 1.28M down to 45.8K at N=1600).