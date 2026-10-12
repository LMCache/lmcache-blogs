---
name: Blog post draft — needs technical review
about: A written post whose technical content needs review before it is published.
title: "[blog][draft] "
labels: ["blog", "draft", "needs-tech-review"]
---

<!--
USE THIS TEMPLATE IF THE POST IS WRITTEN BUT THE TECHNICAL CONTENT IS NOT
CHECKED.

For example: you wrote about someone else's work, you describe a system you
do not own, or you want a second person to confirm the details.

Use a different template if:

  - the technical content is already correct, because you built the feature
    or someone already reviewed it
    -> "Finished blog post - ready for copyedit" (most written posts)
  - you have notes or a PR and want someone else to write the post
    -> "Blog post from a PR"

Your card skips Idea, Claimed, and Drafting. It goes to the review lane you
choose below.

Do not delete or rename any heading. The pipeline reads them by name.
Leave a section empty instead.
-->

```yaml
draft:                # link to the doc, or attach the file to this issue
entry_lane: editorial # editorial | technical
author:
language: en          # the language the DRAFT is written in: en, zh, ko, ja, de...
post_type: how-to     # how-to | why-to | deep-dive | release-note
pr:                   # if it is about a PR; leave blank if not
repo: LMCache/LMCache
reader: # who is this for? e.g. "someone running vLLM in production and hitting TTFT limits"
publish_by: # date, or leave blank
```

## Where the draft is [CORE]

<!-- A link, or write "attached" and drag the file onto this issue. Any
format: Google Doc, markdown, HTML, Notion. If it is a doc, share it so
that anyone with the link can comment.

A pull request that adds the draft under content/drafts/ also works, and is
the easiest to review line by line. See content/README.md for the layout.

If the draft is in more than one place, say which copy is the main one. -->

## What it says in one sentence [CORE]

<!-- One plain sentence. We use it for the title, the meta description,
and to tell the reviewer what the post is about. -->

## Which lane it should enter [CORE]

<!-- Set `entry_lane` above. Add one sentence about why.

  editorial  — nobody has edited it yet. This is the normal choice.
               Goes to Editorial review, then Technical review.
  technical  — an editor already checked structure and style. It needs
               only the correctness check. Goes to Technical review.

Both lanes include Technical review. If the post does not need technical
review, use the "Finished blog post - ready for copyedit" template.

If you are not sure, choose editorial. -->

## Who has already reviewed it

<!-- Names, and what each person checked. "Nobody" is a normal answer. If
reviewer comments are in the doc, say so, so the next reviewer does not
repeat them. -->

## Where your claims come from

<!-- Optional. Any format. This makes the technical review faster. The
review still happens if you leave it empty.

Choose whatever is easiest:

  - "Links are inline in the post."
  - A list: the claim, then its source. Example:
      - the 3.2x figure -> benchmark in PR #1234, run on the H100 box
      - the eviction behavior -> docs/design/v1/storage_backend/README.md
      - "most deployments hit this" -> support threads, about a dozen
  - One pointer: "Everything comes from PR #1234 and issue #987."
  - "See the comments, footnotes, or sources section in the doc."
  - An attachment: a benchmark log, a spreadsheet, a transcript. -->

## What you are least sure about

<!-- Optional, but very useful. What should the reviewer check first? A
number, a claim about behavior, a recommendation, a version requirement.

If you are sure of everything, the "Finished blog post" template is
probably faster. -->

## Numbers and their conditions

<!-- List every benchmark or measurement in the draft, with its test
conditions: hardware, model, batch size, workload. We do not publish a
number without its conditions. If the draft does not state the conditions
next to a number, give them here.

If the draft has no numbers, write "none". -->

## Images and assets

<!-- Attach or link any diagrams, screenshots, or charts. Say whether each
one is final or needs redrawing. For a redraw, describe in one or two
sentences what it should show, and we will draw it. -->

## Who should care and what should they do [CORE]

<!-- Who should read this? What should they do next: upgrade, set a flag,
try a config, read a doc? If the draft already says this, write "in the
draft". -->

## What is still open

<!-- Known limits, cases that do not work yet, follow-up PRs, and anything
you want the reviewer to question. -->

## Notes for the editor

<!-- Optional. This issue is public: do not write anything here that you
would not publish. Use this section for practical notes, such as when the
post should go out or a question for the editor.

Also: how much editing do you accept? If you want only a light copyedit,
say so. -->
