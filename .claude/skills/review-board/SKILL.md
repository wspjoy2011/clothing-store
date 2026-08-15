---
name: review-board
description: Run an independent three-role review — architect, tech lead and senior developer — over uncommitted changes, a branch or a pull request. Each reviewer forms its own verdict against CLAUDE.md and the findings are printed to the console. Use when asked to review code, review a PR, get a second opinion, or check whether a change is ready to merge. Never posts comments to GitHub.
---

# Review board

Three reviewers examine the same change from different angles and report independently. Their disagreement is the useful part — do not smooth it over.

## Rules

1. **Console only.** Never run `gh pr comment`, `gh pr review`, or write to any issue or pull request. The entire output is text in the terminal. This holds even when the review target is a pull request.
2. **Independent.** Reviewers receive the change and the repository conventions, never your opinion of the change, and never each other's findings. Do not tell them what you think is wrong, what the author intended, or that the code was written by you.
3. **`CLAUDE.md` is the standard.** Every reviewer reads it first. A convention violation cites the rule it breaks. When `CLAUDE.md` is silent, that is not a violation — at most a suggestion to add the rule.
4. **Read-only.** Reviewers do not edit files, do not fix what they find, and do not commit. Fixing is a separate decision made after the report.

## Steps

### 1. Pick the target

- an explicit pull request number → `--target pr --pr <number>`
- an explicit branch or base → `--target branch --base <ref>`
- uncommitted work in progress → `--target worktree`
- nothing specified → `--target branch` against the default base

### 2. Collect one snapshot

```
python .claude/skills/review-board/scripts/collect_review_context.py --target <target> --output <temp file>
```

Every reviewer reads this one file, so all findings refer to identical code. The script prints the path it wrote.

### 3. Run the three reviewers in parallel

Send all three in a single message so they run concurrently. Give each one:

- the path to the snapshot,
- the path to its role file under `.claude/skills/review-board/roles/`,
- the instruction to read `CLAUDE.md` before judging,
- the ref holding the reviewed code, and the instruction to read files with `git show <ref>:<path>` rather than from the working tree — the diff alone rarely tells the whole story, but the working tree may sit on a different branch or be switched mid-review, and files read from it would then belong to different code than the diff.

Roles: `architect.md`, `tech-lead.md`, `senior-developer.md`.

Require each reviewer to return:

- a verdict — `approve`, `approve with follow-up`, or `request changes`,
- findings, each with severity (`blocker`, `major`, `minor`), `file:line`, what breaks concretely, and the `CLAUDE.md` rule when one applies,
- what it deliberately did not check.

### 4. Report to the console

Print, in this order:

1. **Verdicts** — one line per reviewer with its decision.
2. **Blockers** — every blocker, grouped by file, each with the reviewer who raised it.
3. **Major and minor findings** — same grouping, severity descending.
4. **Disagreements** — where reviewers reached opposite conclusions on the same code. Present both positions; do not pick a winner silently.
5. **Convention violations** — findings that cite `CLAUDE.md`, listed separately so the rules stay visible.
6. **Not covered** — what no reviewer checked, so the gap is explicit.

Report findings as they came back. Do not soften a verdict because you wrote the code, and do not amplify one to look thorough. If a reviewer is wrong, say so and explain why, rather than dropping the finding.

### 5. Stop

The skill ends with the report. Fixing anything is a separate request.
