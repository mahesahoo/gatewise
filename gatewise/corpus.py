"""corpus.py — load the generated question corpus.

`questions.jsonl` is built from the official GATE DA papers and answer keys by
`build_corpus.py`. One JSON object per line:

  {"year": 2024, "qno": 12, "topic": "probability", "question": "...",
   "options": ["a", "b", "c", "d"], "answer": "b", "text": "searchable blob"}

`text` is what the retriever indexes: year + question + options + answer + topic.
"""
import json
import pathlib

DATA = pathlib.Path(__file__).parent / "questions.jsonl"


def load(path=None):
    p = pathlib.Path(path) if path else DATA
    if not p.exists():
        raise FileNotFoundError(f"{p} is missing — run `python build_corpus.py` first")
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
