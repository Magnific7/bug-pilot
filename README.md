# bug-reporter

Describe a bug in plain words, optionally attach a screenshot, and get a GitHub
issue on your project board. The tool prints the issue link so you can add a video.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env          # then fill in your values
gh auth refresh -s project    # gh needs the "project" scope to add issues to a board
```

The target repo needs a `bug` label (GitHub creates one by default).

## Usage

Run `bugreport` with no arguments and it asks for the bug, a screenshot (drag the file into
the terminal) and the board. Or pass everything at once:

```bash
bugreport "Export button does nothing on Safari after picking CSV" --shot ~/Desktop/err.png --board rama
```

| Flag | Meaning |
|------|---------|
| `--shot, -s` | Screenshot that Gemini reads to write a better report |
| `--repo, -r` | Overrides `GITHUB_REPO` |
| `--board, -b` | Picks a board from `.env`: `--board rama` reads `RAMA_GITHUB_PROJECT` and `RAMA_GITHUB_REPO` |
| `--project, -p` | Board title; overrides `--board` and `GITHUB_PROJECT` |
| `--me` | Assigns the issue to you |
| `--yes, -y` | Skips the confirmation prompt |
| `--no-open` | Doesn't open the new issue in your browser (it opens by default) |

GitHub's API can't attach images or videos to issues, so the screenshot is used
only to write the report. Drag the screenshot and video into the issue in the browser.
