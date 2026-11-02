# Board automation

How a card moves on the content board after it is placed, and what happens
when a person moves one. Placement of a new issue is covered in
[`board-routing.md`](board-routing.md); this document starts where that one
stops.

The code is [`tools/board_automation.py`](../../tools/board_automation.py) for
GitHub reads and writes, and [`tools/board_stages.py`](../../tools/board_stages.py)
for the rules. The rules are pure functions with no network access, so every
transition below is covered by `tests/test_board_stages.py`.

## The short version

- **The board column is the source of truth.** Automation never moves a card
  back after a person moves it.
- **One PR per post.** A written post arrives as a PR under
  `content/drafts/<slug>/`, and the review stages happen as reviews on that PR.
- **The PR names its post** with a `Post: #N` line in its description.
- **People can move any card at any time.** The automation notices within
  about 15 minutes and follows along.

## How a card moves on its own

| Event | Card moves to |
|---|---|
| A draft PR opens, naming a post in Idea, Claimed, or Drafting | Editorial review |
| A maintainer approves the PR while the card is in Editorial review | the next review stage the post requires |
| A maintainer approves while the card is in Technical review | Copyedit |
| A maintainer approves while the card is in Copyedit | Translations |
| The PR merges, with no translation still open | Published |
| The PR merges while a translation is still open | Translations, to wait |
| The last translation of a merged post closes | Published |
| A translation sub-issue is closed | Published (that translation's own card) |

"The next review stage the post requires" depends on the post's route:

| Post labelled | Review stages, in order |
|---|---|
| `tech-verified` | Editorial review, Copyedit |
| anything else (`skeleton`, `needs-tech-review`, or only `blog`) | Editorial review, Technical review, Copyedit |

A post whose intake labels conflict takes the full route. When the path is
unclear, it asks for more review, not less.

### What counts as an approval

An approving review counts only if all of these hold:

- The reviewer is a maintainer: GitHub reports their association as `OWNER`,
  `MEMBER`, or `COLLABORATOR`. Anyone else's review is welcome but is not a
  stage gate.
- The reviewer is not the PR's author.
- It was submitted **after the card last changed column.**

The last rule is what makes each stage need its own sign-off. One approval
moves the card one stage, and after that the card's change time is later than
the approval, so the same approval never counts twice. An approval given while
the card sat in Drafting, before review began, does not count either.

"Request changes" and comments move nothing. The card stays in the stage being
reviewed until someone approves.

### Why the PR merges at publication

The draft PR stays open until the post is published, as
[`content/README.md`](../../content/README.md#drafts) says. So a merge means
the English post is out, and the card goes to Published. If translations are
still being written, the card waits in Translations, and moves to Published
when the last one closes.

A post with no translations at all is never moved to Published by the
translation rule. Its merge publishes it.

## Naming the post in a PR

Put this line in the PR description:

```
Post: #36
```

The full URL of the post's issue in this repository works too. Before `Post:`
existed, authors were told to write `Refs #N`, so a description with exactly
one `Refs #N` also counts. A description with several `Refs` and no `Post:`
line is ambiguous and is ignored.

Do **not** use `Fixes #N` or another closing keyword for the post. It would
close the post's issue when the PR merges, possibly while translations are
still in progress.

A PR that adds files under `content/drafts/` but names no post gets one comment
asking for the line. A PR that names an issue that is not a blog post gets one
comment saying so. Neither is ignored, and neither is commented on twice.

## When a person moves a card

GitHub cannot run a repository workflow when a card moves: that event is
available only to an organization webhook. So a scheduled job, the
**reconciler**, reads the whole board every 15 minutes and works out what
changed.

It keeps two hidden text fields on each card:

- **Synced status:** the column the reconciler last recorded.
- **Prior status:** the column a card was in before it reached Published.

When a card's column differs from its Synced status, someone moved it. The
reconciler then:

1. **Syncs a stage label** on the issue, such as `stage:copyedit`, so that
   search and filters agree with the board. It removes any stale `stage:*`
   label.
2. **Posts the checklist** for the column the card entered, from
   [`stage-checklists.md`](stage-checklists.md). It posts once each time the
   card enters a column, not on every run.
3. **Flags an odd move** with a comment, and **never reverts it**: a move
   backwards, or a move that skips a review stage this post requires. The
   comment asks the person to say why, which is often a perfectly good reason.
4. **Closes the issue** if the card reached Published, and records the column
   it came from.
5. **Restores a reopened post.** If an issue is reopened while its card is in
   Published, the card goes back to the column it came from.
6. **Records the new column** in Synced status, so the move is handled once.

Automation's own moves update Synced status at the same moment, so the
reconciler never mistakes them for a person's.

The reconciler also catches up on anything the event jobs missed: an approval
on a PR from a fork (fork PRs get no secrets on review events), or an event
that was dropped while another run held the queue.

### Turning it on is quiet

The first time the reconciler sees a card, it records its column and syncs its
stage label, and does nothing else. No checklist, no flag, no close. Turning the
automation on does not bury every existing card in comments, and it does not
close a card that was already in Published.

A card that predates the reconciler has no Prior status, so if its issue is
open while it sits in Published, it is left alone rather than "restored".

## Translations

Each translation is a **sub-issue** of the post it translates, one per
language, labelled `l10n`. The board adds sub-issues automatically, and the
router puts an `l10n` issue in Translations. A translation has no review stages
of its own.

Close a translation's issue when it is published, or move its card to
Published, which closes it. Either way the post is checked: if its draft PR has
merged and every translation is closed, the post moves to Published.

## What you can change on the board without touching code

| Change | Effect |
|---|---|
| Move a card | Handled, as above. |
| Edit an issue or its labels | The card stays where it is. |
| Add an issue to the board by hand | Recorded on the next run, quietly. |
| Edit a stage checklist | Change [`stage-checklists.md`](stage-checklists.md). |
| Add a column | Cards can be moved into it and get a stage label. It is not a review stage and gets no checklist until the checklist doc has a section for it. |

These need a code change in `tools/board_stages.py`, and the tests will tell
you what else depends on them:

| Change | Why |
|---|---|
| Reorder columns | The code's column order decides what counts as "backwards" and "skipped". |
| Rename a column | Moves, checklists, and labels look columns up by name. |
| Delete Synced status or Prior status | The reconciler keeps its state there. `setup` recreates them, empty, which makes every card "first seen" again. |

## Setup

Once per board, create the hidden fields:

```bash
python tools/board_automation.py setup --repo LMCache/lmcache-blogs
```

It is safe to run again; existing fields are left alone. The workflow needs the
same `PROJECT_TOKEN` secret and `BOARD_NUMBER` variable as the router; see
[`board-routing.md`](board-routing.md#setup-one-required-secret).

## Running it locally

```bash
export GH_TOKEN=$(gh auth token)
export PROJECT_TOKEN=<a token with project scope>
export BOARD_NUMBER=6

# The whole board: what would change, changing nothing
python tools/board_automation.py reconcile --repo LMCache/lmcache-blogs --dry-run

# One PR or one issue event
python tools/board_automation.py pr --repo LMCache/lmcache-blogs --number 45 --dry-run
python tools/board_automation.py issue --repo LMCache/lmcache-blogs --number 36 \
  --action edited --dry-run
```

## What this does not do

- **No stall reminders.** A card waiting on someone is not chased. That needs
  Slack; see issue #6.
- **No policy for closing a post that was abandoned.** Closing a post's issue
  outside Published leaves its card where it is. See issue #7.
- **Latency.** Event-driven moves happen within a minute or two. Manual moves are
  seen within about 15 minutes, because they can only be seen by polling.
