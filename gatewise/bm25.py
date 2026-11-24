"""Minimal BM25. No dependencies, no downloads — runs on any free tier."""
import math
import re

TOKEN = re.compile(r"[a-z0-9]+")

# Question words carry no retrieval signal and inflate coverage for queries that
# should match nothing (see the out-of-corpus case in eval.py).
STOPWORDS = frozenset("a an the is are was were be been of to in on at for with from by and or not "
                      "what which who how does do did can could should would this that these those it its "
                      "as if then than there their any all i my me we you your".split())


def tokenise(text):
    return [w for w in TOKEN.findall(text.lower()) if w not in STOPWORDS]


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = docs
        self.k1, self.b = k1, b
        self.tokens = [tokenise(d["text"]) for d in docs]
        self.lens = [len(t) for t in self.tokens]
        self.avg = sum(self.lens) / max(len(self.lens), 1)
        self.df = {}
        for toks in self.tokens:
            for w in set(toks):
                self.df[w] = self.df.get(w, 0) + 1
        n = len(docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in self.df.items()}

    def score(self, query, i):
        toks = self.tokens[i]
        if not toks:
            return 0.0
        tf = {}
        for w in toks:
            tf[w] = tf.get(w, 0) + 1
        s = 0.0
        for w in tokenise(query):
            if w not in tf:
                continue
            num = tf[w] * (self.k1 + 1)
            den = tf[w] + self.k1 * (1 - self.b + self.b * self.lens[i] / self.avg)
            s += self.idf.get(w, 0.0) * num / den
        return s

    def top(self, query, k=3, min_coverage=0.3):
        """Top-k documents, filtered by a relevance floor.

        BM25 alone never returns nothing: any shared rare token scores > 0, so an
        unrelated query still gets three confident-looking answers. Requiring the
        document to cover at least `min_coverage` of the query's content words
        (stopwords ignored) is what makes "no matches" possible.
        """
        q_terms = set(tokenise(query))
        if not q_terms:
            return []
        scored = []
        for i, doc in enumerate(self.docs):
            s_ = self.score(query, i)
            if s_ <= 0:
                continue
            coverage = len(q_terms & set(self.tokens[i])) / len(q_terms)
            if coverage >= min_coverage:
                scored.append((s_, doc))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [doc for _s, doc in scored[:k]]
