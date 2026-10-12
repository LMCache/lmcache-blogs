# Board routing

This document explains how an issue becomes a card in the right column, and
what happens to issues that fit no rule.

The mechanism is `.github/workflows/content-board.yml` plus
[`tools/board_router.py`](../../tools/board_router.py). The board is
**LMCache Blogs [Editorial Kanban]** at `github.com/orgs/LMCache/projects/6`.
The router reads the board's location at runtime; see
[Locating the board](#locating-the-board).

## Setup: one required secret

`GITHUB_TOKEN` cannot write to a Projects V2 board. No workflow permission
grants it, because Projects V2 is outside the repository permission model. The
workflow needs its own token in a secret named `PROJECT_TOKEN`.

### Which token to use

Fine-grained PATs offer a `Projects` permission only under Organization
permissions. There is no account-level equivalent. GitHub offers the
organization-level permission only to an organization owner. The right token
depends on who owns the board and on your role:

| Board owner | You are | Token |
|---|---|---|
| **A user account** | the owner | a **classic** PAT with the `project` scope; nothing narrower exists |
| **An organization** | a **Member** | a **classic** PAT with the `project` scope — the org-level `Projects` permission is not offered to you |
| **An organization** | an **Owner** | a **fine-grained** PAT with the org-level `Projects` permission, scoped to this one repository |
| **An organization** | — | a **GitHub App** installed on the org by an owner. No personal token at all |

For a user-owned board, a fine-grained token cannot express "read and write my
projects". This is a
[long-standing open request](https://github.com/orgs/community/discussions/36441).

The Member row was confirmed after this repo moved to `LMCache`. An LMCache
Member created a fine-grained token with `LMCache` as the resource owner. The
org appeared in the dropdown, but `Projects` was not among the Organization
permissions. With an org he owns as the resource owner, the same page offered
`Projects`.

A classic token routes the board today. The classic `project` scope cannot be
limited to one project or one repository: the token can read and write every
project its account can reach. The narrow alternative is a GitHub App that an
org owner installs on the org. The org owns the App, its permissions are
narrow, and it keeps working when a person leaves.

Unless you own the org that owns the board:

1. Create a **classic** personal access token with the **`project`** scope
   (Settings → Developer settings → Personal access tokens → Tokens (classic)).
2. Add it to this repo as a secret named `PROJECT_TOKEN`:

   ```bash
   gh secret set PROJECT_TOKEN --repo <owner>/lmcache-blogs
   ```

   The command prompts for the value. Do not use `--body "<token>"`, which
   puts the token in your shell history. For a non-interactive alternative,
   use `gh secret set PROJECT_TOKEN < tokenfile`.

## Locating the board

The router has no board address in its code. It reads two environment
variables, which you set as repository **variables** (Settings → Secrets and
variables → Actions → Variables):

| Variable | Required | Meaning |
|---|---|---|
| `BOARD_NUMBER` | **yes** | The project's number. |
| `BOARD_OWNER` | no | The login that owns the board. Defaults to this repository's owner. |

Set `BOARD_OWNER` only when the board belongs to a different account than the
repository. The default lets the repository move to a new owner without a code
change.

`BOARD_NUMBER` has no default. Project numbers are small integers that every
account reuses, so a wrong guess would not fail: it would write cards onto
another account's board. If `BOARD_NUMBER` is unset, the router raises an
error.

The GraphQL query uses `repositoryOwner`, which resolves a user and an
organization the same way. The router works with either kind of owner.

Routing is inactive until both `BOARD_NUMBER` and `PROJECT_TOKEN` exist. The
`preflight` job checks for each, writes a plain-English notice to the run
summary, and emits a warning annotation. The other jobs then skip, instead of
failing one API call at a time. Issues are still filed and labelled correctly
in the meantime. The first sweep after setup places all of them.

## The routing table

Routing uses labels, because a human can see, edit, and search a label. For
path D, the `entry_lane` value in the issue's YAML block also selects the
column, because a label cannot say which review a draft needs.

| Labels | Column | Triage? |
|---|---|---|
| `skeleton` | Drafting | no |
| `needs-tech-review` + `entry_lane: editorial` | Editorial review | no |
| `needs-tech-review` + `entry_lane: technical` | Technical review | no |
| `needs-tech-review`, no `entry_lane` | Editorial review | no — the documented default |
| `needs-tech-review` + an unrecognised `entry_lane` | Editorial review | **yes** |
| `tech-verified` | Editorial review | no |
| more than one of the three intake labels | Idea | **yes** |
| `blog`, but no intake label | Idea | **yes** |
| `pipeline` | *off the board* | no |
| neither `blog` nor `pipeline` | *off the board* | **yes** |

## Nothing is ignored, and nothing dead-ends

The router guarantees that every issue either gets a column or gets flagged.

**Every input produces a decision.** `route()` returns a column or an explicit
decision to stay off the board for any set of labels, always with a
one-sentence reason. It has no fall-through branch.
[`tests/test_board_router.py`](../../tests/test_board_router.py) checks every
combination of the labels in play, with valid and invalid lanes.

An issue that the router cannot place gets the `needs-triage` label and a
comment that says why. Find these issues with
`is:issue is:open label:needs-triage`. The router posts the comment once;
re-runs do not repeat it.

Only two cases stay off the board. A `pipeline` issue stays off because the
board's columns are editorial lanes, and "Published" means nothing for a parser
bug. An issue with neither `blog` nor `pipeline` stays off and is triaged,
because nobody has classified it.

An unrecognised `entry_lane` still gets a card in Editorial review, and it is
triaged. Leaving it off the board would be worse. Choosing a lane by inference
could skip a review on something about to be published.

Two intake labels make the author's intent unknown. The router does not let one
label win by branch order. It routes the issue to Idea and triages it.

The `issues` event handles new and changed issues. The hourly `sweep` job
routes every open issue that is not already on the board. This covers issues
that predate the workflow, arrived while it was failing, or were missed.
`workflow_dispatch` runs the sweep on demand. Its `dry_run` input logs each
decision and changes nothing.

GitHub drops an issue-template label that does not exist in the repository,
with no error. Every intake issue would then be unlabelled and unroutable. This
happened once: all seven template labels were missing when the templates were
first written. The `ensure-labels` job reads the labels that the templates
declare and creates any that are missing.

## What this does not do

- The router never moves a card forward through the lanes. It sets a card's
  entry column only.
- The `issues` event re-routes on every `opened`, `reopened`, `labeled`,
  `unlabeled`, or `edited` event. It sets the column even if the card is
  already on the board, so an edit to an issue resets a card that a human
  moved. The sweep skips issues that are already on the board.
- The sweep reads at most 200 open issues and the first 100 board items. Past
  100 items, it sees some on-board issues as missing and re-routes them.
- No stall detection. The process doc promises a nudge when a card waits on
  someone for more than two days. That needs Slack and is not built.
- No closed-issue handling. A closed issue keeps its card where it was. Whether
  "closed" means abandoned or published is an open policy question.

## Running it locally

```bash
export GH_TOKEN=$(gh auth token)
export PROJECT_TOKEN=<a token with project scope>

# What would happen, changing nothing
python tools/board_router.py sweep --repo <owner>/lmcache-blogs --dry-run

# One issue
python tools/board_router.py route --repo <owner>/lmcache-blogs --issue 12 --dry-run
```

Set `BOARD_NUMBER` (and `BOARD_OWNER` if needed) in the environment too.

Tests:

```bash
pip install -r requirements/test.txt
pytest tests/ -q
```

## Changing the rules

The routing table above, `route()` in the router, and the `Routing` sections of
the parse contracts describe one agreement. They can drift apart without
warning. If you change a label, a lane, or a column:

1. Update `route()` and its tests. Add any new column to the assertion in
   `test_every_routed_column_is_a_real_column`.
2. Update this table and the `Routing` section of the parse contract.
3. Confirm that the column exists on the board. The router raises an error if
   it does not, so a typo fails loudly, but only at runtime.
