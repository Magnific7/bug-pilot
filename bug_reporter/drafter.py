import os
from pathlib import Path

from google import genai
from google.genai import types
from pydantic import BaseModel

DEFAULT_MODEL = "gemini-3.5-flash-lite"

MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

PROMPT = """You are a QA engineer writing a GitHub bug report.
Turn the user's description (and the screenshot, if one is attached) into a clear,
concise bug report. Use details visible in the screenshot, such as error messages,
URLs, and UI state. Do not invent steps you can't infer; write "Unknown" instead.
Severity must be one of: low, medium, high, critical.

User description:
{description}"""


class BugReport(BaseModel):
    title: str
    summary: str
    steps_to_reproduce: list[str]
    expected: str
    actual: str
    environment: str
    severity: str


def draft_report(description: str, screenshot: Path | None = None) -> BugReport:
    """Ask Gemini to turn a free-text description into a structured bug report."""
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")

    contents: list = [PROMPT.format(description=description)]
    if screenshot:
        mime_type = MIME_TYPES.get(screenshot.suffix.lower())
        if not mime_type:
            raise ValueError(f"Unsupported screenshot type: {screenshot.suffix}")
        contents.append(
            types.Part.from_bytes(data=screenshot.read_bytes(), mime_type=mime_type)
        )

    client = genai.Client()
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        contents=contents,
        config={
            "response_mime_type": "application/json",
            "response_schema": BugReport,
        },
    )
    if not response.text:
        raise RuntimeError("The AI model returned an empty response.")

    return BugReport.model_validate_json(response.text)


def to_markdown(report: BugReport) -> str:
    steps = "\n".join(
        f"{i}. {step}" for i, step in enumerate(report.steps_to_reproduce, 1)
    )
    return (
        f"## Summary\n{report.summary}\n\n"
        f"## Steps to reproduce\n{steps}\n\n"
        f"## Expected behaviour\n{report.expected}\n\n"
        f"## Actual behaviour\n{report.actual}\n\n"
        f"## Environment\n{report.environment}\n\n"
        f"**Severity:** {report.severity}\n\n"
        "## Screenshots / Video\n_To be attached._\n"
    )
