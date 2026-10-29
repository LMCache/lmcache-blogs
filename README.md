# lmcache-blogs

This repo holds the tools, content, and assets that turn LMCache pull requests
(PRs) into blog posts. Contributors do not write the post. They write a
**skeleton**: rough notes about what was broken and how they fixed it. The
pipeline adds the PR's metadata and diff, builds a prompt, and generates a
draft. An editor and the original author review the draft before it is
published.

To propose a post, [open an issue](../../issues/new/choose) and choose **Blog
post from a PR**. To change the pipeline, read
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Propose a post about your PR

[Open an issue](../../issues/new/choose), choose **Blog post from a PR**, and
fill in the five sections marked `[CORE]`. This takes about ten minutes. A
draft comes back within one day. Write in the language you think in, and do
not translate. Fragments and typos are fine.

You can also submit through a Google Doc or a markdown file committed with your
code. See [`docs/blog-submission-process.md`](docs/blog-submission-process.md).

## Change the pipeline

Read [`CONTRIBUTING.md`](CONTRIBUTING.md), then [`AGENTS.md`](AGENTS.md).
`AGENTS.md` applies to humans and agents, and reviewers check PRs against it.

## Map

```
.github/ISSUE_TEMPLATE/blog-post.md   the skeleton, canonical (GitHub reads this one)
docs/                                 the process
  blog-submission-process.md            contributor-facing: five intake paths
  pipeline/skeleton-to-prompt.md         machine-facing: parse and prompt contracts
  templates/blog-post-skeleton.md        downloadable copy of the skeleton
content/skeletons/                    filled skeletons committed via intake path C
content/drafts/                       written posts submitted as a PR for review (paths D and E)
events/                               slides and an index for each LMCache community event
tools/                                repo invariant checks used by pre-commit
.claude/skills/                       committed agent skills for the PR flow
MAINTAINERS.md                        who maintains this repo and how to reach them
```

## Status

The intake side is built: the templates, the five intake paths, and their
contracts. The automation side is not built yet. See "Not here yet" in
[`docs/README.md`](docs/README.md) for what is missing and the planned order.

## License

[Apache 2.0](LICENSE). Contributions are certified under the
[Developer Certificate of Origin](DCO). Sign off your commits with
`git commit -s`.
