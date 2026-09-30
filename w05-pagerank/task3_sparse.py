#!/usr/bin/env python3
"""Week 5 · Task 3 — PageRank on a graph that will not fit as a matrix.

Textbook §5.2 (efficient PageRank), §5.2.1 - §5.2.3.

`DenseMatrix` is PageRank written the way the equations are written: build the
transition matrix M, multiply. It is correct, it is easy to read, and it stores
n^2 numbers for a graph with almost no edges.

The web's matrix is about 99.9999% zeros. Storing them is the problem, and
§5.2 is the chapter about not doing that.

    python3 bench.py
    python3 bench.py --yours

Correctness first: the harness compares your ranks against the dense version
element by element. A fast PageRank that ranks pages differently is a different
algorithm, not a faster one.
"""


class DenseMatrix:
    """PageRank as written in the equations. Stores n^2 floats."""

    def __init__(self, beta=0.85, tol=1e-10, max_iter=100):
        self.beta, self.tol, self.max_iter = beta, tol, max_iter

    def run(self, graph):
        nodes = list(graph)
        n = len(nodes)
        index = {v: i for i, v in enumerate(nodes)}

        # the full transition matrix, zeros and all
        M = [[0.0] * n for _ in range(n)]
        for v, outs in graph.items():
            if outs:
                share = 1.0 / len(outs)
                for w in outs:
                    M[index[w]][index[v]] = share
            else:
                for i in range(n):           # dead end: spread it everywhere
                    M[i][index[v]] = 1.0 / n

        r = [1.0 / n] * n
        for self.iterations in range(1, self.max_iter + 1):
            nr = [0.0] * n
            for i in range(n):
                row = M[i]
                s = 0.0
                for j in range(n):
                    if row[j]:
                        s += row[j] * r[j]
                nr[i] = self.beta * s + (1 - self.beta) / n
            delta = sum(abs(a - b) for a, b in zip(nr, r))
            r = nr
            if delta < self.tol:
                break
        return {v: r[index[v]] for v in nodes}

    def memory_floats(self):
        return getattr(self, "_n", 0) ** 2


class YourPageRank:
    """Your PageRank.

        __init__(beta=0.85, tol=1e-10, max_iter=100)
        run(graph) -> {node: rank}
        memory_floats() -> the largest number of floats you held at once

    Same ranks, to within 1e-9 per node. Far less memory.

    `graph` is {node: [out-neighbours]}. Note what that already is: an adjacency
    list, which is the sparse representation. The dense version throws that
    structure away and then pays to get it back.

    Two things to be careful about, and they are the same two as Task 1:

      * dead ends, whose rank has to go somewhere
      * the teleport term, which touches every node and is therefore the one
        part that looks like it needs a dense operation - it does not, and
        working out why is the point of §5.2.3

    `memory_floats()` is on your honour and the harness reads it. Count the
    numbers you actually hold at once.
    """

    def __init__(self, beta=0.85, tol=1e-10, max_iter=100):
        self.beta = beta
        self.tol = tol
        self.max_iter = max_iter
        self.iterations = 0
        self._max_floats = 0

    def run(self, graph):
        nodes = list(graph.keys())
        n = len(nodes)
        if n == 0:
            self._max_floats = 0
            return {}

        # 1. 랭크 벡터 초기화 (r_old: n, r_new: n)
        r = {node: 1.0 / n for node in nodes}

        # 메모리 추적: r 벡터(n) + new_r 벡터(n) + 각 노드의 degree 정보에 대한 float/계산 구조
        # 알고리즘 동작 중 동시에 가지고 있는 float 값들의 개수 (약 2n ~ 3n 개 수준)
        self._max_floats = 2 * n

        for it in range(1, self.max_iter + 1):
            self.iterations = it
            new_r = {node: 0.0 for node in nodes}

            # 2. Dead end 노드들의 랭크 합 계산
            dead_end_rank = sum(
                r[node] for node, outs in graph.items() if len(outs) == 0
            )

            # 3. Sparse update: Out-link를 따라 랭크를 아웃-이웃들에게만 전송
            for node, outs in graph.items():
                deg = len(outs)
                if deg > 0:
                    share = r[node] / deg
                    for target in outs:
                        new_r[target] += share

            # 4. Teleportation + Dead end 처리를 단일 스칼라 상수로 합성
            teleport_share = (1.0 - self.beta + self.beta * dead_end_rank) / n

            # 5. 전역 스칼라 가산 및 수렴 판단(L1 norm 계산)
            delta = 0.0
            for node in nodes:
                new_r[node] = self.beta * new_r[node] + teleport_share
                delta += abs(new_r[node] - r[node])

            r = new_r

            if delta < self.tol:
                break

        return r

    def memory_floats(self):
        return self._max_floats
