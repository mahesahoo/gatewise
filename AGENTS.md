# AGENTS.md — GATEwise

Read this first. Why it exists, what's decided, what's measured.

## What / why
Ask a GATE DA question in plain English → get the closest **real past-year
questions** back, with year, question number, topic and the **official answer
key**. Built to be a *retrieval system with a number attached*, not a chatbot.

Owner: Mahesh (`mahesahoo`). Public repo. Original planning doc `SCOPE.md` is
deliberately **untracked** (it contained private business context) — it stays
local only.

## Hard rules
1. **No LLM generation.** Answers come from the organisers' key, never generated.
   Adding a generator to a 0.70 hit@1 retriever produces confident wrong answers.
2. **Every number in the README must be reproducible** with `python eval.py`.
   If it changes, update the README in the same commit.
3. **Corpus provenance is official only** — IIT Madras PDFs, no third-party copies.
4. **GA questions are excluded** (only Q11+ ship); figure-dependent questions are
   skipped on purpose. A demo does not need a picture.

## Current numbers (2026-11-24)
```
corpus 155 questions (2024: 53, 2025: 53, 2026: 49)
hit@1 0.70 | hit@3 0.80 | MRR 0.750 | 10 fixed queries
```
Known miss: a paraphrase says "first derivative", the paper writes `f′(x*) = 0`.
That's a vocabulary gap BM25 cannot close — it is the argument for embeddings,
not a bug to paper over.

## How to run
```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python build_corpus.py     # data/*.pdf -> gatewise/questions.jsonl
python eval.py             # prints hit@1 / hit@3 / MRR
python ask.py "hash table linear probing"
streamlit run app.py
```
`data/*.pdf` is gitignored (~10 MB each). Re-download from
`https://gate2027.iitm.ac.in/static/doc/download/` with the filenames listed in
the README table, or `build_corpus.py` fails loudly.

## Decisions
- **BM25, zero dependencies** (`gatewise/bm25.py`). 155 docs; a vector store would
  be decoration and would hide the baseline.
- **Coverage floor (`min_coverage=0.3`) instead of `score > 0`.** BM25 never
  returns nothing — any shared rare token scores above zero, so unrelated queries
  got three confident-looking answers. This single change took the out-of-corpus
  case from 3 false hits to 0.
- **Stopwords in the tokeniser.** Question words inflate coverage and carry no signal.
- **Answers are strings as printed**: `A` / `A;C` for MSQ / `0.25 to 0.25` for NAT /
  `MTA` where the key says so. Don't "normalise" them into floats.
- **Three key formats, one parser.** 2025's key explodes every table cell onto its
  own line; normalising whitespace is what makes a single regex fit all years.

## Gotchas
- `gatewise/corpus.py` used to *write placeholder data* if `questions.jsonl` was
  missing. It now raises instead — never reintroduce synthetic questions.
- Topic labels are keyword-mapped, so ~23% land in `general`. That's known, not a bug.
- pypdf extracts math notation with lost arrows (`A→B` → `AB`) in a few 2026
  records. Tolerable; affects display, not retrieval.

## Next
- Deploy `app.py` to Streamlit Community Cloud so the portfolio card can link a demo.
- Embeddings as a second retriever, compared head-to-head on hit@3.
- Hand-check the `general` topic labels, then rebuild the corpus.

## Feedback log
Append dated one-liners here. Don't rewrite past entries.
- 2026-11-24 — `SCOPE.md` is untracked on purpose (private business context). Never commit it.
- 2026-11-24 — Report the first eval number BEFORE tuning, and keep the failed case in the README.
