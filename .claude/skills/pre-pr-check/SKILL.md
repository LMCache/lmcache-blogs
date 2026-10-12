---
name: pre-pr-check
description: Check local changes against this repo's standards and fix what is mechanically fixable, before creating a PR
allowed-tools: Bash, Read, Edit, Write, Grep, Glob, Agent
argument-hint: "[--scope uncommitted|branch|staged] [--fix|--check-only]"
---

# Pre-PR Check

Check the current changes against `AGENTS.md`, and fix what can be fixed
mechanically. Run this skill before `/create-pr`.

## Arguments

- `--scope` (default: `branch`)
  - `uncommitted`: unstaged and staged changes against `HEAD`
  - `staged`: staged changes only
  - `branch`: every commit on this branch that is not in `main` (the full PR
    diff, as a reviewer sees it)
- `--fix` (default): fix what is mechanically fixable
- `--check-only`: report only; change nothing

## Workflow

### Step 0: Load the standard

Read `AGENTS.md`, which is authoritative, especially § Commit Authorship,
§ Writing Prose, and § Pipeline-Specific Rules for Agents.

### Step 1: Detect scope

```bash
git status --short
git branch --show-current
```

| Scope | Diff | File list |
|---|---|---|
| `uncommitted` | `git diff HEAD` | `git diff --name-only HEAD` |
| `staged` | `git diff --cached` | `git diff --cached --name-only` |
| `branch` | `git diff main...HEAD` | `git diff --name-only main...HEAD` |

If the scope has no changes, say so and stop.

### Step 2: Read the changed files

Read the full content of each changed file, not only the diff. For a large
change, ask the Explore agent for a per-file summary first.

### Step 3: Run the checks

#### A. Mechanical (fix unless `--check-only`)

1. Prose over 80 columns in any `.md` file under `docs/`, in `README.md`, or
   in a template. Rewrap only the lines you changed; reflowing untouched
   paragraphs makes a small diff large.
2. Skeleton drift. If `.github/ISSUE_TEMPLATE/blog-post.md` changed, copy it:
   `cp .github/ISSUE_TEMPLATE/blog-post.md docs/templates/blog-post-skeleton.md`.
   Always copy from `.github/` to `docs/`, never the reverse.
3. Banned words in prose or in generator instructions: "leverage", "utilize",
   "seamlessly", "revolutionary", "in today's fast-paced world", "delve", and
   "robust solution". Replace each with the plain word.
4. Trailing whitespace, a missing final newline, or CRLF line endings.
5. A missing SPDX header. Every new `.py` file needs
   `# SPDX-License-Identifier: Apache-2.0` on line 1.
6. Python typing gaps (`AGENTS.md` § Python): missing type hints, `Any`, bare
   generics (`list` → `list[str]`), and `Optional[X]` (→ `X | None`).
7. `assert` used for runtime validation. Replace with
   `if not cond: raise ValueError(...)`.
8. Lazy imports. Move them to the top of the file, under the correct section
   heading.

#### B. Docstrings (fix when the purpose is clear; flag when it is not)

9. A public Python function with no docstring. If the purpose is clear, write
   a full docstring (summary, args, returns, and raises). If not, write what
   you can, add `TODO: confirm`, and note it in the report.
10. A stale docstring: a parameter was added or changed, and the docstring
    still describes the old contract.

#### C. Judgment calls (flag only; do not change)

11. A `##` heading in the skeleton was renamed, reordered, or removed, which
    breaks the parser. If the parse-contract table in
    `docs/pipeline/skeleton-to-prompt.md` did not change in the same PR,
    report an error.
12. The issue template, `docs/blog-submission-process.md`, and
    `docs/pipeline/skeleton-to-prompt.md` now disagree. They describe one
    intake agreement.
13. A `[CORE]` section was added or grew. Ask what was cut. The five core
    fields must take about ten minutes, or contributors will not fill them
    in.
14. An invented number, or a number without its conditions (hardware, model,
    batch size, and workload shape) in the same or the next sentence. Report
    an error.
15. A claim that does not trace to the skeleton, the diff, or a linked issue,
    and is missing from the claims ledger. Report an error.
16. Content from `Notes for the editor` in anything that is published.
17. A customer name, embargo date, credential, token, or internal-only URL
    anywhere in the diff. Report an error.
18. Upstream board mutation: a plan or script that relabels, assigns,
    transitions, or closes an issue in `LMCache/LMCache`. Report an error.
19. New Python without tests, or a bug fix without a regression test.
20. A PR that is too large because the diff covers unrelated concerns. Suggest
    a split.

### Step 4: Apply fixes

Use `Edit` for minimal changes. Keep the existing voice and formatting.
Re-read each edited file to confirm the change.

Never auto-fix category C. Report it.

### Step 5: Check the commits

```bash
git log --format='%H%n%an <%ae>%n%b%n---' main..HEAD
```

For every commit on the branch, verify these points:

- The required `Signed-off-by:` trailers are present. A commit by the repo
  owner needs both `quaid@iquaid.org` and `karsten@tensormesh.ai`. Other
  contributors sign off once, as themselves. If a trailer is missing, report an
  error. The fix is a rebase; the developer runs it, not you.
- The author line has no handle in parentheses:
  `Karsten Wade <quaid@iquaid.org>`, not `Karsten Wade (quaid) <...>`.
- No `Co-Authored-By:` trailer names a model, and there is no "generated
  with" banner, in the commits or the PR body. Otherwise report an error
  (`AGENTS.md` § Commit Authorship).
- The author is a human, not an agent identity.

### Step 6: Final verification

Print this command for the developer to run. Do not run it yourself.

```bash
pre-commit run --all-files     # or: uvx pre-commit run --all-files
```

## Output Format

### Summary
- Scope: `<uncommitted|staged|branch>`
- Files changed: `<N>`
- Issues found: `<total>` (auto-fixed: `<N>`, manual: `<N>`)

### Auto-fixed
Group by category, with `file:line` references.

### Manual review required
Group by severity: error (must fix before the PR), warning (should fix), and
info (suggestion). Give each item a `file:line` and a one-line explanation.

### Commands to run next

### Summary table

| Category | Auto-fixed | Manual | Total |
|---|---|---|---|

## Rules

- Change only files in the selected scope. Do not edit unchanged files.
- Do not add error handling, validation, or abstraction the task does not
  need.
- When a fix needs judgment, flag it. Do not guess.
- Never run `git add`, `git commit`, or `git push`. The developer owns git.
- Never run `pre-commit` yourself. Print the command.
- If `AGENTS.md` is missing, stop and ask the developer to pull the latest
  `main`.
