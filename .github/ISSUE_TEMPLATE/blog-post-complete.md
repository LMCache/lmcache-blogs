---
name: Finished blog post — ready for copyedit
about: Technically complete and already verified. Needs a copyedit, then translation and publishing.
title: "[blog][final] "
labels: ["blog", "complete", "tech-verified"]
---

<!--
USE THIS ONE IF THE POST IS DONE AND THE TECHNICAL CONTENT IS ALREADY SOUND.

That is the normal case for a post written by the person who built the thing,
and for a post coming from another organization that already reviewed it.
Those do not need our technical review, and sending them through it wastes
your time and the reviewer's.

Pick a different template if:

  - the post still needs someone to check the technical claims
    -> "Blog post draft - needs technical review"
  - you have notes or a PR and want someone else to write the post
    -> "Blog post from a PR"

Your card enters Editorial review for the copyedit, then goes to
Translations. It does not pass through Technical review.

Most of this is one line per section. Only the third one needs thought.

Do not delete any headings. The pipeline reads them by name. Leave a heading
empty rather than removing it.
-->

```yaml
post:                 # link to it, or attach the file to this issue
author:
language: en          # the language the POST is written in: en, zh, ko, ja, de...
post_type: how-to     # how-to | why-to | deep-dive | release-note
placement: lmcache    # lmcache | tensormesh — see "Placement" below
verified_by: author   # author | own-org | external-review — see below
copyedit: full        # full | light
publish_by: # date, or leave blank
pr:                   # if it is about a PR; leave blank if not
repo: LMCache/LMCache
```

## Where the finished post is [CORE]

<!-- A link, or say "attached" and drag the file onto this issue. Google Doc,
markdown, HTML, Notion, a published URL elsewhere — whatever you have. We do
not care what you wrote it in.

A pull request that adds the post under content/drafts/ also works, and is the
easiest to review line by line. See content/README.md for the layout.

If it exists in more than one place, say which one is authoritative. Two
versions of a finished post is the most expensive kind of confusion here. -->

## What it says in one sentence [CORE]

<!-- The hallway version. Used for title candidates and the meta description,
and it tells the copyeditor what they are about to read. -->

## Who verified the technical content [CORE]

<!-- The one section that matters here, and it is usually one line.

You are telling us this post does not need technical review. That is almost
always true and we are taking your word for it — this section is just the
record of whose word it was. Set `verified_by` above and say who, in a
sentence:

  author          — you built the thing this post is about, so the technical
                    content is yours and you already know it is right.
                    "I wrote the feature" is a complete answer.
  own-org         — someone at your organization reviewed it before it came
                    to us. Name them or their role.
  external-review — it went through review somewhere else: published on
                    another site, presented at a conference, reviewed by a
                    third party. Say where.

If you find yourself unsure what to put here, that is a useful signal: the
post probably wants the draft template and a technical review instead. No
harm in that, and it is faster than a correction after publishing. -->

## How much editing are you comfortable with [CORE]

<!-- Set `copyedit` above and add anything specific.

  full  — treat it like any other post. Structure, register, and clarity are
          ours to adjust, within house style.
  light — copyedit only. Grammar, typos, consistency, formatting. Leave the
          structure and the phrasing alone.

Either is fine and nobody will argue with you. Saying which one saves a round
trip. If particular passages should not be touched — a quote, a carefully
worded caveat, a line you fought for — name them. -->

## Numbers and their conditions

<!-- Not a re-review of your numbers. This is one specific check that applies
to every post regardless of who verified it: we do not publish a figure
without the conditions it holds under — hardware, model, batch size, workload
shape.

So: does every number in the post already carry its conditions nearby? If yes,
say "yes, in the post". If some are missing, supply them here rather than
making the copyeditor guess or cut the number.

If there are no numbers, say "none". -->

## Images and assets

<!-- Diagrams, screenshots, charts. Attach or link them, and say whether they
are final or want redrawing. If something needs redrawing, describe what it
should show in a sentence or two and we will draw it.

If the post has no images and you think it wants one, say what it would
show. -->

## Translation notes

<!-- Your card goes to Translations after the copyedit, so this is worth
thirty seconds.

Anything that should NOT be translated — product names, flags, config keys,
API names, a term of art you want left in English? Any languages you
specifically want this in, or a colleague who should review a particular
localization? Leave blank if you have no preference. -->

## Placement

<!-- Is this LMCache-canonical or Tensormesh? Set `placement` above.

LMCache content is published as LMCache's. Tensormesh does not originate
LMCache content — so if you are unsure, say so here rather than guessing, and
it gets settled before anything is scheduled.

If the post has already been published somewhere else, say where and when. A
republished piece is handled differently from an original. -->

## Notes for the editor

<!-- Not published. Anything we should avoid saying, a customer we should not
name, an embargo date, a competitor comparison you would rather we did not
draw, how to spell your name and what title you want on the byline. -->
