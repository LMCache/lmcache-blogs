---
name: create-pr
description: Create a GitHub pull request from the current branch, using the repo's PR template
allowed-tools: Bash, Read, Glob, Grep, Agent, mcp__github__create_pull_request
argument-hint: "[base_branch] [--draft] [--title 'PR title']"
---

# Create Pull Request

Open a pull request from the current branch. This skill only opens the PR. It
never commits and never pushes.

Run `/pre-pr-check` first.

## Arguments

`$ARGUMENTS` may contain:
- First positional arg: the base branch (default: the repo's default branch,
  `main`)
- `--draft`: open the PR as a draft
- `--title 'PR title'`: use this title instead of a generated one

## Steps

### 1. Gather context

Run these in parallel:

```bash
git remote -v
git branch -vv --contains HEAD
git status -s
gh api repos/<OWNER>/<REPO> --jq '.default_branch'
```

Find the remote, the owner/repo, and the base branch (from `$ARGUMENTS`, else
the default branch).

### 2. Check that the branch is pushed

Verify that the branch exists on the remote. If it does not, **stop and tell
the developer to push it.** Do not push it yourself.

If the working tree has uncommitted changes, warn that they will not be in the
PR.

### 3. Verify the commits

```bash
git log --format='%H%n%an <%ae>%n%b%n---' <base>..HEAD
```

Do not open the PR. Stop and report if any commit:

- is missing a required `Signed-off-by:` trailer. A commit by the repo owner
  needs both `quaid@iquaid.org` and `karsten@tensormesh.ai`. Other contributors
  sign off once, as themselves.
- has a `Co-Authored-By:` trailer that names a model, or a "generated with"
  banner. Only humans author commits in this repo (`AGENTS.md` § Commit
  Authorship).

The same rule applies to the PR body: do not add model attribution or a
"generated with" footer.

### 4. Read the PR template

```
Glob: .github/PULL_REQUEST_TEMPLATE.md
Glob: .github/pull_request_template.md
```

### 5. Analyze the changes

```bash
git log --oneline <base>..HEAD
git diff <base>..HEAD --stat
git diff <base>..HEAD          # if the change is small enough to read whole
```

### 6. Draft the PR

- Title: use `--title` if given. Otherwise write one under 70 characters. Start
  it with a type tag: a bracketed type (`[Doc]`, `[Bugfix]`, `[Core]`, `[CI]`,
  `[Build]`, `[Test]`, `[Misc]`) or a conventional-commit type (`docs:`,
  `fix:`, `feat:`, `ci:`, `chore:`). Add the component when it helps:
  `[Intake][Doc] ...` or `docs(intake): ...`.
- Body: fill in the template's sections. Start with why the change is needed
  and what the reviewer should look at first. Tick the checkboxes that apply,
  including skeleton-sync and parse-contract when the change touches the
  skeleton. Do not list changes file by file; the reviewer can read the diff.
- Issue link: `Fixes #N` closes the issue on merge. `Refs #N` links it for
  context only.

Show the title and body, and **ask for confirmation before you create the
PR.**

### 7. Create it

Call `mcp__github__create_pull_request` with the owner, repo, `head` (the
branch), `base`, title, body, and `draft` if requested.

### 8. Report

Print the PR URL. Remind the developer that a new PR does not notify a
specific person. Post the link in `#lmcache-content` with a one-line summary so
that a human knows it is waiting.

## Important Notes

- Never push or commit.
- Always show the title and body for confirmation first.
- Keep one logical change per PR. If the diff covers unrelated concerns, say
  so and suggest a split.
