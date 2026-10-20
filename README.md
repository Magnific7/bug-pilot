# bug-reporter

Transform quick bug notes into polished, ready-to-edit GitHub issues with Gemini AI.

You describe what went wrong in plain words, straight from your terminal. Gemini reads your
description and screenshot, picks up details like error messages and what's on screen, and
writes a clear bug report: a title, summary, steps to reproduce, expected and actual
behaviour, and severity. You check the draft, then the tool creates the issue with a `bug`
label, adds it to your project board and opens it in your browser so you can attach your
screenshot and video.

## Run it

From any folder, in any terminal:

```bash
bug
```

It asks for the bug, a screenshot (drag the file into the terminal) and the board, shows you
the draft, then creates the issue and opens it so you can attach a video.

Or do it in one line:

```bash
bug "Export button does nothing on Safari" --shot ~/Desktop/err.png --board web
```

First time? Do the setup below. It also sets up the `bug` command.

## Setup (once)

You need Python 3.11+, the [GitHub CLI](https://cli.github.com) (`brew install gh`) and a
[Gemini API key](https://aistudio.google.com/apikey).

```bash
git clone <this-repo-url> bug-reporter && cd bug-reporter
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
gh auth login && gh auth refresh -s project
cp .env.example .env    # then fill it in, see below

# Add the bug command so it works from any folder
echo "alias bug=\"$PWD/.venv/bin/bugreport\"" >> ~/.zshrc && source ~/.zshrc
```

On bash, use `~/.bashrc` instead of `~/.zshrc`. Open terminals pick up `bug` after
`source ~/.zshrc`; new ones have it automatically.

## Fill in `.env`

```bash
GEMINI_API_KEY="your-gemini-api-key"

WEB_GITHUB_REPO="your-org/your-repo"        # repo the issue is created in
WEB_GITHUB_PROJECT="Your Board Title"       # board the issue is added to
```

- The board title must match GitHub exactly. Use the title, not the URL.
  To list them: `gh project list --owner name_of_owner`
- `.env` is ignored by git, so your key and settings stay on your machine.

## Rename a board or add more

Each board is a pair of lines in `.env`. The start of the name is what you type after `--board`:

| In `.env` | Command |
|-----------|---------|
| `WEB_GITHUB_REPO`, `WEB_GITHUB_PROJECT` | `bug --board web` |
| `MOBILE_GITHUB_REPO`, `MOBILE_GITHUB_PROJECT` | `bug --board mobile` |

- **Rename a board:** change the start of both names, e.g. `WEB_` to `SHOP_` gives `--board shop`.
- **Add a board:** add another pair of lines with a new name. No code changes needed.
- `_GITHUB_PROJECT` is required. Leave out `_GITHUB_REPO` to use the `GITHUB_REPO` line instead.
- Use only letters, numbers and underscores in board names, e.g. `shop` or `web_app`.
- **Update the guided prompt:** it lists board names from the `Which board? (...)` line in
  [bug_reporter/cli.py](bug_reporter/cli.py). Edit the names in brackets to match yours.

## Options

| Flag | Meaning |
|------|---------|
| `--shot, -s` | Screenshot for Gemini to read (`.png`, `.jpg`, `.jpeg`, `.webp`) |
| `--board, -b` | Board name from `.env` |
| `--repo, -r` | Repo as `owner/name`; overrides the board's repo |
| `--project, -p` | Board title; overrides the board's title |
| `--me` | Assigns the issue to you |
| `--yes, -y` | Skips the confirmation step |
| `--no-open` | Doesn't open the issue in your browser |

GitHub's API can't upload files, so attach the screenshot and video in the browser.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `command not found: bug` | Run `source ~/.zshrc`, or redo the last line of setup from the project folder |
| `GEMINI_API_KEY is not set` | Add your key to `.env` |
| `Set WEB_GITHUB_PROJECT in .env...` | Add that board's title to `.env` |
| `gh issue create failed` mentioning scopes | Run `gh auth refresh -s project` |
| `gh issue create failed` saying `not found` | Use the board's exact title, not its URL |
| `'bug' not found` | Create a `bug` label in the repo under **Issues → Labels** |
