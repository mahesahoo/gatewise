"""app.py — GATEwise: ask a GATE DA question in plain English.

    streamlit run app.py

BM25 over real past-year questions. No LLM, no API key, no download at runtime.
"""
import streamlit as st

from gatewise.bm25 import BM25
from gatewise.corpus import load

EVAL = {"hit@1": "7/10", "hit@3": "8/10", "mrr": "0.750"}

EXAMPLES = [
    "chance of getting two or more heads when three coins are tossed",
    "hash table size 10 with linear probing",
    "what does relu do to negative inputs",
    "functional dependency candidate keys",
]

st.set_page_config(page_title="GATEwise", page_icon="🎯", layout="centered")


@st.cache_data(show_spinner=False)
def corpus():
    return load()


@st.cache_resource(show_spinner=False)
def index():
    return BM25(corpus())


docs = corpus()

st.title("GATEwise")
st.caption(
    f"Ask in plain English. Cited answers from {len(docs)} real GATE DA questions "
    f"(2024–2026), each with year, question number and the official key. "
    f"BM25 retrieval — no LLM in the loop."
)

query = st.text_input(
    "Your question",
    placeholder="e.g. probability of two heads in three coin tosses",
)

if not query.strip():
    st.markdown("**Try one of these**")
    cols = st.columns(2)
    for i, example in enumerate(EXAMPLES):
        if cols[i % 2].button(example, use_container_width=True):
            query = example

if query.strip():
    matches = index().top(query, k=3)
    if not matches:
        st.warning("No matches — the corpus does not cover this yet. It only holds GATE DA questions from 2024–2026.")
    else:
        st.markdown(f"**{len(matches)} closest question(s)**")
        for m in matches:
            st.markdown(
                f"**{m['year']} · Q{m['qno']} · {m['topic'].replace('_', ' ')}**"
            )
            st.markdown(m["question"])
            if m["options"]:
                st.markdown("\n".join(f"- **({chr(65 + i)})** {opt}" for i, opt in enumerate(m["options"])))
            st.success(f"Official answer: **{m['answer']}**")
            st.divider()

with st.sidebar:
    st.header("How good is it?")
    st.metric("hit@1", EVAL["hit@1"])
    st.metric("hit@3", EVAL["hit@3"])
    st.metric("MRR", EVAL["mrr"])
    st.caption("10 hand-written queries, targets fixed before measuring. `python eval.py` reproduces this.")
    st.divider()
    st.caption("Corpus: official IIT Madras question papers and answer keys, GA questions dropped, figure-dependent questions dropped.")
