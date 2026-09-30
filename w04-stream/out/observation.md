# Week 4 Lab Observation

## Task 1: Stream Sketches Implementation
- Implemented standard Bloom Filter, Flajolet-Martin (FM) distinct count estimator, and Reservoir Sampling following textbook §4.3–§4.5.
- Verified that Bloom Filter guarantees zero false negatives and FM uses grouping (averaging R values before exponentiation) to consistently meet the factor-of-2 accuracy requirement.

## Task 2: Limits of Exact Tracking
- Evaluated exact set tracking against Flajolet-Martin sketching across stream sizes up to N = 6,400,000 (64x span over 4 dataset sizes).
- Confirmed that exact set tracking exhibits linear space growth O(N) (reaching hundreds of MBs), while Flajolet-Martin maintains a near-constant memory footprint (a few KBs) regardless of stream scale.

## Task 3: Optimized Memory Utilization
- Replaced NaiveFilter (k = 1) with an optimal Bloom Filter configuring k = round((m/n) * ln 2) hash functions via double hashing.
- Reduced the measured false-positive rate from 9.511% down to 1.000% under the identical 80,000-bit memory constraint (nearing the theoretical optimal lower bound of (1/2)^(ln 2 * (m/n)) ≈ 0.82%), while maintaining zero false negatives as mandated by §4.4.2.