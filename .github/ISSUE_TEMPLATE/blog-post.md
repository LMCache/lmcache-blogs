---
name: Blog post from a PR
about: Write short notes about a merged PR. We turn them into a blog post.
title: "[blog] "
labels: ["blog", "skeleton"]
---

<!--
HOW TO USE THIS

Write in your own language: Chinese, English, or any other.
Do NOT translate. Translation loses details, and we translate the post
later.

Write as you would explain it to a teammate. Rough notes, short phrases,
and typos are fine. An editor and a model write the post from your notes.

IN A HURRY? Fill in only the sections marked [CORE]. That takes about ten
minutes and is enough to start.

Do not delete or rename any heading. The pipeline reads them by name.
Leave a section empty instead.
-->

```yaml
pr: https://github.com/LMCache/LMCache/pull/
repo: LMCache/LMCache
author:
language: en          # the language YOU wrote this skeleton in: en, zh, ko, ja, de...
post_type: how-to     # how-to | why-to | deep-dive | release-note
reader: # who is this for? e.g. "someone running vLLM in production and hitting TTFT limits"
publish_by: # date, or leave blank
```

## The one-liner

<!-- One sentence. How would you tell a colleague what this PR does? Not
the commit message. -->

## What was wrong before [CORE]

<!-- 2-4 sentences. What was broken, missing, slow, or hard to use? What
did you see: an error, a bad graph, a user complaint? Describe the
symptom exactly. -->

## Why it mattered [CORE]

<!-- Who had this problem, and what did it cost them? Latency, memory,
money, operations work, blocked work. Give numbers if you have them.
Estimates are fine ("about a third of requests", "every restart"). -->

## What we did [CORE]

<!-- The idea behind the change, in your own words. Do not describe the
diff. Also: what other options did you consider, and why did you reject
them? Readers often find this the most interesting part. -->

## The interesting part [CORE]

<!-- THIS IS THE MOST IMPORTANT SECTION. If you write a lot in one
section, write it here. Answer any of these:

  - What surprised you?
  - What did you try first that did not work?
  - What made this harder than it looked?
  - What should the next person be careful about?
  - Did you learn that the problem was different from what you thought?

Without this section, the post is only a changelog. -->

## Show me the code [CORE]

<!-- Paste the smallest code snippet that explains the change. Before and
after is good. Paste the code; do not describe it. Include the file path. -->

## Numbers

<!-- Benchmarks, before and after, throughput, memory, TTFT. Also give the
test conditions: hardware, model, batch size, workload. We do not publish
a number without its conditions. -->

## Who should care and what should they do [CORE]

<!-- Who should read this? What should they do next: upgrade, set a flag,
try a config, read a doc? -->

## What is still open

<!-- Known limits, cases that do not work yet, follow-up PRs, and where
you want help. Readers trust a post that states its limits. -->

## Pictures in your head

<!-- Did you picture a diagram while you worked on this? A flow, where the
data sits before and after, a timeline? Describe it in one or two
sentences and we will draw it. Example: "A box for the GPU, a box for CPU
memory, and an arrow that went both ways and now goes one way." -->

## Anything else

<!-- Related PRs and issues, earlier work, the discussion thread, papers,
and people to credit by name. -->

## Notes for the editor

<!-- Optional. This issue is public: do not write anything here that you
would not publish. Use this section for practical notes, such as when the
post should go out or a question for the editor. -->
