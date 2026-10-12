# CLAUDE.md

Guidance for Claude Code (claude.ai/code) in this repository.

## Read First

[AGENTS.md](AGENTS.md) is the authoritative agent policy for this repo. It
covers standards, layout, commit authorship, PR conventions, prose and Python
style, pipeline-specific rules, and the review checklist. Read it before you
write anything.

[CONTRIBUTING.md](CONTRIBUTING.md) covers the human flow: how to submit a blog
post and how to change the pipeline.

This repo adopts the LMCache project standards for agentic contributors, with
two repo-specific exceptions: the base branch is `main` (not `dev`), and commits
carry no AI co-author trailers. AGENTS.md has the full table.

## The Two Things Most Likely to Trip You Up

1. Commits carry two DCO sign-offs and no AI attribution. Both of Karsten's
   identities sign off: `quaid@iquaid.org` and `karsten@tensormesh.ai`.
   `git commit -s` adds only one, so set both trailers explicitly. The command
   is in AGENTS.md § Commit Authorship. Do not add a `Co-Authored-By:` trailer
   that names a model or a "generated with" banner, in commits or PR bodies.
2. The skeleton exists in two places, and the files must stay byte-identical.
   `.github/ISSUE_TEMPLATE/blog-post.md` is canonical.
   `docs/templates/blog-post-skeleton.md` is the copy for intake path C.
   `tools/check_skeleton_sync.sh` enforces this in pre-commit.

## Docs Map

| Document | What it is |
|---|---|
| [`docs/blog-submission-process.md`](docs/blog-submission-process.md) | Contributor-facing. The intake paths and what happens to a card. |
| [`docs/pipeline/skeleton-to-prompt.md`](docs/pipeline/skeleton-to-prompt.md) | Machine-facing. Parse contract, hydration, prompt assembly, output contract, claims ledger. |
| [`docs/pipeline/board-routing.md`](docs/pipeline/board-routing.md) | Label-to-column routing, the totality guarantee, and the `PROJECT_TOKEN` secret the workflow needs. |
| [`.github/ISSUE_TEMPLATE/blog-post.md`](.github/ISSUE_TEMPLATE/blog-post.md) | The skeleton. Its `##` headings are the parser's schema. |
| [`.github/ISSUE_TEMPLATE/blog-post-draft.md`](.github/ISSUE_TEMPLATE/blog-post-draft.md) | A written post whose technical content still needs checking. Goes through Technical review. |
| [`.github/ISSUE_TEMPLATE/blog-post-complete.md`](.github/ISSUE_TEMPLATE/blog-post-complete.md) | A written post that is already technically sound. Copyedit, then Translations; skips Technical review. The usual case for a written post. |

When you change one of these, check whether the others need the same change.
The process doc, the template, and the parse contract describe one agreement,
and they drift without warning.

## Skills

Use the committed skills for the PR flow:

- `/pre-pr-check`: before you open a PR, check the branch against this repo's
  standards and fix what can be fixed mechanically.
- `/create-pr`: open the PR from a pushed branch with the repo's PR template.

## Working Agreements

- Wrap prose at 80 columns. See AGENTS.md § Writing Prose for the rest of the
  house style.
- Keep PRs small, with one logical change each.
- Treat upstream `LMCache/LMCache` issues and PRs as read-only. Never relabel,
  assign, transition, or close an issue that this project does not own.
- Never invent a number. Never state a number without its conditions. This
  applies to docs and to all pipeline output.
