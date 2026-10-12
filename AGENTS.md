# AGENTS.md

Rules for AI coding agents (Claude Code, Copilot, Cursor, Gemini, and others)
in this repository.

## AGENTS.md Ownership

`AGENTS.md` is a human-owned policy file. Do not edit it unless the user
explicitly asks for changes to `AGENTS.md`. Report recurring guidance or
environment notes in chat instead.

## Project Overview

`lmcache-blogs` is the pipeline for LMCache blog posts: intake templates, parse
and prompt contracts, process docs, and automation. Contributors write a
skeleton (rough notes, in their own words). The pipeline and a human editor turn
it into a post. The LMCache code is not here. For the contributor view, see
[`docs/blog-submission-process.md`](docs/blog-submission-process.md). For the
machine view, see
[`docs/pipeline/skeleton-to-prompt.md`](docs/pipeline/skeleton-to-prompt.md).

## Standards This Repo Follows

This repo follows the LMCache standards for agentic contributors, because its
output goes to `LMCache/LMCache`. Where they differ, this repo's rule wins:

| Topic | `LMCache/LMCache` | **This repo** |
|---|---|---|
| Base branch | `dev` | **`main`** |
| Contribution model | fork-and-pull | branch-and-PR within the repo |
| Primary content | Python / C++ / CUDA / Rust | **Markdown**, plus Python for pipeline tooling |
| Test suite | `pytest` (large) | `pytest` for the pipeline tooling |
| Commit trailers | one DCO sign-off and an agent `Co-Authored-By:` trailer | **two DCO sign-offs, no agent trailer**; see [Commit Authorship](#commit-authorship) |

For everything else, follow the LMCache
[`AGENTS.md`](https://github.com/LMCache/LMCache/blob/dev/AGENTS.md) and
[`docs/coding_standards.md`](https://github.com/LMCache/LMCache/blob/dev/docs/coding_standards.md).
The sections below summarize them.

## Repository

The default branch is `main`. Base all branches and pull requests on `main`.

### Layout

```
.github/ISSUE_TEMPLATE/blog-post.md   canonical blog-post skeleton / issue template
.github/ISSUE_TEMPLATE/blog-post-draft.md     written, needs technical review (path D)
.github/ISSUE_TEMPLATE/blog-post-complete.md  written and verified, needs copyedit (path E)
.github/PULL_REQUEST_TEMPLATE.md
docs/README.md                        map of the docs
docs/blog-submission-process.md       contributor-facing: the five intake paths
docs/pipeline/                        machine-facing pipeline contracts
docs/templates/blog-post-skeleton.md  attachable copy of the skeleton (intake path C)
tools/                                repo invariant checks, and the board router
tests/                                pytest suite for the pipeline tooling
.github/workflows/content-board.yml   routes issues onto the content board
.claude/skills/                        committed agent skills for the PR flow
```

### The skeleton exists twice, on purpose

`.github/ISSUE_TEMPLATE/blog-post.md` is **canonical**, because GitHub's
template chooser reads only that directory. Intake path C needs a downloadable
file, and a symlink does not work over `raw.githubusercontent.com`, so
`docs/templates/blog-post-skeleton.md` is a byte-identical copy.
`tools/check_skeleton_sync.sh` fails pre-commit if they differ. Edit the
canonical file, then copy it:

```bash
cp .github/ISSUE_TEMPLATE/blog-post.md docs/templates/blog-post-skeleton.md
```

Never edit only one copy.

## Commit Authorship

Author every commit as the human contributor. Do not add a `Co-Authored-By:`
trailer that names a model, a "generated with" banner, or an AI identity in the
author or committer field. LMCache upstream asks for an agent co-author
trailer; this repo does not, because its output is editorial content published
under a human byline.

Every commit needs a DCO `Signed-off-by` trailer for the
[Developer Certificate of Origin](DCO). Commits by Karsten Wade carry **two**,
one for each identity. He does this work for LMCache on behalf of Tensormesh,
and he has a personal and a Tensormesh identity. This rule is under review
after the move to `LMCache/lmcache-blogs`; see
[`docs/TRANSFER.md`](docs/TRANSFER.md).

```bash
git -c user.name="Karsten Wade" -c user.email="quaid@iquaid.org" commit \
  --trailer "Signed-off-by: Karsten Wade <quaid@iquaid.org>" \
  --trailer "Signed-off-by: Karsten Wade <karsten@tensormesh.ai>" \
  -m "[Doc] Describe the change"
```

Do not use `git commit -s`. It adds only one trailer, taken from `user.email`.

Set the author identity explicitly, as the command does. The author line must
read `Karsten Wade <quaid@iquaid.org>`, with no handle in parentheses.

Other contributors sign off once, as themselves.

## Branches and PR Titles

Name branches `<type>/<short-slug>`, with type `docs/`, `chore/`, `feat/`,
`fix/`, or `ci/`.

Start each PR title with a type tag, as LMCache does. Use either form:

- a bracketed type: `[Doc]`, `[Bugfix]`, `[Core]`, `[CI]`, `[Build]`,
  `[Test]`, `[Misc]`
- a conventional-commit type: `docs:`, `fix:`, `feat:`, `ci:`, `chore:`,
  `refactor:`, `test:`

Add the component when it helps a reviewer: `[Intake][Doc] ...` or
`docs(intake): ...`.

Keep each PR to one logical change. Split large work into PRs that each work
alone.

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

The hooks cover whitespace and end-of-file hygiene, YAML/JSON/TOML validity,
`codespell`, the skeleton-sync check, an SPDX-header check, and `ruff`,
`isort`, and `mypy` for `.py` files.

### Writing Prose

Many readers write English as a second, third, or fourth language. Be concrete
and concise, give examples, explain why, and write each document for one
audience. Also follow these rules:

- Wrap Markdown at 80 columns in `docs/` and in every template.
- Use short words and short sentences. Do not use "leverage", "utilize",
  "seamlessly", "revolutionary", or "in today's fast-paced world".
- Write "KV cache" and "KV caching": lowercase "cache", no hyphen. This
  applies to prose, headings, captions, and alt text. Hyphenate only when
  grammar needs it in a stacked modifier ("KV-cache-aware routing").
  Title-case headlines capitalize it like any other word. Code, flags, and
  identifiers keep their own spelling.
- Use second person and present tense.
- Do not rewrite a contributor's words into house style. House style controls
  structure, register, and clarity, but not how authors describe their work.

These rules apply to the docs and to everything the pipeline generates.

### Python (pipeline tooling)

The LMCache conventions apply. The most common:

- Put `# SPDX-License-Identifier: Apache-2.0` on line 1 of every Python
  file.
- Add type hints to every argument and return value. Do not use `Any` or bare
  generics (use `list[str]`, not `list`). Use `X | None`, not `Optional[X]`.
  Prefer an empty object to a nullable one.
- Give every public function a complete docstring: summary, args, returns, and
  raises. The docstring must match what the code does now.
- Do not use `assert` for runtime validation. Use
  `if not cond: raise ValueError(...)`.
- Do not use boolean parameters on public APIs. Use an enum, or split the
  function.
- Do not return ambiguous values, such as one `None` with two meanings.
- Never access another class's `_`-prefixed members.
- Group imports under section headings. Use `isort` with `profile=black` and
  `from_first=true`:

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
- Put module-level helpers after the imports and before the classes. Put
  private methods at the end of a class, after the public ones.
- Add tests for new features and bug fixes. Test the public interface and the
  docstring contract, not internals.

## Pipeline-Specific Rules for Agents

Breaking one of these rules produces a post that must be discarded, or one that
is published with errors.

- The `##` headings in all three blog issue templates are the schema. The parser
  splits on them by name and strips the ` [CORE]` suffix before it matches. To
  rename, reorder, or delete a heading, update the matching parse-contract
  table in `docs/pipeline/skeleton-to-prompt.md` in the same PR. There are three
  tables, one per template.
- **Never invent a number.** If the skeleton's `Numbers` section is empty, the
  post has no benchmarks.
- State every number with its conditions (hardware, model, batch size, and
  workload shape) in the same sentence or the next one.
- Never claim a capability that the diff does not show.
- Record every assertion that does not come from the skeleton, the diff, or a
  linked issue in the claims ledger at the end of the draft, with a pointer to
  where it appears. The ledger keeps technical review to a fixed scope.
- An already-written post takes path D or path E. The author chooses. Path D
  (`blog-post-draft.md`) goes through Technical review. Path E
  (`blog-post-complete.md`) skips it. Most are path E (written by the person
  who built the feature, or already reviewed by another org). Treat path D as
  the exception.
- On path D, `sources` and `uncertain` are optional hints for the reviewer. If
  they are empty, route the card and add the note *"no sourcing supplied"* for
  the reviewer. Never hold the card or emit `QUESTION FOR AUTHOR` because of
  them. Accept them in any form (links, a list, "it is all in PR #1234", or a
  log).
- On path E, `verified_by` records who vouched for the post. Accept it as
  given. Do not re-check it against the diff, and do not route the card through
  Technical review because the attestation looks thin. Never ask a path E post
  for a claims ledger. Honor `copyedit: light` when it is set: the author has
  declined a rewrite.
- Never render `Notes for the editor`. It constrains the generator only.
- When a required field is empty, write a `QUESTION FOR AUTHOR` block. Do not
  guess. A draft with open questions does not move to editorial.
- Keep routing total. `route()` in `tools/board_router.py` returns a decision
  and a reason for every possible set of labels. It labels an issue that it
  cannot place `needs-triage` and comments on it. When you add a branch, add
  its test: `tests/test_board_router.py` checks totality exhaustively. Never add
  a silent fall-through. Never let the router guess a review lane, because a
  wrong guess skips review on a post that is about to be published.
- Do not change the upstream LMCache board. Treat issues and PRs in
  `LMCache/LMCache` as read-only reference. You may comment. Never relabel,
  assign, transition, or close an issue that this project does not own.

## Review Checklist

Use this list to check your own PR before you open it, and to review others.

### Correctness
- [ ] The change does what the PR description says.
- [ ] The process docs, the issue template, and the parse contract agree.
- [ ] Links resolve, including anchors and raw-file URLs.

### Standards
- [ ] `pre-commit run --all-files` passes.
- [ ] Markdown wraps at 80 columns.
- [ ] Every commit has both DCO `Signed-off-by` trailers and no AI co-author
      trailer. The PR body has no AI attribution.
- [ ] The PR title has a type tag, and the PR is one logical change.

### Skeleton and contracts
- [ ] `.github/ISSUE_TEMPLATE/blog-post.md` and
      `docs/templates/blog-post-skeleton.md` are byte-identical.
- [ ] Every heading change is in the matching parse-contract table (one per
      template).
- [ ] Every new or changed `entry_lane` value maps to a real column on the
      board.
- [ ] A contributor can still complete the five `[CORE]` fields in about ten
      minutes. If the skeleton grew, something else was cut.

### Python (when present)
- [ ] SPDX header on line 1; type hints and docstrings complete.
- [ ] No `assert` for validation, no boolean params, no private-member access.
- [ ] Tests cover the public contract and pass.

### Content safety
- [ ] No invented numbers; every number states its conditions.
- [ ] Generated drafts have a complete claims ledger.
- [ ] No content from `Notes for the editor` in published output.
- [ ] No customer names, embargoed dates, or credentials in the diff.
