"""eval.py — how good is the retrieval, actually?

Ten hand-written queries, each tied to the (year, qno) it should return.
Prints hit@1, hit@3 and MRR, plus every failure by name.

    python eval.py

The first number this prints is the honest one. Tuning happens after, and the
before/after is what the README reports.
"""
import sys

from gatewise.bm25 import BM25
from gatewise.corpus import load

# (query, (year, qno), kind)
CASES = [
    # 4 paraphrases — different words from the paper
    ("chance of getting two or more heads when three coins are tossed",
     (2024, 12), "paraphrase"),
    ("how many additions and multiplications does gaussian elimination take",
     (2025, 12), "paraphrase"),
    ("if the first derivative is zero and the second derivative is positive at a point",
     (2024, 15), "paraphrase"),
    ("what does relu do to negative inputs",
     (2025, 48), "paraphrase"),
    # 3 keyword-dense
    ("hash table size 10 linear probing collisions insert keys",
     (2025, 18), "keywords"),
    ("functional dependency candidate keys relational schema R(A,B,C,D,E)",
     (2026, 17), "keywords"),
    ("k-means clustering euclidean distance 100 points centroids",
     (2024, 19), "keywords"),
    # 2 topic-only
    ("singular values of a rank one matrix outer product",
     (2024, 61), "topic"),
    ("naive bayes classifier two class problem",
     (2025, 35), "topic"),
    # 1 deliberately out of corpus — must return nothing
    ("how do I fine-tune a large language model with LoRA",
     None, "out-of-corpus"),
]

K = 3


def target(doc):
    return (doc["year"], doc["qno"])


def main():
    docs = load()
    index = BM25(docs)
    hits1 = hits3 = 0
    rr_total = 0.0
    rows = []

    for query, want, kind in CASES:
        got = index.top(query, k=K)
        ranks = [target(d) for d in got]
        hit1 = bool(want) and ranks[:1] == [want]
        hit3 = bool(want) and want in ranks
        rr = 0.0
        if want and want in ranks:
            rr = 1.0 / (ranks.index(want) + 1)
        if want is None:
            ok = not got
            rows.append((kind, query, "empty" if ok else f"returned {len(got)}", ok))
        else:
            rows.append((kind, query, f"{'hit' if hit3 else 'miss'} {ranks}", hit3))
        hits1 += hit1
        hits3 += hit3
        rr_total += rr

    n = len(CASES)
    print(f"\ncorpus: {len(docs)} questions  |  eval: {n} queries  |  k={K}\n")
    for kind, query, result, _ok in rows:
        print(f"  [{kind:<13}] {query[:58]:<58} -> {result}")

    print(f"\n  hit@1  {hits1}/{n}  ({hits1 / n:.2f})")
    print(f"  hit@3  {hits3}/{n}  ({hits3 / n:.2f})")
    print(f"  MRR    {rr_total / n:.3f}\n")

    if "--strict" in sys.argv and hits3 != n:
        sys.exit(1)


if __name__ == "__main__":
    main()
