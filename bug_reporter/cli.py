import os
import webbrowser
from pathlib import Path

import typer
from dotenv import load_dotenv

from bug_reporter.drafter import draft_report, to_markdown
from bug_reporter.github import create_issue

# Load the project's .env no matter which folder the command is run from
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = typer.Typer(add_completion=False)


def _ask_screenshot() -> Path | None:
    """Prompt for a screenshot path; dragging a file into the terminal pastes its path."""
    while True:
        raw = typer.prompt(
            "Screenshot (drag the file here, or press Enter to skip)",
            default="", show_default=False,
        ).strip().strip("'\"").replace("\\ ", " ")
        if not raw:
            return None
        path = Path(raw).expanduser()
        if path.is_file():
            return path
        typer.secho(f"No file at {path}, try again.", fg="red")


@app.command()
def report(
    description: str | None = typer.Argument(
        None, help="What went wrong, in your own words. Asked for if left out."
    ),
    screenshot: Path | None = typer.Option(
        None, "--shot", "-s", exists=True, dir_okay=False, help="Screenshot of the bug."
    ),
    repo: str | None = typer.Option(None, "--repo", "-r", help="owner/name; overrides GITHUB_REPO."),
    board: str | None = typer.Option(
        None, "--board", "-b", help="Board key, e.g. rama or cbhi; reads <KEY>_GITHUB_PROJECT and <KEY>_GITHUB_REPO from .env."
    ),
    project: str | None = typer.Option(None, "--project", "-p", help="Board title; overrides --board and GITHUB_PROJECT."),
    assign_me: bool = typer.Option(False, "--me", help="Assign the issue to yourself."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip the confirmation prompt."),
    open_browser: bool = typer.Option(True, "--open/--no-open", "-o", help="Open the issue in your browser."),
) -> None:
    """Draft a bug report with AI and file it as a GitHub issue."""
    if not description:
        description = typer.prompt("What's the bug?")
        if not screenshot:
            screenshot = _ask_screenshot()
    if not board and not project:
        board = typer.prompt("Which board? (rama/cbhi)").strip().lower()
    if board:
        key = board.upper()
        repo = repo or os.getenv(f"{key}_GITHUB_REPO")
        project = project or os.getenv(f"{key}_GITHUB_PROJECT")
        if not project:
            typer.secho(f"Set {key}_GITHUB_PROJECT in .env to use --board {board}.", fg="red")
            raise typer.Exit(1)
    repo = repo or os.getenv("GITHUB_REPO")
    if not repo:
        typer.secho("Set GITHUB_REPO in .env or pass --repo owner/name.", fg="red")
        raise typer.Exit(1)
    project = project or os.getenv("GITHUB_PROJECT") or None

    typer.echo("Drafting bug report...")
    bug = draft_report(description, screenshot)
    body = to_markdown(bug)

    typer.secho(f"\n{bug.title}\n", bold=True)
    typer.echo(body)
    if not yes and not typer.confirm(f"Create this issue in {repo}?", default=True):
        raise typer.Abort()

    url = create_issue(
        repo, bug.title, body, project=project, labels=["bug"], assign_me=assign_me
    )
    typer.secho(f"\nCreated: {url}", fg="green")
    if screenshot:
        typer.echo(f"Remember to drag {screenshot.name} and your video into the issue.")
    if open_browser:
        webbrowser.open(url)


if __name__ == "__main__":
    app()
