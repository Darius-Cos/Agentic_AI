"""Streamlit UI for the Autonomous Research Agent."""

import asyncio

import streamlit as st

from agent import ResearchAgentRunner
from utils.config import MAX_ITERATIONS

st.set_page_config(
    page_title="Autonomous Research Agent",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 Autonomous Research Agent")
st.caption(
    "Powered by Gemini 2.0 Flash · ADK · FAISS · Tavily · Yahoo Finance via MCP"
)

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    max_iter = st.slider(
        "Max refinement iterations",
        min_value=1,
        max_value=5,
        value=MAX_ITERATIONS,
        help="How many Plan→Execute→Critique cycles to run",
    )
    output_format = st.selectbox("Canvas output format", ["markdown", "html"])
    st.divider()
    st.markdown(
        "**Tools available:**\n"
        "- 📄 Document Search (FAISS)\n"
        "- 🌐 Web Search (Tavily)\n"
        "- 💹 Financial Data (Yahoo Finance via MCP)\n"
        "- 🖼️ Canvas (Report Generator)"
    )
    st.divider()
    st.markdown("**Architecture:**\n`Planner → LoopAgent(Executor → Critiquer)`")

# Query input
query = st.text_area(
    "Research question",
    placeholder="e.g. What are the latest advances in RAG systems for enterprise AI?",
    height=100,
)

col1, col2 = st.columns([1, 4])
with col1:
    run_button = st.button("🚀 Research", type="primary", use_container_width=True)

# State for storing results
if "history" not in st.session_state:
    st.session_state.history = []


async def _run(q: str, max_iterations: int) -> str:
    runner = ResearchAgentRunner()
    return await runner.run(q, max_iterations=max_iterations)


if run_button and query.strip():
    with st.spinner("Running research pipeline... (Plan → Execute → Critique → Refine)"):
        try:
            answer = asyncio.run(_run(query.strip(), max_iter))
            st.session_state.history.append({"query": query.strip(), "answer": answer})
        except Exception as e:
            st.error(f"Agent error: {e}")
            answer = None

# Display results
if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(
            f"Q: {item['query'][:80]}{'...' if len(item['query']) > 80 else ''}",
            expanded=(i == 0),
        ):
            st.markdown(item["answer"])
            st.download_button(
                label="⬇ Download answer",
                data=item["answer"],
                file_name=f"research_{i}.md",
                mime="text/markdown",
                key=f"dl_{i}",
            )
