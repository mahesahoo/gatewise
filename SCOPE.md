# GATEwise — ship cut, Nov 14 → Nov 20

**One sentence:** ask a GATE DA question in plain English, get the top matching past-year questions back with their year, number, topic and answer — with a measured hit-rate.

Not a product. A deployed, cited retrieval system with a number attached.

## What ships

- A corpus of GATE DA past-year questions as `data/questions.jsonl` (question, options, answer, year, qno, topic).
- A retrieval engine (BM25 first — no GPU, no downloads, runs anywhere).
- `ask.py` — CLI: query in, top-3 matches with full citation out.
- `eval.py` — 10 hand-written queries → hit@1 and hit@3, printed as a table.
- Streamlit app: same thing in a browser.
- Public link + README with the eval number and a screenshot.

## What does NOT ship

No LLM generation, no chat history, no auth, no user accounts, no fine-tuning, no embeddings until the eval number exists and is honest. If time remains on day 5, add embeddings as a second retriever and compare hit@3 head-to-head — that comparison is worth more than any UI.

## Six days

| Day | Date | Deliverable | Proof |
|---|---|---|---|
| 1 | Sat 14 Nov | corpus file + BM25 index + `ask.py` running on real data | terminal output |
| 2 | Sun 15 Nov | `eval.py`, 10 queries, hit@1/hit@3 printed | number on screen |
| 3 | Mon 16 Nov | fix chunking/tokenisation to raise hit@3; record before/after | commit + numbers |
| 4 | Tue 17 Nov | Streamlit app running locally | screenshot |
| 5 | Wed 18 Nov | deployed, public URL, README with metrics | live link |
| 6 | Thu 19 Nov | buffer: embeddings retriever if ahead, otherwise polish + post | ship |

**Ship day is the 19th.** The 20th is empty on purpose.

## The rule for these six days

One deliverable per day, in the repo, with proof in the message. No new page, no new system, no scope added. If a day is missed, the next day does not double up — it continues.

## Why BM25 first

It proves the pipeline end-to-end in one evening with zero installs, gives an honest baseline number, and makes any later embedding upgrade a *measured* improvement rather than a rewrite. A cited answer with hit@3 = 0.9 is a stronger artifact than an impressive demo with no number.
