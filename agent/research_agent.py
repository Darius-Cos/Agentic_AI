"""Autonomous Research Agent built with Google ADK.

Architecture (Plan → Execute → Critique → Refine loop):

  RefinementLoop (LoopAgent, max_iterations=N)
  └── ResearchCycle (SequentialAgent)
      ├── Planner  (LlmAgent)  — initial plan OR re-plan from follow_up_queries
      ├── Executor (LlmAgent)  — calls tools, synthesises answer
      └── Critiquer (LlmAgent) — evaluates; calls exit_loop() when COMPLETE
"""

from __future__ import annotations

import vertexai
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from tools.canvas import canvas_tool
from tools.document_search import document_search_tool
from tools.financial_data import financial_data_tool
from tools.web_search import web_search_tool
from utils.config import GCP_LOCATION, GCP_PROJECT, GEMINI_MODEL, MAX_ITERATIONS

from .exit_loop import exit_loop
from .prompts import (
    CRITIQUE_INSTRUCTION,
    EXECUTOR_INSTRUCTION,
    ORCHESTRATOR_INSTRUCTION,
    PLANNER_INSTRUCTION,
)

APP_NAME = "autonomous_research_agent"
_vertex_initialised = False


def _init_vertex() -> None:
    global _vertex_initialised
    if not _vertex_initialised:
        vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
        _vertex_initialised = True


def build_agent(max_iterations: int = MAX_ITERATIONS) -> LoopAgent:
    """Construct and return the research agent pipeline."""
    _init_vertex()

    # Planner: initial plan OR re-plan using follow_up_queries from previous critique
    planner = LlmAgent(
        name="planner",
        model=GEMINI_MODEL,
        instruction=PLANNER_INSTRUCTION,
        output_key="research_plan",
    )

    # Executor: calls all 4 tools, synthesises answer
    executor = LlmAgent(
        name="executor",
        model=GEMINI_MODEL,
        instruction=EXECUTOR_INSTRUCTION,
        tools=[
            document_search_tool,
            web_search_tool,
            financial_data_tool,
            canvas_tool,
        ],
        output_key="current_answer",
    )

    # Critiquer: evaluates answer; calls exit_loop() to set actions.escalate=True when done
    critiquer = LlmAgent(
        name="critiquer",
        model=GEMINI_MODEL,
        instruction=CRITIQUE_INSTRUCTION,
        tools=[exit_loop],
        output_key="critique_result",
    )

    # One full cycle: plan → execute → critique
    research_cycle = SequentialAgent(
        name="research_cycle",
        sub_agents=[planner, executor, critiquer],
    )

    # Loop until critiquer calls exit_loop() or max_iterations reached
    return LoopAgent(
        name="refinement_loop",
        sub_agent=research_cycle,
        max_iterations=max_iterations,
        description=ORCHESTRATOR_INSTRUCTION,
    )


class ResearchAgentRunner:
    """High-level runner that wraps the ADK agent pipeline."""

    def __init__(self) -> None:
        self._session_service = InMemorySessionService()

    async def run(
        self,
        query: str,
        max_iterations: int = MAX_ITERATIONS,
        user_id: str = "default",
    ) -> str:
        """Run the full research pipeline and return the final synthesised answer."""
        # Rebuild agent per call so max_iterations is honoured correctly
        agent = build_agent(max_iterations=max_iterations)
        runner = Runner(
            agent=agent,
            app_name=APP_NAME,
            session_service=self._session_service,
        )

        session = await self._session_service.create_session(
            app_name=APP_NAME, user_id=user_id
        )

        message = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=query)],
        )

        final_answer = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=message,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_answer = event.content.parts[0].text or ""

        # Prefer the executor's synthesised answer from session state
        session_obj = await self._session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session.id
        )
        if session_obj and hasattr(session_obj, "state"):
            answer = session_obj.state.get("current_answer", "")
            if answer:
                return answer

        return final_answer or "No answer generated."
