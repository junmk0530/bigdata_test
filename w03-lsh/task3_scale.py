#!/usr/bin/env python3
"""Week 3 · Task 3 — Find the same pairs without comparing everything.

Textbook §3.4.

`BruteForce` compares every pair. On 3,000 documents that is 4.5 million
comparisons and it is completely correct. On 3 million documents it is 4.5
trillion and it is completely useless.

Beat it. Find the same near-duplicate pairs while making far fewer comparisons.

    python3 bench.py
    python3 bench.py --yours

The harness counts every call you make to `similarity()`. That is your score.
It also checks **recall** - which of the truly similar pairs you found. Skipping
comparisons is easy; skipping comparisons without losing the pairs is the task.
"""


class BruteForce:
    """Correct, and quadratic."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        """docs is [set_of_shingles, ...]. Return {(i, j), ...} with i < j."""
        out = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))
        return out


class YourFinder:
    """Your near-duplicate finder.

        __init__(threshold)
        find(docs, similarity) -> {(i, j), ...}

    `similarity(a, b)` is the only way to compare two documents, and every call
    is counted. Everything else - signatures, banding, bucketing - is free, in
    the sense that the harness does not charge you for it. That is deliberate:
    it is also roughly true at scale, where the comparison is the expensive
    part and the hashing is linear.

    Two knobs decide everything:

        the number of hashes in a signature
        how many bands you split it into

    §3.4.2 gives you the relationship between those and the probability that a
    pair at similarity s becomes a candidate. It is an S-curve, and where its
    step sits is something you choose. Choose it on purpose and be able to say
    why in observation.md - a threshold of 0.8 does not mean bands should be
    anything in particular until you have done the arithmetic.

    You may reuse your Task 1 code.
    """

    def __init__(self, threshold):
        self.threshold = threshold
        # 해시 수 n=160, 밴드 수 b=80 -> r = 2로 변경
        # r=2로 낮추면 후보군을 매우 촘촘하게 추출하여 Recall이 95~100%까지 상승합니다.
        self.num_hashes = 160
        self.bands = 80
        self.r = self.num_hashes // self.bands

        # 결정론적 해시 함수 생성
        self.prime = 4294967311
        self.hashes = [
            (lambda r, a=a, b=b: ((a * r + b) % self.prime))
            for a, b in [
                ((i * 10007 + 3) % 2147483647, (i * 50021 + 7) % 2147483647)
                for i in range(1, self.num_hashes + 1)
            ]
        ]

    def find(self, docs, similarity):
        num_docs = len(docs)
        if num_docs < 2:
            return set()

        # 1. Minhash 시그니처 생성
        # 각 문서(doc)의 shingle들을 해싱하여 최소값을 구합니다.
        signatures = []
        for doc in docs:
            sig = []
            for h in self.hashes:
                if not doc:
                    sig.append(0)
                else:
                    sig.append(min(h(x) for x in doc))
            signatures.append(sig)

        # 2. LSH Banding을 통해 후보 쌍(Candidates) 추출
        candidates = set()
        for b in range(self.bands):
            buckets = {}
            for doc_id in range(num_docs):
                band_portion = tuple(
                    signatures[doc_id][b * self.r : (b + 1) * self.r]
                )
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

        # 3. LSH가 걸러낸 후보 쌍들에 대해서만 실제 similarity() 호출 검사
        out = set()
        for i, j in candidates:
            if similarity(docs[i], docs[j]) >= self.threshold:
                out.add((i, j))

        return out
