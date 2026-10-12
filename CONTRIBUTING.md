# Contributing

People come here for one of two tasks:

- To get a blog post written about a PR you landed, or about an idea, see
  [Submitting a blog post](#submitting-a-blog-post). You do not write the post.
- To change the pipeline (the template, the docs, or the tooling), see
  [Changing the pipeline](#changing-the-pipeline).

---

## Submitting a blog post

Read [`docs/blog-submission-process.md`](docs/blog-submission-process.md). It
describes five intake paths (A to E). Use the one that is easiest for you.

The usual path: open an issue, choose the **Blog post from a PR** template, and
fill in the five sections marked `[CORE]`. This takes about ten minutes. A
draft comes back within one day, and you review it before it is published.

Write in the language you think in. Do not translate. Translation on intake
loses details, and we localize the finished post anyway.

Fragments, typos, and informal explanations are fine.

---

## Changing the pipeline

This repo follows the LMCache project standards for agentic contributors,
because its output goes upstream into `LMCache/LMCache`.
[`AGENTS.md`](AGENTS.md) has the full standard and this repo's exceptions. It applies to humans and
agents, and reviewers check PRs against it.

### 1. Before you write

For any change larger than a typo, open an issue first and describe the change.
The template, the process doc, and the parse contract are three views of one
agreement. A change to one usually requires changes to the others, so agree on
it before you start.

Keep each PR small, with one logical change.

### 2. Branch and commit

The default branch is `main`. Base all branches and PRs on `main`.

```bash
git switch main
git pull
git switch -c docs/my-change
```

Name branches `<type>/<short-slug>`, where the type is `docs/`, `chore/`,
`feat/`, `fix/`, or `ci/`.

Every commit must carry a `Signed-off-by` trailer, which certifies that you
agree to the [Developer Certificate of Origin](DCO). Use `-s` and git adds it:

```bash
git commit -s -m "[Doc] Describe the change"
```

To add a missing sign-off, run `git commit --amend -s` for the last commit or
`git rebase --signoff main` for the whole branch.

Maintainer note: commits by Karsten Wade carry two sign-offs, one per identity.
`git commit -s` cannot add both. See
[`AGENTS.md` § Commit Authorship](AGENTS.md#commit-authorship) for the command.
All other contributors sign off once, as themselves.

**A human authors every commit, never an AI.** You are encouraged to use an
agent, but the commit carries your name and no model attribution. Do not add a
`Co-Authored-By:` trailer that names a model or a "generated with" banner, in
the commit message or the PR body. This repo publishes editorial content under
a human byline. LMCache upstream asks for an agent co-author trailer; this repo
differs on purpose.

### 3. Check your work locally

```bash
pre-commit run --all-files

# or, without installing anything
uvx pre-commit run --all-files
```

This runs whitespace and end-of-file checks, YAML/JSON/TOML validation,
`codespell`, and the skeleton-sync check. When the repo contains Python, it
also runs the SPDX-header check, `ruff`, `isort`, and `mypy`.

If you changed the skeleton, update the copy. The two files must stay
byte-identical:

```bash
cp .github/ISSUE_TEMPLATE/blog-post.md docs/templates/blog-post-skeleton.md
```

`AGENTS.md` explains why this is a copy and not a symlink.

### 4. Open the pull request

Push the branch and open a PR against `main`.

- Title: start with a type tag, as LMCache does. Use a bracketed type
  (`[Doc]`, `[Bugfix]`, `[Core]`, `[CI]`, `[Build]`, `[Test]`, `[Misc]`) or a
  conventional-commit type (`docs:`, `fix:`, `feat:`, `ci:`, `chore:`,
  `refactor:`, `test:`). Add the component if you can, for example
  `[Intake][Doc] ...` or `docs(intake): ...`.
- Description: fill in the [PR template](.github/PULL_REQUEST_TEMPLATE.md).
  Say what the PR does, why it is needed, and what a reviewer should look at
  first.
- Issue link: `Fixes #12` closes the issue on merge. `Refs #12` links it
  without closing it.
- Draft status: open the PR as a draft for early feedback, and mark it ready
  when it is done.

### 5. Review

Reviewers use the checklist at the end of [`AGENTS.md`](AGENTS.md). Read it
before you open the PR. To address feedback, push more signed-off commits to
the same branch. Merges are squashed, so you do not need to clean up your
history.

---

## Working with agents in this repo

The repo is configured for agent contributors:

- [`AGENTS.md`](AGENTS.md): the policy file for all agents (Claude Code,
  Copilot, Cursor, and Gemini). Humans own it. An agent reports missing
  guidance and does not edit the file.
- [`CLAUDE.md`](CLAUDE.md): the entry point for Claude Code. It points to
  `AGENTS.md`.
- `.claude/skills/`: committed skills for the PR flow. Run `/pre-pr-check`
  before you open a PR and `/create-pr` to open it.

The most important rules in `AGENTS.md` are the pipeline-specific ones. Never
invent a number. Never state a number without its conditions. Put every
unsourced claim in the claims ledger. Never publish `Notes for the editor`. A
post that breaks one of these rules must be retracted, which is worse than a
correction.

---

## Code of Conduct

The [Code of Conduct](CODE_OF_CONDUCT.md) applies to all participation.

## Who to ask

Ask Karsten Wade in `#lmcache-content`, or see
[`MAINTAINERS.md`](MAINTAINERS.md). If the pipeline produces something wrong,
report it in the issue. Do not fix it silently: these reports improve the
pipeline.
