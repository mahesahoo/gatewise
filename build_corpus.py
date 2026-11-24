"""build_corpus.py — extract GATE DA past-year questions from the official PDFs.

Reads the organiser's own question papers and answer keys from `data/` and
writes `gatewise/questions.jsonl` (one record per question).

    python build_corpus.py

Rules (see SCOPE.md):
  - GA out, DA in: keep Q11+ only.
  - Answers come from the key, never guessed.
  - Figure-dependent questions are skipped.
"""
import json
import pathlib
import unicodedata
import re
import sys

from pypdf import PdfReader

DATA = pathlib.Path(__file__).parent / "data"
OUT = pathlib.Path(__file__).parent / "gatewise" / "questions.jsonl"

PAPERS = {
    2024: ("2024_DA24S1.pdf", "2024_DAFinalAnswerKey.pdf"),
    2025: ("2025_DA2025.pdf", "2025_Key_DA_Keys.pdf"),
    2026: ("2026_DA.pdf", "2026_Keys_DA_Keys.pdf"),
}

QSTART = re.compile(r"^\s*Q\.?\s*(\d+)\b", re.M)
OPTION = re.compile(r"\(([A-D])\)\s*")
FIGURE = ("as shown", "shown in the figure", "given figure", "figure below",
          "following figure", "as shown below")
NOISE_LINE = re.compile(
    r"^\s*(Page \d+ of \d+|GATE \d{4} Data Science.*|Data Science .*\((?:DA|AI)\)|Organizing Institute.*|"
    r"General Aptitude.*|.*Carry (?:ONE|TWO) mark.*|.*marks? each\.?)\s*$",
    re.I,
)
NOISE_INLINE = re.compile(
    r"\s*(Page \d+ of \d+|GATE \d{4} Data Science.*|"
    r"Data Science and Artificial Intelligence \(DA\)|"
    r"Organizing Institute:.*|General Aptitude \(GA\)).*$",
    re.I,
)


def normalise(text):
    """NFKC (math italics -> ascii), drop page furniture, collapse whitespace."""
    text = unicodedata.normalize("NFKC", text)
    lines = [ln for ln in text.splitlines() if not NOISE_LINE.match(ln)]
    text = "\n".join(lines)
    return text.replace("\u200b", "").replace("\xa0", " ")


def pdf_text(path):
    raw = "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    return normalise(raw)


def parse_key(path):
    """Return {qno: (section, qtype, answer)} from an official answer key.

    The three keys are laid out differently: 2024/2026 print one row per line,
    2025 explodes every table cell onto its own line and separates them with
    pipes. Normalising all whitespace to single spaces makes one pattern fit all.
    """
    flat = re.sub(r"\s+", " ", pdf_text(path).replace("|", " "))
    row = re.compile(
        r"(\d{1,2}) (\d) (MCQ|MSQ|NAT|MTA) (GA|DA) "
        r"((?:\d*\.?\d+ to \d*\.?\d+)|[A-Za-z0-9.;\-]+) (\d)"
    )
    key = {}
    for m in row.finditer(flat):
        qno, _sess, qtype, section, ans, _marks = m.groups()
        key[int(qno)] = (section, qtype, ans.strip())
    return key


def split_questions(text):
    """Return {qno: block_text} using 'Q.<n>' markers, keeping the last block per number."""
    marks = [(m.start(), int(m.group(1))) for m in QSTART.finditer(text)]
    blocks = {}
    for i, (pos, qno) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        blocks[qno] = text[pos:end]
    return blocks


def clean(block):
    """Strip the question marker and any page furniture that bled in."""
    body = QSTART.sub("", block, count=1)
    body = NOISE_INLINE.sub(" ", body)
    return re.sub(r"\s+", " ", body).strip()


def parse_question(block):
    """Split a block into stem + options. Returns (stem, options) or (None, None)."""
    first = OPTION.search(block)
    if first:
        stem, rest = block[: first.start()], block[first.start():]
        opts = []
        parts = OPTION.split(rest)
        # parts = ['', 'A', 'text', 'B', 'text', ...]
        for i in range(1, len(parts) - 1, 2):
            opts.append(re.sub(r"\s+", " ", parts[i + 1]).strip())
        return re.sub(r"\s+", " ", stem).strip(), opts[:4]
    return re.sub(r"\s+", " ", block).strip(), []


