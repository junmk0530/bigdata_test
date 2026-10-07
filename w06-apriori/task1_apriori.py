#!/usr/bin/env python3
"""Week 6 · Task 1 — A-Priori, and why the second pass is the whole problem.

Textbook §6.1 (market-basket model), §6.2 (A-Priori).

Finding frequent pairs is easy until you count how many pairs there are. With
n items there are n(n-1)/2 of them, and for a supermarket's 10,000 items that
is 50 million counters before you have read a single basket.

A-Priori's observation is one sentence long: **a pair cannot be frequent unless
both of its items are frequent.** One extra pass over the data buys you a much
smaller second pass, and the whole chapter is consequences of that trade.

    python3 task1_apriori.py --verify
"""
import argparse
from itertools import combinations

# Small enough to check by hand. support threshold 3 unless stated.
BASKETS = [
    {"bread", "milk"},
    {"bread", "diaper", "beer", "egg"},
    {"milk", "diaper", "beer", "cola"},
    {"bread", "milk", "diaper", "beer"},
    {"bread", "milk", "diaper", "cola"},
    {"bread", "milk", "beer"},
    {"diaper", "beer"},
]


def frequent_singletons(baskets, support):
    """Items appearing in at least `support` baskets. Return {item: count}."""
    counts = {}
    for basket in baskets:
        for item in basket:
            counts[item] = counts.get(item, 0) + 1

    return {item: cnt for item, cnt in counts.items() if cnt >= support}

def frequent_pairs(baskets, support):
    """Pairs appearing in at least `support` baskets, using A-Priori.

    Return {frozenset({a, b}): count}.
    

    The requirement that makes this A-Priori rather than brute force: pass two
    must only ever count pairs **both of whose items were frequent in pass one**.
    If you count every pair and filter afterwards you have written the thing
    A-Priori exists to avoid, and it will pass this harness while failing the
    point. Task 3 measures whether you actually did it.
    """
    # Pass 1: Frequent Singletons
    singletons = frequent_singletons(baskets, support)
    freq_items = set(singletons.keys())

    # Pass 2: A-Priori Filtering
    # Pass 1에서 자주 등장한(frequent) 아이템들만으로 조합을 만들어 카운트
    pair_counts = {}
    for basket in baskets:
        valid_items = sorted(list(basket & freq_items))
        for pair in combinations(valid_items, 2):
            key = frozenset(pair)
            pair_counts[key] = pair_counts.get(key, 0) + 1

    return {pair: cnt for pair, cnt in pair_counts.items() if cnt >= support}


def association_rules(baskets, support, min_confidence):
    """Rules I -> j from the frequent pairs.

    For a frequent pair {i, j}, confidence of i -> j is
    support({i, j}) / support({i}).

    Return [(antecedent, consequent, confidence, lift), ...] for rules whose
    confidence is at least `min_confidence`, sorted by confidence descending.

    `lift` is confidence divided by the consequent's own support fraction. A
    rule with high confidence and lift near 1 tells you nothing - the consequent
    was common anyway - and §6.1.3 is about why that matters more than it looks.
    """
    singletons = frequent_singletons(baskets, support)
    pairs = frequent_pairs(baskets, support)
    num_baskets = len(baskets)

    rules = []

    for pair, pair_supp in pairs.items():
        pair_list = list(pair)
        i, j = pair_list[0], pair_list[1]

        # Rule 1: i -> j
        supp_i = singletons[i]
        conf_i_j = pair_supp / supp_i
        supp_frac_j = singletons[j] / num_baskets
        lift_i_j = conf_i_j / supp_frac_j

        if conf_i_j >= min_confidence:
            rules.append((i, j, conf_i_j, lift_i_j))

        # Rule 2: j -> i
        supp_j = singletons[j]
        conf_j_i = pair_supp / supp_j
        supp_frac_i = singletons[i] / num_baskets
        lift_j_i = conf_j_i / supp_frac_i

        if conf_j_i >= min_confidence:
            rules.append((j, i, conf_j_i, lift_j_i))

    # 신뢰도(Confidence) 내림차순 정렬
    rules.sort(key=lambda x: x[2], reverse=True)
    return rules


# ------------------------------------------------------------------- harness
def verify():
    fails = 0

    def check(label, got, want):
        nonlocal fails
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<44} {got}"
              + ("" if ok else f"\n{'':>54}want {want}"))
        fails += not ok

    try:
        singles = frequent_singletons(BASKETS, 3)
    except NotImplementedError:
        print("  frequent_singletons is still a stub"); return 1
    # counted by hand: bread 5, milk 5, diaper 5, beer 5, cola 2, egg 1
    check("frequent singletons at support 3",
          dict(sorted(singles.items())),
          {"beer": 5, "bread": 5, "diaper": 5, "milk": 5})

    try:
        pairs = frequent_pairs(BASKETS, 3)
    except NotImplementedError:
        print("  frequent_pairs is still a stub"); return 1
    got = {tuple(sorted(k)): v for k, v in pairs.items()}
    check("frequent pairs at support 3", dict(sorted(got.items())),
          {("beer", "bread"): 3, ("beer", "diaper"): 4, ("beer", "milk"): 3,
           ("bread", "diaper"): 3, ("bread", "milk"): 4, ("diaper", "milk"): 3})

    # cola appears twice, so it must never reach pass two
    check("infrequent items excluded from pairs",
          any("cola" in k or "egg" in k for k in got), False)

    try:
        rules = association_rules(BASKETS, 3, 0.75)
    except NotImplementedError:
        print("  association_rules is still a stub"); return 1
    # diaper -> beer: support 4, diaper 5, confidence 0.8
    hit = [r for r in rules if r[0] == "diaper" and r[1] == "beer"]
    check("diaper -> beer confidence", round(hit[0][2], 3) if hit else None, 0.8)
    check("rules are sorted by confidence",
          all(rules[i][2] >= rules[i + 1][2] for i in range(len(rules) - 1)), True)

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
