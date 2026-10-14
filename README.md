# lmcache-blogs

Pipeline tools, content, and assets to go from skeleton to publication.

LMCache merges more good PRs than anyone has time to write up. So contributors do not write
posts — they write a **skeleton**: rough notes, in their own language, about what was broken
and what was interesting about fixing it. The pipeline hydrates that skeleton with the PR's
own metadata and diff, assembles a prompt, and generates a draft. A human editor and the
original author review it before it goes out.

## I landed a PR and it deserves a post

[Open an issue](../../issues/new/choose) and choose **Blog
post from a PR**. Fill in the five sections marked `[CORE]`. Ten minutes is a normal amount
of time to spend, and a draft comes back to you within a day.

Write in whatever language you think in — do not translate for us. Rough is fine; fragments
and typos are fine. You are writing notes, not prose.

Two other ways in (a Google Doc, or a markdown file committed with your code) are in
**[`docs/blog-submission-process.md`](docs/blog-submission-process.md)**.

## I want to change the pipeline

Read **[`CONTRIBUTING.md`](CONTRIBUTING.md)**, then **[`AGENTS.md`](AGENTS.md)** — which
applies to humans and agents alike and is what a reviewer will hold your PR against.

## Map

```
.github/ISSUE_TEMPLATE/blog-post.md   the skeleton, canonical (GitHub reads this one)
docs/                                 the process
  blog-submission-process.md            contributor-facing: three intake paths
  pipeline/skeleton-to-prompt.md         machine-facing: parse and prompt contracts
  templates/blog-post-skeleton.md        downloadable copy of the skeleton
content/skeletons/                    filled skeletons committed via intake path C
content/drafts/                       written posts submitted as a PR for review (paths D and E)
tools/                                repo invariant checks used by pre-commit
.claude/skills/                        committed agent skills for the PR flow
```

## The state of it

The intake half is real: the template, the three paths, and the contracts they imply. The
automation half is not built yet — see "Not here yet" in
[`docs/README.md`](docs/README.md) for what is missing and roughly in what order.

## License

[Apache 2.0](LICENSE). Contributions are certified under the
[Developer Certificate of Origin](DCO) — sign off your commits with `git commit -s`.
