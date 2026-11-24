# GATEwise

Ask a GATE DA question in plain English. Get the closest real past-year questions
back — with the year, question number, topic and the **official answer key** —
and a measured hit rate on top.

No LLM, no API key, no runtime downloads. BM25 over the actual papers.

```
hit@1  7/10  (0.70)
hit@3  8/10  (0.80)
MRR    0.750      ← 10 hand-written queries, `python eval.py` reproduces this
```

The one miss in the top 3 is a vocabulary gap, not a ranking bug: the query says
"first derivative is zero and the second derivative is positive", while the paper
writes `f′(x*) = 0 and f″(x*) > 0`. BM25 cannot bridge that without embeddings —
which is exactly why embeddings are the next step, not a rewrite.

## What it is (and isn't)

It's a retrieval system, not a chatbot. It never generates an answer: every
answer it returns was printed in the organisers' own key. That constraint is the
point — a wrong answer with a confident tone is worse than no answer, and this
design makes the failure mode visible ("No matches — the corpus does not cover
this") instead of plausible.

## Corpus

155 questions from the official IIT Madras GATE DA papers:

| Year | Question paper | Answer key | Kept |
|---|---|---|---|
| 2024 | `DA24S1.pdf` | `DAFinalAnswerKey.pdf` | 53 |
| 2025 | `DA2025.pdf` | `DA_Keys.pdf` | 53 |
| 2026 | `DA.pdf` | `DA_Keys.pdf` | 49 |

Built by `build_corpus.py`, which is deterministic and auditable:

- **GA out, DA in** — general aptitude (Q1–10) is dropped, only Q11+ ships.
- **Figure-dependent questions skipped** — a demo does not need a picture.
- **Answers come from the key, never guessed** — MCQ letters, `A;C` for MSQ,
  the printed range for NAT (`0.25 to 0.25`), `MTA` where the key says so.
- **One key parser for three formats** — the 2025 key explodes every table cell
  onto its own line; normalising whitespace makes one pattern cover all three years.

The PDFs themselves are not committed (`data/*.pdf` is ignored — they are ~10 MB).
Download them from `https://gate2027.iitm.ac.in/static/doc/download/` into `data/`
using the filenames in the table above, then run the build.

## Run it

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python build_corpus.py          # PDFs in data/ -> gatewise/questions.jsonl
python eval.py                  # the numbers above
python ask.py "hash table linear probing"    # CLI, cited
streamlit run app.py            # the demo
```

## Design decisions

- **BM25 with zero dependencies** (`gatewise/bm25.py`) instead of a vector store.
  The corpus is 155 documents; a vector database would be decoration, and the
  honest baseline is what makes the number meaningful.
- **A coverage floor, not just `score > 0`.** BM25 alone never returns nothing —
  any shared rare token scores above zero, so an unrelated query still gets three
  confident-looking answers. Requiring the document to cover ≥30% of the query's
  content words is what makes "no matches" possible. This is the single change
  that took the out-of-corpus case from 3 false hits to 0.
- **Stopwords in the tokeniser.** Question words ("how", "does", "which") carry no
  signal and inflate coverage; removing them tightened every query.
- **No LLM generation.** Deliberately out of scope until the retrieval number
  exists. A generator on top of a 0.70 hit@1 retriever would produce confident
  answers to questions the corpus cannot answer.

## Layout

```
build_corpus.py        PDFs -> gatewise/questions.jsonl
gatewise/bm25.py       BM25, no dependencies
gatewise/corpus.py     loader
ask.py                 CLI: query in, cited matches out
eval.py                hit@1, hit@3, MRR over 10 fixed queries
app.py                 Streamlit demo
```

## Next

- Embeddings as a second retriever, compared head-to-head on hit@3. The one
  paraphrase miss above is the case for it.
- Topic labels are keyword-mapped, not hand-checked: ~23% land in `general`.

Built on official GATE Data Science & Artificial Intelligence papers (IIT Madras).
Not affiliated with the organising institute.
