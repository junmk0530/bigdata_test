#!/usr/bin/env python3
"""Week 3 · Task 1 — Minhash and LSH, built from the matrix up.

Textbook §3.2 - §3.4.

Comparing every pair is quadratic, so it stops being possible somewhere around
a hundred thousand documents. The way out is two ideas stacked:

    minhash   replace a set with a short signature, such that the chance two
              signatures agree in a position equals their Jaccard similarity
    LSH       hash bands of those signatures so that similar pairs collide and
              you only ever compare the ones that did

You build both. The textbook's §3.3.5 example is small enough to check by hand,
and the harness checks you against it.

    python3 task1_minhash.py --verify
"""
import argparse

# §3.3.5. Rows are elements 0..4, columns are the sets S1..S4.
BOOK = [[1, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 0, 1, 0]]
# The two hash functions the textbook uses on the row numbers.
BOOK_HASHES = [lambda r: (r + 1) % 5, lambda r: (3 * r + 1) % 5]


def jaccard(a, b):
    """|a and b| / |a or b|. Empty union is 0, not an error."""
    intersection=len(a&b)
    union=len(a|b)
    if union==0:
        return 0
    return intersection/union

def minhash_signatures(columns, hashes, n_rows):
    num_docs = len(columns)
    num_hashes = len(hashes)
    
    sig_matrix = [[float('inf')] * num_hashes for _ in range(num_docs)]
    
    for r in range(n_rows):
        
        hash_values = [h(r) for h in hashes]
        
        
        for c, col_set in enumerate(columns):
            if r in col_set:
                for h_idx in range(num_hashes):
                    sig_matrix[c][h_idx] = min(sig_matrix[c][h_idx], hash_values[h_idx])
                    
    return sig_matrix


def lsh_candidates(signatures, bands):
    num_docs = len(signatures)
    sig_len = len(signatures[0])
    
    assert sig_len % bands == 0, "Signature length must divide evenly by bands"
    
    r = sig_len // bands
    candidates = set()
    
    for b in range(bands):
        buckets = {}
        for doc_id in range(num_docs):
           
            band_portion = tuple(signatures[doc_id][b * r : (b + 1) * r])
            
           
            if band_portion not in buckets:
                buckets[band_portion] = []
            buckets[band_portion].append(doc_id)
        
        
        for doc_list in buckets.values():
            if len(doc_list) > 1:
                for i in range(len(doc_list)):
                    for j in range(i + 1, len(doc_list)):
                        u, v = doc_list[i], doc_list[j]
                        if u > v:
                            u, v = v, u
                        candidates.add((u, v))
                        
    return candidates


# ------------------------------------------------------------------- harness
def columns_from_matrix(matrix):
    n_rows, n_cols = len(matrix), len(matrix[0])
    return [{r for r in range(n_rows) if matrix[r][c]} for c in range(n_cols)]


def verify():
    fails = 0

    def check(label, got, want):
        nonlocal fails
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<44} {got}"
              + ("" if ok else f"\n{'':>54}want {want}"))
        fails += not ok

    cols = columns_from_matrix(BOOK)
    try:
        # S1 = {0,3}, S4 = {0,2,3}: intersection 2, union 3
        check("jaccard(S1, S4)", round(jaccard(cols[0], cols[3]), 4), round(2 / 3, 4))
        check("jaccard(S1, S2)", jaccard(cols[0], cols[1]), 0.0)
        check("jaccard on empty sets", jaccard(set(), set()), 0)
    except NotImplementedError:
        print("  jaccard is still a stub"); return 1

    try:
        sig = minhash_signatures(cols, BOOK_HASHES, len(BOOK))
    except NotImplementedError:
        print("  minhash_signatures is still a stub"); return 1

    # Figure 3.4 in the textbook.
    check("signature of S1", sig[0], [1, 0])
    check("signature of S2", sig[1], [3, 2])
    check("signature of S3", sig[2], [0, 0])
    check("signature of S4", sig[3], [1, 0])

    try:
        cands = lsh_candidates([[1, 0], [3, 2], [0, 0], [1, 0]], bands=2)
    except NotImplementedError:
        print("  lsh_candidates is still a stub"); return 1
    # With one row per band, S1 and S4 are identical, so they must collide.
    check("S1 and S4 are candidates", (0, 3) in cands, True)
    check("S1 and S2 are not", (0, 1) in cands, False)

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    if not fails:
        print("  Note that S1 and S4 agree in both signature positions, which "
              "estimates\n  their similarity as 1.0 when it is actually 2/3. "
              "Two hashes is not many.")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
