"""Minimal BM25. No dependencies, no downloads — runs on any free tier."""
import math
import re

TOKEN = re.compile(r"[a-z0-9]+")


def tokenise(text):
    return TOKEN.findall(text.lower())


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

    def top(self, query, k=3):
        ranked = sorted(range(len(self.docs)), key=lambda i: self.score(query, i), reverse=True)
        return [self.docs[i] for i in ranked[:k] if self.score(query, i) > 0]
