"""Collect a single snapshot of the changes under review.

All reviewers read the same snapshot so their findings refer to identical code.
"""

import argparse
import json
import subprocess
import sys
from typing import List, Optional

DEFAULT_MAX_DIFF_BYTES = 200_000

GENERATED_FILES = (
    ":(exclude)*.lock",
    ":(exclude)*lock.json",
    ":(exclude)*.min.js",
    ":(exclude)*.min.css",
)


def run_git(arguments: List[str]) -> str:
    """
    Run a git command and return its output

    Args:
        arguments: Git arguments without the leading executable name

    Returns:
        Command output, or an empty string when the command fails
    """
    try:
        completed = subprocess.run(
            ["git", *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
    except FileNotFoundError:
        return ""

    if completed.returncode != 0:
        return ""

    return completed.stdout.strip()


def resolve_default_base() -> str:
    """
    Resolve the branch a feature branch is normally compared against

    Returns:
        Name of the base branch
    """
    head = run_git(["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"])
    if head:
        return head

    for candidate in ("origin/main", "origin/master", "main", "master"):
        if run_git(["rev-parse", "--verify", "--quiet", candidate]):
            return candidate

    return "HEAD~1"


def collect_pull_request(number: str) -> Optional[dict]:
    """
    Collect pull request metadata and diff through the GitHub CLI

    Args:
        number: Pull request number

    Returns:
        Mapping with pull request fields, or None when the CLI is unavailable
    """
    try:
        metadata = subprocess.run(
            ["gh", "pr", "view", number, "--json", "title,body,baseRefName,headRefName,commits,files"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        diff = subprocess.run(
            ["gh", "pr", "diff", number],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
    except FileNotFoundError:
        return None

    if metadata.returncode != 0 or diff.returncode != 0:
        return None

    return {"metadata": metadata.stdout, "diff": diff.stdout}


def render_pull_request_metadata(raw: str) -> str:
    """
    Render pull request metadata as a readable summary

    Args:
        raw: JSON returned by the GitHub CLI

    Returns:
        Markdown summary, falling back to the raw payload when it cannot be parsed
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return f"## Metadata\n\n```json\n{raw.strip()}\n```\n"

    lines = [
        "## Pull request\n",
        f"- title: {data.get('title', '')}",
        f"- branches: {data.get('headRefName', '')} -> {data.get('baseRefName', '')}",
    ]

    commits = data.get("commits") or []
    if commits:
        lines.append("\n### Commits\n")
        lines.extend(f"- {commit.get('messageHeadline', '')}" for commit in commits)

    files = data.get("files") or []
    if files:
        lines.append("\n### Files\n")
        lines.extend(
            f"- {item.get('path', '')} (+{item.get('additions', 0)}/-{item.get('deletions', 0)})"
            for item in files
        )

    description = (data.get("body") or "").strip()
    if description:
        lines.append(f"\n### Description as written by the author\n\n{description}\n")

    return "\n".join(lines) + "\n"


def truncate(text: str, limit: int) -> str:
    """
    Shorten text that exceeds the allowed size

    Args:
        text: Text to shorten
        limit: Maximum number of bytes to keep

    Returns:
        Text within the limit, marked when it was cut
    """
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text

    kept = encoded[:limit].decode("utf-8", errors="ignore")
    dropped = len(encoded) - limit
    return f"{kept}\n\n[diff truncated, {dropped} bytes omitted — review the listed files directly]"


def build_report(target: str, base: str, pull_request: Optional[str], max_diff_bytes: int) -> str:
    """
    Build the review snapshot

    Args:
        target: One of worktree, branch or pr
        base: Ref the branch is compared against
        pull_request: Pull request number when target is pr
        max_diff_bytes: Maximum diff size to include

    Returns:
        Snapshot rendered as markdown
    """
    sections: List[str] = []

    if target == "pr":
        collected = collect_pull_request(pull_request)
        if collected is None:
            return "Unable to read the pull request. Is the GitHub CLI installed and authenticated?"

        sections.append("# Review target: pull request\n")
        sections.append(render_pull_request_metadata(collected["metadata"]))
        sections.append(f"## Diff\n\n```diff\n{truncate(collected['diff'], max_diff_bytes)}\n```\n")
        return "\n".join(sections)

    if target == "worktree":
        sections.append("# Review target: uncommitted changes\n")
        stat = run_git(["diff", "HEAD", "--stat"])
        diff = run_git(["diff", "HEAD", "--", *GENERATED_FILES])
        untracked = run_git(["ls-files", "--others", "--exclude-standard"])
        if untracked:
            sections.append(f"## Untracked files\n\n```\n{untracked}\n```\n")
    else:
        sections.append(f"# Review target: branch against {base}\n")
        commits = run_git(["log", "--oneline", f"{base}..HEAD"])
        sections.append(f"## Commits\n\n```\n{commits or 'no commits ahead of base'}\n```\n")
        stat = run_git(["diff", f"{base}...HEAD", "--stat"])
        diff = run_git(["diff", f"{base}...HEAD", "--", *GENERATED_FILES])

    sections.append(f"## Changed files\n\n```\n{stat or 'no changes'}\n```\n")
    sections.append(f"## Diff\n\n```diff\n{truncate(diff, max_diff_bytes) if diff else 'no changes'}\n```\n")

    return "\n".join(sections)


def main() -> int:
    """
    Parse arguments and print the review snapshot

    Returns:
        Process exit code
    """
    parser = argparse.ArgumentParser(description="Collect the changes under review")
    parser.add_argument("--target", choices=("worktree", "branch", "pr"), default="branch")
    parser.add_argument("--base", default=None, help="Ref to compare the branch against")
    parser.add_argument("--pr", default=None, help="Pull request number when target is pr")
    parser.add_argument("--max-diff-bytes", type=int, default=DEFAULT_MAX_DIFF_BYTES)
    parser.add_argument("--output", default=None, help="Write the snapshot to this file instead of stdout")
    arguments = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if arguments.target == "pr" and not arguments.pr:
        parser.error("--pr is required when --target is pr")

    base = arguments.base or resolve_default_base()
    report = build_report(arguments.target, base, arguments.pr, arguments.max_diff_bytes)

    if arguments.output:
        with open(arguments.output, "w", encoding="utf-8") as handle:
            handle.write(report)
        print(arguments.output)
        return 0

    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
