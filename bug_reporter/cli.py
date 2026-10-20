import os
import webbrowser
from pathlib import Path

import typer
from dotenv import load_dotenv

from bug_reporter.drafter import draft_report, to_markdown
from bug_reporter.github import create_issue

load_dotenv()

app = typer.Typer(add_completion=False)


@app.command()
def report(
    description: str = typer.Argument(..., help="What went wrong, in your own words."),
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
    open_browser: bool = typer.Option(False, "--open", "-o", help="Open the issue in your browser."),
) -> None:
    """Draft a bug report with AI and file it as a GitHub issue."""
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
