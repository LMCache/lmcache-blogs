# Content

This directory holds the material the pipeline works on. The process docs are
in [`../docs/`](../docs/).

| Directory | What goes in it |
|---|---|
| `skeletons/` | Filled-in skeletons committed through intake path C, named `<pr-number>.md`. |
| `drafts/` | Written posts submitted for review as a PR (paths D and E), one folder per post. |

## skeletons/

Intake path C lets a contributor commit a filled skeleton with their code
instead of pasting it into an issue. Name the file after the `LMCache/LMCache`
PR number, for example `content/skeletons/1234.md`.

Start from
[`../docs/templates/blog-post-skeleton.md`](../docs/templates/blog-post-skeleton.md).
Do not change the `##` headings: the parser reads them by name.

Each skeleton committed here also needs an issue on the content board that
links to it. The file holds the content; the issue tracks it.

## drafts/

A written post can come in as a PR. Editors then review it line by line and
suggest changes that the author accepts with one click. Each post gets its own
folder:

```
content/drafts/<slug>/post.md
content/drafts/<slug>/images/<name>.png
```

- Make `<slug>` short, lowercase, and hyphenated: `mp-coordinator`, not
  `MP_Coordinator_v2`.
- Send Markdown, not exported HTML. HTML with embedded images cannot be
  reviewed as a diff.
- Put one sentence per line, with a blank line between paragraphs, so that a
  review comment points at one sentence.
- Keep images as separate files. Link them with relative paths and alt text:
  `![Each vLLM process uses its own KV cache](images/fig-1-per-process-kv.png)`.

To submit:

1. Fork this repo and branch from `main`: `git switch -c content/<slug>`
2. Add `content/drafts/<slug>/post.md` and its `images/`.
3. Commit with a sign-off and no AI co-author line:
   `git commit -s -m "[Doc] Draft: <title>"`
4. Open the board issue with the matching template (path D or E). Then open
   the PR against `main`, with this line in its description, using the issue's
   number:

   ```
   Post: #<issue>
   ```

   The board follows the PR through that line. Do not use `Fixes #<issue>`:
   it would close the post's issue when the PR merges.
5. Post the PR link in `#lmcache-content`.

Editors review with suggested changes. Accept them with **Commit suggestion**,
or reply on the line. Each review stage ends with a maintainer's approval, and
each approval moves the post's card to its next stage. The PR stays open until
the post is published; merging it moves the card to Published. The issue
remains the tracking record. How the card moves is in
[`../docs/pipeline/board-automation.md`](../docs/pipeline/board-automation.md).

## Not here yet

Published posts and their final image assets have no directory in this repo yet.
Their location depends on the WordPress publishing service, which is a later
phase. Do not create a directory for them until an issue agrees on the layout.
