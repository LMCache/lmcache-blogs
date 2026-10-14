# AGENTS.md

Guidelines for AI coding agents (Claude Code, Copilot, Cursor, Gemini, etc.) working in
this repository.

## AGENTS.md Ownership

`AGENTS.md` is a human-owned policy file.
Agents must not modify this file unless the user explicitly requests changes to `AGENTS.md`.
If an agent discovers recurring guidance or environment notes, it should report them in chat
instead of editing this file.

## Project Overview

`lmcache-blogs` holds the pipeline tools, content, and assets that take an LMCache blog post
from a contributor's rough skeleton to publication. It is the pipeline repo, not the LMCache
codebase: what lives here is the intake template, the parse and prompt contracts, the
process docs, and (as they get built) the automation that assembles drafts.

The pipeline exists because LMCache merges more good PRs than anyone has time to write up.
Contributors write a **skeleton** — rough notes, in their own language — and the pipeline
plus a human editor turn it into a post. See
[`docs/blog-submission-process.md`](docs/blog-submission-process.md) for the contributor
view and [`docs/pipeline/skeleton-to-prompt.md`](docs/pipeline/skeleton-to-prompt.md) for
the machine-facing half.

## Standards This Repo Follows

This repo adopts the **LMCache project standards for agentic contributors**, because its
output flows upstream into `LMCache/LMCache` (the blog-post issue template lands there, and
generated posts describe merged LMCache PRs). An agent that works to LMCache's standard here
produces artifacts that fit upstream without rework.

Where LMCache's standard is repo-specific, this repo's binding wins. The differences:

