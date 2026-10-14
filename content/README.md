# Content

Where the actual material lives, as opposed to the process that produces it. The process
docs are in [`../docs/`](../docs/).

| Directory | What goes in it |
|---|---|
| `skeletons/` | Filled-in skeletons committed through intake path C, named `<pr-number>.md`. |
| `drafts/` | Written posts submitted for review as a PR (paths D and E), one folder per post. |

## skeletons/

Intake path C lets a contributor commit a filled skeleton alongside their code rather than
pasting it into an issue. Those land here as `content/skeletons/<pr-number>.md` — the PR
number from `LMCache/LMCache`, so `content/skeletons/1234.md`.

Use the template at
[`../docs/templates/blog-post-skeleton.md`](../docs/templates/blog-post-skeleton.md) and
keep the `##` headings exactly as they are: the parser reads them by name.

A skeleton committed here still needs an issue on the content board linking to it. The file
is the working surface; the issue is the tracking record.

## drafts/

A post that is already written can come in as a PR, so editors can review it line by line
and suggest changes the author accepts with one click. Each post gets its own folder:

```
content/drafts/<slug>/post.md
content/drafts/<slug>/images/<name>.png
```

- `<slug>` is short, lowercase, and hyphenated: `mp-coordinator`, not `MP_Coordinator_v2`.
- Send Markdown, not exported HTML. HTML with embedded images cannot be reviewed as a diff.
- Put one sentence per line, with a blank line between paragraphs. A review comment then
  points at one sentence, not a whole paragraph.
- Keep images as separate files and link them with relative paths, with alt text:
  `![Each vLLM process uses its own KV cache](images/fig-1-per-process-kv.png)`.

To submit:

1. Fork this repo and branch from `main`: `git switch -c content/<slug>`
2. Add `content/drafts/<slug>/post.md` and its `images/`.
3. Commit with a sign-off and no AI co-author line: `git commit -s -m "[Doc] Draft: <title>"`
4. Open the PR against `main`. Open the board issue with the matching template (path D or E)
   and link the PR from it; put `Refs #<issue>` in the PR body.
5. Post the PR link in `#lmcache-content`.

Editors review with suggested changes. Accept them with **Commit suggestion**, or reply on the
line. The PR stays open until the post publishes; the issue remains the tracking record.

## Not here yet

Published posts and their final image assets do not have a home in this repo yet. Where they
land depends on the WordPress publishing service, which is a later phase. Do not invent a
directory for them without an issue agreeing on the layout first.
