"""ADK tool that terminates the LoopAgent by setting actions.escalate = True."""

from google.adk.tools.tool_context import ToolContext


def exit_loop(tool_context: ToolContext) -> dict:
    """Terminate the research refinement loop because quality is sufficient.

    Call this tool ONLY when verdict is COMPLETE and quality_score >= 8.
    Do NOT call it when verdict is NEEDS_REFINEMENT.
    """
    tool_context.actions.escalate = True
    return {"status": "complete", "message": "Research quality sufficient. Loop terminated."}
