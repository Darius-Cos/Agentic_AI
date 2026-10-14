"""Canvas: structured report and code snippet generator using Jinja2."""

from __future__ import annotations

import pathlib
from datetime import datetime, timezone
from typing import Literal

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field

TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"
_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=False)


class ReportSection(BaseModel):
    heading: str
    content: str
    sources: list[str] = Field(default_factory=list)


class ReportInput(BaseModel):
    title: str
    summary: str
    sections: list[ReportSection]
    conclusions: str = ""
    recommendations: list[str] = Field(default_factory=list)
    author: str = "Autonomous Research Agent"
    output_format: Literal["markdown", "html"] = "markdown"


def generate_report(data: ReportInput) -> str:
    """Render a structured report using Jinja2 templates."""
    template_file = (
        "report.md.j2" if data.output_format == "markdown" else "report.html.j2"
    )
    template = _env.get_template(template_file)
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return template.render(
        title=data.title,
        summary=data.summary,
        sections=[s.model_dump() for s in data.sections],
        conclusions=data.conclusions,
        recommendations=data.recommendations,
        author=data.author,
        generated_at=now,
    )


def generate_code_snippet(language: str, description: str, content: str) -> str:
    """Wrap a code snippet with language tag and description header."""
    return f"# {description}\n\n```{language}\n{content}\n```"
