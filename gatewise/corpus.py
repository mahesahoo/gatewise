"""Sample corpus — replace with real GATE DA past-year questions.

One JSON object per line:
  {"year": 2024, "qno": 12, "topic": "probability", "question": "...",
   "options": ["a", "b", "c", "d"], "answer": "b", "text": "searchable blob"}

`text` is what the retriever indexes: question + options + answer.
The three entries below are placeholders written to make the pipeline
testable. They are NOT real PYQs and must be replaced before the demo ships.
"""
import json
import pathlib

DATA = pathlib.Path(__file__).parent / "questions.jsonl"

if not DATA.exists():
    DATA.write_text(
        "\n".join(
            json.dumps(r)
            for r in [
                {
                    "year": 0,
                    "qno": 1,
                    "topic": "placeholder",
                    "question": "What is the expected value of a fair six-sided die roll?",
                    "options": ["3", "3.5", "4", "4.5"],
                    "answer": "3.5",
                    "text": "expected value fair six-sided die roll E[X] mean of uniform distribution 3.5",
                },
                {
                    "year": 0,
                    "qno": 2,
                    "topic": "placeholder",
                    "question": "Eigenvalues of a symmetric real matrix are always:",
                    "options": ["zero", "real", "purely imaginary", "complex conjugates"],
                    "answer": "real",
                    "text": "eigenvalues symmetric real matrix spectral theorem always real linear algebra",
                },
                {
                    "year": 0,
                    "qno": 3,
                    "topic": "placeholder",
                    "question": "Bayes rule denominator is also known as:",
                    "options": ["prior", "likelihood", "marginal", "posterior"],
                    "answer": "marginal",
                    "text": "bayes theorem posterior prior likelihood marginal evidence denominator probability",
                },
            ]
        )
    )


def load(path=None):
    p = pathlib.Path(path) if path else DATA
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
