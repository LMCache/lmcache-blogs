# Docs

Each document has one audience. Start with the row that describes you.

| Document | Who it is for |
|---|---|
| [`blog-submission-process.md`](blog-submission-process.md) | A contributor who landed a PR. The intake paths, and what happens to your card after you submit. Start here. |
| [`templates/blog-post-skeleton.md`](templates/blog-post-skeleton.md) | A contributor using intake path C. The skeleton as a file to download and fill in. Byte-identical to the issue template. |
| [`pipeline/skeleton-to-prompt.md`](pipeline/skeleton-to-prompt.md) | Whoever builds or debugs the pipeline. Parse contract, PR hydration, prompt assembly, output contract, claims ledger, and the two smaller contracts for written posts. |
| [`pipeline/board-routing.md`](pipeline/board-routing.md) | Whoever needs to know why a card is in its column. The label-to-column table, what happens to issues that match no rule, and the one secret the automation needs. |
| [`TRANSFER.md`](TRANSFER.md) | Record of the move to the LMCache org (done). What GitHub carried over, what it did not (the board), the steps, and two open decisions. |

## Summary

Contributors do not write posts. They write a **skeleton**: rough notes, in
their own language, about what was broken and how they fixed it. The pipeline
adds the PR's metadata and diff, builds a prompt, and generates a draft. An
editor and the original author review the draft before it is published.

A post that is already written uses one of the other two templates and skips
drafting. See paths D and E in the process doc, and templates two and three in
the parse contract.

## These three documents are one agreement

The issue template, the process doc, and the parse contract describe the same
agreement. They drift apart without warning.

- The skeleton's `##` headings are the parser's schema. Renaming, reordering,
  or deleting a heading is a breaking change.
- The process doc promises contributors a set of fields and a ten-minute budget
  for the five `[CORE]` fields.
- The parse contract says which fields are required and what each one does in
  the finished post.

When you change one, check the other two. Reviewers return a PR that changes a
heading without changing the parse contract table. See the checklist in
[`../AGENTS.md`](../AGENTS.md).

## The three issue templates

| Template | For | Enters at | Technical review? |
|---|---|---|---|
| `blog-post.md` | notes about a PR; someone else writes the post | Drafting | yes |
| `blog-post-draft.md` | a written post whose technical content still needs checking | Editorial review or Technical review | yes |
| `blog-post-complete.md` | a written post that is already technically sound | Editorial review | no, goes to Translations |

The last two templates both take a written post. The only difference is whether
the technical content still needs checking. Most written submissions use the
third template: the author built the feature, or another org already reviewed
the post. The second template is the exception.

Only the first template has a downloadable copy under `templates/`. It is the
only one a contributor fills in offline; a written post is already a file.

## Where the skeleton lives

`.github/ISSUE_TEMPLATE/blog-post.md` is canonical, because GitHub's template
chooser reads only that directory. `docs/templates/blog-post-skeleton.md` is a
byte-identical copy. Intake path C needs a file that a contributor can download
and attach, and a symlink does not work through `raw.githubusercontent.com`.
`tools/check_skeleton_sync.sh` fails pre-commit if the two files differ. Edit
the canonical file, then run:

```bash
cp .github/ISSUE_TEMPLATE/blog-post.md docs/templates/blog-post-skeleton.md
```

## Not here yet

The pipeline plan names these, and they are not written yet:

- The whitePrint style definition that the image stage depends on.
- The Google Doc copy of the skeleton for intake path B, and its link in the
  process doc.
- The parser that implements the parse contract for the three skeleton paths (A, B, and C).
- The prompt assembler: hydration, claims ledger, and `QUESTION FOR AUTHOR`
  output.
- Stall detection. The process doc promises a reminder when a card waits on
  someone for more than two days. This needs Slack. See "What this does not
  do" in [`pipeline/board-routing.md`](pipeline/board-routing.md).