TOPICS = {
    "probability": ["probability", "bayes", "random variable", "distribution", "expectation",
                    "expected value", "variance", "binomial", "poisson", "normal distribution",
                    "conditional", "density function", "uniform", "exponential", "markov chain"],
    "statistics": ["confidence interval", "hypothesis", "test statistic", "p-value", "regression",
                   "correlation", "estimator", "unbiased", "sampling", "least-squares",
                   "maximum likelihood", "covariance"],
    "linear_algebra": ["matrix", "eigen", "vector", "rank", "determinant", "orthogonal",
                       "subspace", "span", "linear transformation", "singular value", "invertible",
                       "symmetric", "projection", "positive definite", "null space"],
    "calculus": ["derivative", "differentiable", "continuous", "integral", "limit", "gradient",
                 "maxima", "minima", "taylor", "convex", "jacobian", "partial"],
    "optimization": ["optimization", "gradient descent", "lagrange", "duality",
                     "linear programming", "constraint", "objective function", "local minimum"],
    "machine_learning": ["classifier", "supervised", "unsupervised", "svm", "support vector",
                         "decision tree", "k-means", "overfitting", "neural network", "dropout",
                         "regularization", "training set", "cross-validation", "bias-variance",
                         "perceptron", "clustering", "labels", "features"],
    "deep_learning": ["activation", "backpropagation", "convolution", "recurrent", "lstm",
                      "transformer", "attention", "embedding", "autoencoder", "pooling"],
    "algorithms": ["complexity", "sorting", "graph", "tree", "dynamic programming", "greedy",
                   "hashing", "heap", "bfs", "dfs", "shortest path", "spanning tree",
                   "pseudocode", "recursion", "bijection"],
    "data_structure": ["stack", "queue", "linked list", "binary search tree", "hash table",
                       "hash function", "array", "priority queue"],
    "databases": ["sql", "relational", "normal form", "transaction", "index", "join",
                  "primary key", "functional dependency", "candidate key", "schema", "tuple"],
    "ai": ["search algorithm", "heuristic", "minimax", "alpha-beta", "propositional",
           "predicate logic", "resolution", "bayesian network", "reinforcement", "admissible"],
}


def topic_for(stem):
    s = stem.lower()
    best, hits = "general", 0
    for topic, words in TOPICS.items():
        n = sum(1 for w in words if w in s)
        if n > hits:
            best, hits = topic, n
    return best


def main():
    records, skipped = [], []
    for year, (paper, keyfile) in PAPERS.items():
        qtext = pdf_text(DATA / paper)
        key = parse_key(DATA / keyfile)
        blocks = split_questions(qtext)
        for qno, block in sorted(blocks.items()):
            if qno < 11:
                continue
            if qno not in key:
                skipped.append((year, qno, "no key"))
                continue
            section, qtype, answer = key[qno]
            if section != "DA":
                skipped.append((year, qno, "GA"))
                continue
            body = clean(block)
            stem, options = parse_question(body)
            if len(stem) < 40 or any(f in stem.lower() for f in FIGURE):
                skipped.append((year, qno, "figure/short"))
                continue
            answer = answer if qtype != "NAT" else answer
            records.append({
                "year": year,
                "qno": qno,
                "topic": topic_for(stem),
                "question": stem,
                "options": options,
                "answer": answer,
                "text": " ".join([str(year), stem, " ".join(options), answer, topic_for(stem)]),
            })

    records.sort(key=lambda r: (r["year"], r["qno"]))
    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n")

    print(f"wrote {len(records)} records to {OUT.relative_to(OUT.parent.parent)}")
    for year in PAPERS:
        n = sum(1 for r in records if r["year"] == year)
        print(f"  {year}: {n}")
    print(f"skipped {len(skipped)}: " + ", ".join(f"{y}/Q{q}({why})" for y, q, why in skipped[:20]) + " ...")
    if len(sys.argv) > 1:
        for r in records[:5]:
            print(json.dumps(r, indent=2)[:600])


if __name__ == "__main__":
    main()
