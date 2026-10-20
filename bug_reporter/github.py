import shutil
import subprocess


def create_issue(
    repo: str,
    title: str,
    body: str,
    *,
    project: str | None = None,
    labels: list[str] | None = None,
    assign_me: bool = False,
) -> str:
    """Create a GitHub issue with the gh CLI and return its URL."""
    if not shutil.which("gh"):
        raise RuntimeError("The GitHub CLI (gh) is not installed: brew install gh")

    cmd = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body]
    for label in labels or []:
        cmd += ["--label", label]
    if project:
        cmd += ["--project", project]
    if assign_me:
        cmd += ["--assignee", "@me"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh issue create failed:\n{result.stderr.strip()}")

    # gh prints the new issue's URL as the last line of stdout
    return result.stdout.strip().splitlines()[-1]
