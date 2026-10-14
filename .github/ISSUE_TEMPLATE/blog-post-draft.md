---
name: Blog post draft — needs technical review
about: You wrote the post, but the technical content still wants checking before it goes out.
title: "[blog][draft] "
labels: ["blog", "draft", "needs-tech-review"]
---

<!--
USE THIS ONE IF THE POST IS WRITTEN BUT THE TECHNICAL CONTENT STILL NEEDS
CHECKING.

"Draft" here means exactly that: the writing is done, the verification is
not. Maybe you wrote up someone else's work, or you are describing a system
you do not own, or you would just rather a second pair of eyes confirmed the
details before your name is on it.

Pick a different template if:

  - the technical content is already sound, because you built the thing or
    because someone already reviewed it
    -> "Finished blog post - ready for copyedit"
  - you have notes or a PR and want someone else to write the post
    -> "Blog post from a PR"

Most posts that arrive already written belong in that first one. This
template is for the case where a technical review is genuinely wanted.

Your card skips Idea, Claimed, and Drafting and lands in the review lane you
pick below.

Do not delete any headings. The pipeline reads them by name. Leave a heading
empty rather than removing it.
-->

```yaml
draft:                # link to the doc, or attach the file to this issue
entry_lane: editorial # editorial | technical
author:
language: en          # the language the DRAFT is written in: en, zh, ko, ja, de...
post_type: how-to     # how-to | why-to | deep-dive | release-note
placement: lmcache    # lmcache | tensormesh — see "Placement" below
pr:                   # if it is about a PR; leave blank if not
repo: LMCache/LMCache
reader: # who is this for? e.g. "someone running vLLM in production and hitting TTFT limits"
publish_by: # date, or leave blank
```

## Where the draft is [CORE]

<!-- A link, or say "attached" and drag the file onto this issue. Google Doc,
markdown file, HTML, Notion page — whatever you have. If it is a doc, share
it so anyone at Tensormesh with the link can comment.

A pull request that adds the post under content/drafts/ also works, and is the
easiest to review line by line. See content/README.md for the layout.

If the draft lives in more than one place, say which one is authoritative.
Two versions of a finished post is the most expensive kind of confusion
here. -->

## What it says in one sentence [CORE]

<!-- The hallway version. Used for title candidates and the meta
description, and it tells a reviewer what they are about to read. -->

## Which lane it should enter [CORE]

<!-- Set `entry_lane` above. One sentence of why is plenty.

  editorial  — written, nobody has edited it. This is the normal choice.
               Goes to Editorial review, then Technical review.
  technical  — an editor has already been through it for structure and
               register, and what it needs is the correctness check.
               Goes straight to Technical review.

Either way it passes through Technical review, because that is what this
template is for. If it does not need technical review, you want the
"Finished blog post - ready for copyedit" template instead.

When unsure, pick editorial. -->

## Who has already reviewed it

<!-- Names and what they looked at. "Nobody" is a fine answer and is the
common one. If a reviewer's comments are in the doc, say so — that saves
the next reviewer from re-raising the same points. -->

## Where your claims come from

<!-- Optional, and there is no right format. Anything you put here makes the
technical review faster and more accurate; leaving it empty is allowed and
the review still happens.

What it is for: a reviewer's job is to check the claims in the post. Anything
that tells them where a claim came from saves them rediscovering it. That is
the whole idea.

Use whatever matches how you already work — we do not know or care what you
drafted in:

  - **Already in the post?** Say "links are inline" and skip the rest.
  - **A bullet list here.** Claim, then where it came from. The most common
    shape:
      - the 3.2x figure -> benchmark in PR #1234, run on the H100 box
      - the eviction behavior -> docs/design/v1/storage_backend/README.md
      - "most deployments hit this" -> support threads, roughly a dozen
  - **A pointer.** "Everything comes from PR #1234 and issue #987" is a
    complete answer when it is true.
  - **In the doc itself.** Comments, footnotes, a sources section at the
    bottom — just say where to look.
  - **Attach something.** A benchmark log, a spreadsheet, a transcript.

Most valuable thing you can do here, if you do nothing else: **flag what you
are least sure of.** "I believe this is right but I did not verify it
myself" points the reviewer straight at the part that needs them, and costs
you one line. -->

## What you are least sure about

<!-- Optional, and the single most useful line on this form. What in the post
would you most want a reviewer to check? A number, a claim about how
something behaves, a recommendation, a version constraint.

"Nothing, I am confident in all of it" is a fine answer — though if that is
true, the "Finished blog post" template is probably the faster path. -->

## Numbers and their conditions

<!-- Every benchmark or measurement in the draft, and the conditions it
holds under: hardware, model, batch size, workload shape. We will not
publish a number without its conditions, so if the draft has a number whose
conditions are not written down next to it, this is where you supply them.

If the draft has no numbers in it, say "none" and move on. -->

## Images and assets

<!-- Do you have diagrams, screenshots, or charts? Attach them or link them,
and say whether they are final or want redrawing. If a diagram needs
redrawing, describe what it should show in a sentence or two and we will draw
it. -->

## Who should care and what should they do [CORE]

<!-- Who should read this, and what is the very next thing they should do
after reading? Upgrade? Set a flag? Try a config? Read a doc? If the draft
already ends with this, just say "in the draft". -->

## What is still open

<!-- Known limits, edge cases that do not work yet, follow-up PRs, anything
you would like a reviewer to push back on. -->

## Placement

<!-- Is this LMCache-canonical or Tensormesh? Set `placement` above.

LMCache content is published as LMCache's. Tensormesh does not originate
LMCache content — so if you are unsure, say so here rather than guessing,
and it gets settled before anything is scheduled. -->

## Notes for the editor

<!-- Not published. Anything we should avoid saying, a customer we should
not name, an embargo date, a competitor comparison you would rather we did
not draw, how to spell your name and what title you want on the byline.

Also: how much editing are you comfortable with? Some people want a light
copy-edit only. Say so and we will respect it. -->