| Topic | `LMCache/LMCache` | **This repo** |
|---|---|---|
| Base branch | `dev` | **`main`** |
| Contribution model | fork-and-pull | branch-and-PR within the repo |
| Primary content | Python / C++ / CUDA / Rust | **Markdown**, plus Python for pipeline tooling |
| Test suite | `pytest` (large) | none yet — `pytest` when pipeline code lands |
| Commit trailers | one DCO sign-off **and** an agent `Co-Authored-By:` trailer | **two DCO sign-offs, no agent trailer** — see [Commit Authorship](#commit-authorship) |

Everything else — typing, docstrings, encapsulation, interface discipline, PR scope, the
review checklist — is LMCache's standard as written in their
[`AGENTS.md`](https://github.com/LMCache/LMCache/blob/dev/AGENTS.md) and
[`docs/coding_standards.md`](https://github.com/LMCache/LMCache/blob/dev/docs/coding_standards.md),
summarized below.

## Repository

The default branch is `main`. Base all new branches and pull requests against `main`.

### Layout

```
.github/ISSUE_TEMPLATE/blog-post.md   canonical blog-post skeleton / issue template
.github/ISSUE_TEMPLATE/blog-post-draft.md     written, needs technical review (path D)
.github/ISSUE_TEMPLATE/blog-post-complete.md  written and verified, needs copyedit (path E)
.github/PULL_REQUEST_TEMPLATE.md
docs/README.md                        map of the docs
docs/blog-submission-process.md       contributor-facing: the three intake paths
docs/pipeline/                        machine-facing pipeline contracts
docs/templates/blog-post-skeleton.md  attachable copy of the skeleton (intake path C)
tools/                                repo invariant checks, and the board router
tests/                                pytest suite for the pipeline tooling
.github/workflows/content-board.yml   routes issues onto the content board
.claude/skills/                        committed agent skills for the PR flow
```

### The skeleton exists twice, on purpose

`.github/ISSUE_TEMPLATE/blog-post.md` is **canonical**. GitHub's template chooser only reads
files in that directory, and intake path C needs a file a contributor can download and
attach, which a symlink does not survive over `raw.githubusercontent.com`.

So `docs/templates/blog-post-skeleton.md` is a **byte-identical copy**, and
`tools/check_skeleton_sync.sh` fails pre-commit if the two ever drift. Edit the canonical
file, then copy it:

```bash
cp .github/ISSUE_TEMPLATE/blog-post.md docs/templates/blog-post-skeleton.md
```

Never "improve" one copy alone.

## Commit Authorship

**Standing constraint: commits in this repo are authored as the human contributor, never as
an AI.** No `Co-Authored-By:` trailer naming a model, no "generated with" banner, no AI
identity in the author or committer field. This is a deliberate divergence from LMCache
upstream, which does ask for an agent co-author trailer; it holds for this repo because its
output is published editorial content under a human byline.

Every commit must carry a DCO `Signed-off-by` trailer certifying the
[Developer Certificate of Origin](DCO). In this repo it carries **two** — one per
contributing identity, because the work sits in both contexts at once: the repo lives in a
personal namespace, and the content is produced for LMCache on behalf of Tensormesh.

```bash
git -c user.name="Karsten Wade" -c user.email="quaid@iquaid.org" commit \
  --trailer "Signed-off-by: Karsten Wade <quaid@iquaid.org>" \
  --trailer "Signed-off-by: Karsten Wade <karsten@tensormesh.ai>" \
  -m "[Doc] Describe the change"
```

Note what this does *not* use: plain `git commit -s` adds one trailer, taken from
`user.email`, so it cannot produce both. Set the trailers explicitly.

Set the author identity explicitly too — a local `git user.name` is often unset or carries a
handle in parentheses, and the author line should read `Karsten Wade <quaid@iquaid.org>` to
match the rest of this repo's history.

A contributor who is not Karsten signs off once, as themselves.

## Branches and PR Titles

Branch names: `<type>/<short-slug>` — `docs/`, `chore/`, `feat/`, `fix/`, `ci/`.

PR titles start with a tag saying what kind of change it is, matching LMCache practice.
Either form is fine, and both are in wide use upstream:

- a bracketed type — `[Doc]`, `[Bugfix]`, `[Core]`, `[CI]`, `[Build]`, `[Test]`, `[Misc]`
- a conventional-commit type — `docs:`, `fix:`, `feat:`, `ci:`, `chore:`, `refactor:`, `test:`

Name the component too when it helps a reviewer — `[Intake][Doc] ...` or `docs(intake): ...`.

Keep each PR small and focused on one logical change. Break large work into a series of PRs
that each stand on their own.

## Linting & Code Quality

```bash
# Run all checks (mirrors CI)
pre-commit run --all-files

# If pre-commit is not installed
uvx pre-commit run --all-files

# Tests for the pipeline tooling
pip install -r requirements/test.txt
pytest tests/ -q
```

The hook set is deliberately small while this repo is mostly prose: whitespace and
end-of-file hygiene, YAML/JSON/TOML validity, `codespell`, the skeleton-sync check, and an
SPDX-header check plus `ruff`/`isort`/`mypy` that activate as soon as `.py` files appear.

### Writing Prose

The docs here are read by contributors who are deciding whether to bother, and by engineers
who write English as a second, third, or fourth language. Follow LMCache's documentation
principles — be concrete and concise, include examples, explain the *why* and not just the
*what*, keep each document's audience focused — plus these repo-specific ones:

- **Wrap at 80 columns.** Every markdown file in `docs/` and every template. Diffs on
  hand-wrapped prose stay reviewable; diffs on reflowed paragraphs do not.
- **Short words, short sentences.** No "leverage", "utilize", "seamlessly", "revolutionary",
  or "in today's fast-paced world". This applies to the docs *and* to anything the pipeline
  generates.
- **Write "KV cache" and "KV caching".** Lowercase "cache", no hyphen, in prose, headings,
  captions, alt text, and anything the pipeline generates. Hyphenate only when grammar needs
  it for clarity, as in a stacked modifier ("KV-cache-aware routing"). Title-case headlines
  capitalize it like any other word. Code, flags, and identifiers keep their own spelling.
- **Second person, present tense**, in both docs and generated posts.
- **Do not translate a contributor's words into house style.** House style governs
  structure, register, and clarity. It does not govern an author's own description of their
  own work.

### Python (pipeline tooling, as it lands)

LMCache's conventions apply unchanged. The ones that bite first:

- `# SPDX-License-Identifier: Apache-2.0` as **line 1** of every Python file.
- Type hints on every function argument and return value. No `Any`, no bare generics
  (`list[str]`, not `list`). Prefer `X | None` over `Optional[X]`, and prefer initializing
  an empty object over making it nullable at all.
- A complete docstring on every public function — summary, args, returns, raises. The
  docstring must describe what the code actually does now.
- No `assert` for runtime validation. Use `if not cond: raise ValueError(...)`.
- No boolean parameters on public APIs — use an enum, or split the function.
- No ambiguous return values (one `None` meaning two different things).
- Never access another class's `_`-prefixed members.
- Imports carry section headings, `isort` with `profile=black` and `from_first=true`:

  ```python
  # Standard
  import os

  # Third Party
  import yaml

  # First Party
  from lmcache_blogs.parser import parse_skeleton

  # Local
  from .utils import helper
  ```
- Module-level helpers at the top of the file, after imports and before classes. Private
  methods at the end of a class, after the public ones.
- New features and bug fixes need tests. Tests target the **public interface and docstring
  contract**, not internals.

## Pipeline-Specific Rules for Agents

These are load-bearing. Violating one produces a post that has to be thrown away, or worse,
one that gets published wrong.

- **The `##` headings in all three blog issue templates are the schema.** The parser splits
  on them by name, and strips the ` [CORE]` suffix before matching. Renaming, reordering, or
  deleting a heading is a breaking change: update the matching parse contract table in
  `docs/pipeline/skeleton-to-prompt.md` in the same PR, or don't do it. There are three
  tables — one per template.
- **Never invent a number.** Not one. If a skeleton's `Numbers` section is empty, the post
  has no benchmarks in it.
- **Never state a number without its conditions** — hardware, model, batch size, workload
  shape — in the same sentence or the one next to it.
- **Never claim a capability the diff does not show.**
- **Every assertion that did not come from the skeleton, the diff, or a linked issue goes in
  the claims ledger** at the end of the draft, with a pointer to where it appears. The
  ledger is what makes technical review a bounded task.
- **An already-written post takes one of two paths, and the only difference is whether the
  technical content still needs checking.** Path D (`blog-post-draft.md`) goes through
  Technical review; path E (`blog-post-complete.md`) skips it. The author decides. Most
  already-written submissions are path E — a post by the person who built the thing, or one
  another org already reviewed — so treat D as the exception, not the default.
- **On path D, `sources` and `uncertain` are optional hints, not gates.** They make the
  technical review faster; they do not authorize it, because the review happens either way.
  Empty is not an error: route the card and note *"no sourcing supplied"* for the reviewer.
  Never hold the card or emit `QUESTION FOR AUTHOR` over them, and accept any shape the
  author used — inline links, a bullet list, "it is all in PR #1234", an attached log. We do
  not know what they drafted in and it does not matter.
- **On path E, `verified_by` is an attestation, not a verification.** It records who vouched,
  so a later mistake has a name attached. Take it at face value: do not re-derive it from
  the diff, and do not quietly route the card through Technical review because it looks
  thin — that is the wasted round trip path E exists to avoid. Never ask a path E post for a
  claims ledger; that is asking for the review it just skipped. Honor `copyedit: light` when
  set — it is the author declining a rewrite, not an opening position.
- **`Notes for the editor` is never rendered.** It constrains the generator and stops there.
- **An empty required field is a `QUESTION FOR AUTHOR` block, not a guess.** A draft with
  open questions does not advance to editorial.
- **Respect the brand boundary.** LMCache content is LMCache-canonical. Tensormesh does not
  originate LMCache content. If a piece's placement is unclear, ask rather than assume.
- **Routing decisions must stay total.** `route()` in `tools/board_router.py` returns a
  decision for every possible set of labels, with a reason, and an issue it cannot place is
  labelled `needs-triage` and commented on rather than dropped. If you add a branch, add the
  test alongside it: `tests/test_board_router.py` asserts totality exhaustively, and that
  property is the point of the router. Never introduce a silent fall-through, and never let
  the router guess a review lane — guessing skips a review on something about to be
  published.
- **Do not mutate the upstream LMCache board.** Issues and PRs in `LMCache/LMCache` are
  read-only reference. Comment substantively when you have something useful to add; never
  relabel, assign, transition, or close an issue this project does not own.

## Review Checklist

Self-check before opening a PR, and check when reviewing one:

### Correctness
- [ ] The change does what the PR description says it does.
- [ ] Process docs, the issue template, and the parse contract still agree with each other.
- [ ] Links resolve, including anchors and raw-file URLs.

### Standards
- [ ] `pre-commit run --all-files` passes.
- [ ] Markdown wraps at 80 columns.
- [ ] Every commit has **both** DCO `Signed-off-by` trailers and **no** AI co-author
      trailer, in the commit message *and* in the PR body.
- [ ] PR title carries a type tag; scope is one logical change.

### Skeleton and contracts
- [ ] `.github/ISSUE_TEMPLATE/blog-post.md` and `docs/templates/blog-post-skeleton.md` are
      byte-identical.
- [ ] Any heading change is reflected in the matching parse contract table (there are three,
      one per template).
- [ ] A new or changed `entry_lane` value maps to a real column on the board.
- [ ] The five `[CORE]` fields still take a contributor about ten minutes. If the skeleton
      grew, something else got cut.

### Python (when present)
- [ ] SPDX header on line 1; type hints and docstrings complete.
- [ ] No `assert` for validation, no boolean params, no private-member access.
- [ ] Tests cover the public contract, and they pass.

### Content safety
- [ ] No invented numbers; every number carries its conditions.
- [ ] Claims ledger present and complete for generated drafts.
- [ ] Nothing from `Notes for the editor` leaked into published output.
- [ ] No customer names, embargoed dates, or credentials anywhere in the diff.
