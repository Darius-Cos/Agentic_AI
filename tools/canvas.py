"""ADK tool: Canvas — generate structured reports and code snippets."""

import json

from canvas.generator import (
    ReportInput,
    ReportSection,
    generate_code_snippet,
    generate_report,
)


def canvas_tool(
    output_type: str,
    title: str,
    content_json: str,
    output_format: str = "markdown",
) -> str:
    """Generate a structured document or code snippet (Canvas tool).

    Use this tool when the user asks for a report, summary document, or code snippet
    based on research collected so far.

    Args:
        output_type: Either 'report' or 'code'.
        title: Title of the document or description of the code snippet.
        content_json: For 'report': JSON string matching ReportInput schema
            (fields: summary, sections, conclusions, recommendations).
            For 'code': JSON string with fields 'language' and 'content'.
        output_format: For reports: 'markdown' (default) or 'html'.

    Returns:
        The rendered document as a string.
    """
    try:
        data = json.loads(content_json)
    except json.JSONDecodeError as e:
        return f"Canvas error: content_json is not valid JSON. {e}"

    if output_type == "report":
        sections = [
            ReportSection(
                heading=s.get("heading", ""),
                content=s.get("content", ""),
                sources=s.get("sources", []),
            )
            for s in data.get("sections", [])
        ]
        report_input = ReportInput(
            title=title,
            summary=data.get("summary", ""),
            sections=sections,
            conclusions=data.get("conclusions", ""),
            recommendations=data.get("recommendations", []),
            output_format=output_format,  # type: ignore[arg-type]
        )
        return generate_report(report_input)

    elif output_type == "code":
        return generate_code_snippet(
            language=data.get("language", "python"),
            description=title,
            content=data.get("content", ""),
        )

    return f"Canvas error: unknown output_type '{output_type}'. Use 'report' or 'code'."
