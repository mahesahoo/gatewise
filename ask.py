"""ask.py — query in, cited matches out.

    python ask.py "bayes rule denominator"
    python ask.py            # interactive
"""
import sys

from gatewise.bm25 import BM25
from gatewise.corpus import load


def show(docs, k=3):
    index = BM25(docs)
    return index.top(k)


def render(matches):
    if not matches:
        return "no matches — the corpus does not cover this yet"
    out = []
    for i, d in enumerate(matches, 1):
        src = f"GATE DA {d['year']} · Q{d['qno']}" if d["year"] else f"sample · Q{d['qno']}"
        out.append(f"{i}. [{src} · {d['topic']}]\n   {d['question']}\n   answer: {d['answer']}")
    return "\n".join(out)


def main():
    docs = load()
    q = " ".join(sys.argv[1:]).strip()
    if q:
        print(render(show(docs, q)))
        return
    print(f"{len(docs)} questions indexed. type a query, empty line to quit.")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            break
        print(render(show(docs, line)))
        print()


if __name__ == "__main__":
    main()
