#!/usr/bin/env python3
"""Week 4 · Task 1 — Answer questions about a stream you cannot store.

Textbook §4.3 (sampling), §4.4 (Bloom filter), §4.5 (Flajolet-Martin).

The premise of the whole chapter: the stream is longer than your memory, it
goes past once, and you still have to answer. Every method here trades an exact
answer for a bounded amount of space, and the job is to know exactly what you
traded.

You build three, and the harness checks each against the truth it is
approximating.

    python3 task1_sketches.py --verify
"""
import argparse, random


class BloomFilter:
    """Membership, with one-sided error.

    A Bloom filter never says "no" about something you inserted. It sometimes
    says "yes" about something you did not. That asymmetry is the entire design
    and it is why it is useful for "have I seen this before" and useless for
    "is this definitely in the set".

    `m` bits, `k` hash functions.
    """

    def __init__(self, m, k, seed=246):
        self.m = m
        self.k = k
        self.bit_array = [0] * m
        
        # k개의 독립적인 해시 함수 파라미터 (a, b)
        prime = 4294967311
        rng = random.Random(seed)
        self.hash_params = [
            (rng.randint(1, prime - 1), rng.randint(0, prime - 1))
            for _ in range(k)
        ]
        self.prime = prime

    def add(self, item):
        val = hash(item) & 0xFFFFFFFF
        for a, b in self.hash_params:
            idx = ((a * val + b) % self.prime) % self.m
            self.bit_array[idx] = 1

    def __contains__(self, item):
        val = hash(item) & 0xFFFFFFFF
        for a, b in self.hash_params:
            idx = ((a * val + b) % self.prime) % self.m
            if self.bit_array[idx] == 0:
                return False
        return True

    def expected_fp_rate(self, n_inserted):
        """The textbook's predicted false-positive rate after n insertions.

        §4.4.2 derives it. Return the number, do not measure it - the harness
        measures separately and compares the two.
        """
        if self.m == 0:
            return 1.0
        # 교재 §4.4.2 공식: (1 - (1 - 1/m)^(k*n))^k ≈ (1 - e^(-kn/m))^k
        # math 모듈 없이 근사식 직접 가공
        p_bit_0 = (1.0 - 1.0 / self.m) ** (self.k * n_inserted)
        return (1.0 - p_bit_0) ** self.k

def flajolet_martin(stream, n_hashes=64, seed=246):
    """Estimate how many DISTINCT items went past, in almost no memory.

    §4.5. Hash each item, count trailing zeros in the hash, keep the maximum.
    A maximum of R suggests about 2^R distinct items, because seeing R trailing
    zeros is a 1-in-2^R event.

    One hash gives an estimate with enormous variance, so you use many and
    combine them. How you combine them matters a great deal:

      * averaging 2^R directly is dominated by whichever hash got lucky - the
        values are exponential, so one outlier swamps the rest
      * the median is robust but can only ever be a power of two
      * §4.5.3 suggests grouping, and combining twice

    The harness accepts anything **within a factor of two** of the truth. That is
    not a generous tolerance, it is an honest one: this method really is that
    crude, and HyperLogLog exists because of it. Getting inside a factor of two
    reliably is the requirement; getting closer than that is not expected here.

    Return your estimate as a float.
    """
    prime = 4294967311
    rng = random.Random(seed)
    hash_params = [
        (rng.randint(1, prime - 1), rng.randint(0, prime - 1))
        for _ in range(n_hashes)
    ]

    max_r = [0] * n_hashes

    for item in stream:
        val = hash(item) & 0xFFFFFFFF
        for i, (a, b) in enumerate(hash_params):
            h_val = (a * val + b) % prime
            
            # trailing zeros 계산
            r = 0
            if h_val != 0:
                while (h_val & 1) == 0:
                    r += 1
                    h_val >>= 1
            else:
                r = 32

            if r > max_r[i]:
                max_r[i] = r

    # §4.5.3 Grouping: R값들의 그룹 내 평균을 구한 뒤 2^(avg_R) 계산
    num_groups = 8
    group_size = n_hashes // num_groups

    group_estimates = []
    for g in range(num_groups):
        sub_r = max_r[g * group_size : (g + 1) * group_size]
        avg_r = sum(sub_r) / len(sub_r)
        group_estimates.append(2 ** avg_r)

    group_estimates.sort()
    mid = len(group_estimates) // 2
    if len(group_estimates) % 2 == 1:
        return float(group_estimates[mid])
    else:
        return float((group_estimates[mid - 1] + group_estimates[mid]) / 2.0)


def reservoir_sample(stream, k, seed=246):
    """Keep k items uniformly at random from a stream of unknown length.

    §4.3. Every item that went past must end up with the same probability k/n
    of being in your sample, and you only ever hold k of them.

    Return a list of k items (or fewer if the stream was shorter).
    """
    rng = random.Random(seed)
    sample = []

    for i, item in enumerate(stream):
        if len(sample) < k:
            sample.append(item)
        else:
            j = rng.randint(0, i)
            if j < k:
                sample[j] = item

    return sample

# ------------------------------------------------------------------- harness
def verify():
    fails = 0
    rng = random.Random(246)

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<46} {detail}")
        fails += not ok

    # --- Bloom: no false negatives, ever
    try:
        bf = BloomFilter(m=8192, k=5)
    except NotImplementedError:
        print("  BloomFilter is still a stub"); return 1
    inserted = [f"item-{i}" for i in range(800)]
    for x in inserted:
        bf.add(x)
    check("no false negatives", all(x in bf for x in inserted))

    absent = [f"other-{i}" for i in range(20_000)]
    fp = sum(1 for x in absent if x in bf) / len(absent)
    predicted = bf.expected_fp_rate(len(inserted))
    close = abs(fp - predicted) < max(0.02, predicted * 0.5)
    check("measured false-positive rate matches theory", close,
          f"measured {fp:.3%}, predicted {predicted:.3%}")

    # --- Flajolet-Martin: a factor of two is what this method gives you
    try:
        distinct = 20_000
        stream = [f"k{rng.randrange(distinct)}" for _ in range(120_000)]
        est = flajolet_martin(stream)
    except NotImplementedError:
        print("  flajolet_martin is still a stub"); return 1
    true_distinct = len(set(stream))
    ratio = est / true_distinct
    check("distinct estimate within a factor of 2", 0.5 <= ratio <= 2.0,
          f"estimated {est:,.0f}, true {true_distinct:,} ({ratio:.2f}x)")

    # --- Reservoir: uniform over many trials
    try:
        counts = [0] * 20
        trials = 4000
        for t in range(trials):
            s = reservoir_sample(range(20), 5, seed=t)
            for i in s:
                counts[i] += 1
    except NotImplementedError:
        print("  reservoir_sample is still a stub"); return 1
    expected = trials * 5 / 20
    spread = (max(counts) - min(counts)) / expected
    check("reservoir is uniform across items", spread < 0.15,
          f"spread {spread:.1%} around {expected:.0f}")

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
