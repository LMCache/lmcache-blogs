---
name: Finished blog post — ready for copyedit
about: A finished post that is already technically verified. It needs a copyedit only.
title: "[blog][final] "
labels: ["blog", "complete", "tech-verified"]
---

<!--
USE THIS TEMPLATE IF THE POST IS DONE AND THE TECHNICAL CONTENT IS ALREADY
CORRECT.

This is the normal template for a post by the person who built the feature,
or a post that another organization already reviewed. These posts do not
need our technical review.

Use a different template if:

  - someone still needs to check the technical claims
    -> "Blog post draft - needs technical review"
  - you have notes or a PR and want someone else to write the post
    -> "Blog post from a PR"

Your card goes to Editorial review for the copyedit, then to Translations.
It does not go through Technical review.

Most sections need one line. Only "Who verified the technical content"
needs thought.

Do not delete or rename any heading. The pipeline reads them by name.
Leave a section empty instead.
-->

```yaml
post:                 # link to it, or attach the file to this issue
author:
language: en          # the language the POST is written in: en, zh, ko, ja, de...
post_type: how-to     # how-to | why-to | deep-dive | release-note
verified_by: author   # author | own-org | external-review — see below
copyedit: full        # full | light
publish_by: # date, or leave blank
pr:                   # if it is about a PR; leave blank if not
repo: LMCache/LMCache
```

## Where the finished post is [CORE]

<!-- A link, or write "attached" and drag the file onto this issue. Any
format: Google Doc, markdown, HTML, Notion, or a URL where it is already
published.

A pull request that adds the post under content/drafts/ also works, and is
the easiest to review line by line. See content/README.md for the layout.

If the post is in more than one place, say which copy is the main one. -->

## What it says in one sentence [CORE]

<!-- One plain sentence. We use it for the title, the meta description,
and to tell the copyeditor what the post is about. -->

## Who verified the technical content [CORE]

<!-- Usually one line. Set `verified_by` above, and name the person in one
sentence. We accept your statement and record it.

  author          — you built the feature in this post. "I wrote the
                    feature" is enough.
  own-org         — someone at your organization reviewed it. Give their
                    name or role.
  external-review — it was reviewed elsewhere: published on another site,
                    presented at a conference, or reviewed by a third
                    party. Say where.

If you do not know what to write here, use the "Blog post draft - needs
technical review" template instead. -->

## How much editing are you comfortable with [CORE]

<!-- Set `copyedit` above. Add details if needed.

  full  — we can change structure, style, and wording, within house style.
  light — copyedit only: grammar, typos, consistency, and formatting. We do
          not change structure or wording.

If some passages must not change (a quote, a careful caveat), list them. -->

## Numbers and their conditions

<!-- We do not re-check your numbers. But we do not publish a number
without its test conditions: hardware, model, batch size, workload.

Does every number in the post state its conditions? If yes, write "yes,
in the post". If not, give the missing conditions here.

If the post has no numbers, write "none". -->

## Images and assets

<!-- Attach or link any diagrams, screenshots, or charts. Say whether each
one is final or needs redrawing. For a redraw, describe in one or two
sentences what it should show, and we will draw it.

If the post has no images but needs one, say what it should show. -->

## Translation notes

<!-- Optional. The post goes to Translations after the copyedit.

List anything that must stay in English: product names, flags, config
keys, API names, terms. Name any languages you want, or a colleague who
should review a translation. -->

## Notes for the editor

<!-- Optional. This issue is public: do not write anything here that you
would not publish. Use this section for practical notes, such as when the
post should go out or a question for the editor.

If the post is already published somewhere else, say where and when. We
handle a republished post differently from a new one. -->
