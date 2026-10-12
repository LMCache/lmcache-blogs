# Skeleton → prompt

This document is the contract for turning a filled skeleton into the prompt
that generates a "story of a PR" post. It is the pipeline-facing half of the
template pair.

The skeleton lives at
[`.github/ISSUE_TEMPLATE/blog-post.md`](../../.github/ISSUE_TEMPLATE/blog-post.md)
(canonical) and [`../templates/blog-post-skeleton.md`](../templates/blog-post-skeleton.md)
(the downloadable copy). Its `##` headings are this document's schema. If you
change a heading there, change the parse contract below in the same PR.
Otherwise the parser drops the field without an error.

## Why the skeleton is markdown and not a YAML issue form

There are three intake surfaces: issue body, attached `.md` file, and exported
Google Doc. A YAML issue form works on only one of them. A markdown skeleton
with stable `##` headings works on all three, so the pipeline needs one parser
and one prompt assembler.

Nothing enforces that a heading is filled in, so the parser must handle empty
sections (see "Empty required field" below).

To add form validation later, add a YAML form that emits this exact markdown
as the issue body. The downstream pipeline does not change.

## Parse contract

1. Split the document on `^## ` headings.
2. Strip HTML comments. They are instructions to the human and are never input
   to the model.
3. Read the fenced `yaml` block at the top as front matter.
4. If the skeleton arrives as an attached `.md` file (path C), discard the
   `---`-delimited block above the fenced block. It is GitHub issue-template
   metadata (`name`, `about`, `title`, `labels`), not skeleton content. It is
   absent from an issue body because GitHub consumes it when it creates the
   issue.
5. Strip the ` [CORE]` suffix before you match a heading against the table
   below.

Six headings carry ` [CORE]`, and the suffix is part of the literal heading
text. The raw heading is `What was wrong before [CORE]`; the field name is
`What was wrong before`. A parser that matches the raw text drops exactly the
six fields that carry the post.

| Skeleton field | Machine key | Required |
|---|---|---|
| front matter | `meta.*` | `pr`, `author`, `language`, `post_type` |
| The one-liner | `oneliner` | no |
| What was wrong before | `problem` | **yes** |
| Why it mattered | `stakes` | **yes** |
| What we did | `approach` | **yes** |
| The interesting part | `story` | **yes** |
| Show me the code | `code` | **yes** |
| Numbers | `numbers` | no |
| Who should care and what should they do | `cta` | **yes** |
| What is still open | `open` | no |
| Pictures in your head | `imagery` | no |
| Anything else | `refs` | no |
| Notes for the editor | `editor_notes` | no — **never rendered** |

## Hydration

Before prompt assembly, enrich the bundle from the PR named in front matter:

- PR title, description, merge date, author, and reviewers
- Full diff, plus a file-level summary (paths, lines changed)
- Linked issues and their bodies
- Review conversation, if any. It often holds `story` material when the
  author left that field thin.

## Field → function in the post

Tell the generator what each field is for, so the output does not read like a
changelog.

- `oneliner` → title candidates, meta description, and the lede.
- `problem` → the opening. The hook is the symptom, not the solution.
- `stakes` → the paragraph that tells the reader why to keep reading. Also
  drives SEO framing and keyword selection.
- `approach` → the first body section, including the alternative the author
  rejected.
- `story` → the narrative spine. Build at least one section around it.
  Preserve the author's specific phrasing where it is vivid.
- `code` → rendered verbatim with the file path, plus explanation. Never
  reformat or "improve" it.
- `numbers` → the results section. Every figure carries its conditions in the
  same sentence or the adjacent one.
- `cta` → a "who this is for" line near the top, and the closing action.
- `open` → a limitations section. Keep it a section; do not reduce it to an
  aside.
- `imagery` → image prompts, routed to the whitePrint style. Not rendered as
  prose.
- `refs` → inline links and credits.
- `editor_notes` → constraints on the generator. Never appears in output.

## Output contract

The generator returns:

1. Three title options, marked for SEO weight
2. Slug and meta description
3. Target keywords, with the primary one named
4. The post, in markdown, with the PR linked in the first two paragraphs
5. Image prompt list: one per idea in `imagery`, plus at most one that the
   generator proposes, marked as proposed
6. **Claims ledger** (see below)
7. `QUESTION FOR AUTHOR` blocks, if any

## The claims ledger

List every factual assertion in the draft that did not come from the
skeleton, the diff, or a linked issue. Put the list at the end, with a pointer
to where each assertion appears in the post.

Technical review then checks the ledger instead of re-reading the whole piece
for invented claims. This is the main lever on edit time per piece, which is
the metric the pipeline reports.

## Rules the generator is given

- Do not invent numbers. If `numbers` is empty, the post has no benchmarks.
- Do not state a number without its conditions.
- Do not claim a capability that the diff does not show.
- Preserve the author's voice in `story`. Keep their vivid wording instead of
  rewriting it into house style.
- Apply house style to structure, register, and clarity. Do not apply it to
  the author's specific descriptions.
- Write for a reader who has the problem.
- Use second person and present tense. Do not use "revolutionary",
  "seamlessly", or "in today's fast-paced world".
- Make the post useful to a reader who never adopts the change.

## Empty required field

Do not fabricate. Do not continue silently. Emit:

```
QUESTION FOR AUTHOR — [field]
[the specific question, referencing what the diff appears to show]
```

The pipeline posts these as a comment on the issue and moves the card back to
the author's column. A draft with open questions never advances to editorial.

## Prompt skeleton (assembled)

```
You are drafting a technical blog post for the LMCache project.

HOUSE STYLE
{house_style_block}

WHAT YOU ARE WRITING
A "story of a PR" post: type {meta.post_type}, for this reader:
{meta.reader}. The narrative spine is the author's account in THE
INTERESTING PART. Build the piece around it.

The author wrote this skeleton in {meta.language}. Write the post in
English. Preserve their specific descriptions and examples; do not
flatten their voice into generic technical prose.

AUTHOR'S SKELETON
{all populated fields, labeled, verbatim}

THE PULL REQUEST
{pr_metadata}
{file_summary}
{diff}
{linked_issues}
{review_conversation}

CONSTRAINTS FROM THE EDITOR
{editor_notes}

RULES
{rules_block}

RETURN
{output_contract}
```

## Template two: a draft that needs technical review

Path D (`.github/ISSUE_TEMPLATE/blog-post-draft.md`) has a separate contract.
The post already exists, so this path has no hydration, no prompt assembly,
and no generator. The pipeline routes the card and gives a reviewer enough
context to review.

Use this path when the draft's technical content still needs checking. A
finished post that is already technically sound uses template three below and
skips Technical review. The author decides which applies.

Parse it the same way: split on `^## `, strip HTML comments, strip the
` [CORE]` suffix, and read the fenced `yaml` block as front matter.

| Draft field | Machine key | Required |
|---|---|---|
| front matter | `meta.*` | `draft`, `entry_lane`, `author`, `language` |
| Where the draft is | `draft_location` | **yes** |
| What it says in one sentence | `oneliner` | **yes** |
| Which lane it should enter | `entry_lane_why` | **yes** |
| Who has already reviewed it | `prior_review` | no |
| Where your claims come from | `sources` | no |
| What you are least sure about | `uncertain` | no |
| Numbers and their conditions | `numbers` | no |
| Images and assets | `assets` | no |
| Who should care and what should they do | `cta` | **yes** |
| What is still open | `open` | no |
| Notes for the editor | `editor_notes` | no — **never rendered** |

Five keys (`oneliner`, `numbers`, `cta`, `open`, and `editor_notes`) are
shared with the skeleton contract and mean the same thing. A parser can use
one field map for both templates.

### Routing

`meta.entry_lane` sets the column. It is the only thing on this path that
moves a card.

| `entry_lane` | Column |
|---|---|
| `editorial` | Editorial review |
| `technical` | Technical review |

Treat any other value as a validation error. Do not guess what the author
meant. Route the card to Editorial review and post a comment that says why.

### `sources` and `uncertain` are optional

A generated draft has a claims ledger. A human-written draft has none, and
one cannot be built afterward, because nothing records which sentences were
sourced. `sources` and `uncertain` let the author supply some of that by hand.

Both are optional, and an empty field is not an error. The post gets a full
technical review either way. Sourcing makes the review faster; it is not a
precondition for it.

When they are empty:

- Do **not** emit `QUESTION FOR AUTHOR`, and do **not** hold the card. Route
  it to its lane.
- Add a note for the reviewer: *"no sourcing supplied — claims need verifying
  from scratch."*
- Accept any shape: inline links in the draft, a bullet list, "it is all in
  PR #1234", comments in the doc, or an attached benchmark log. Store the
  section verbatim. Do not try to structure it.

Show `uncertain` prominently to the reviewer even though it is optional. It
names the part the author most wants checked.

### What still applies

These publishing rules hold on this path too. Technical review enforces them
against the draft as written.

- No number without its conditions in the same sentence or the adjacent one.
- `editor_notes` is never rendered.

## Template three: a finished post, ready for copyedit

Path E (`.github/ISSUE_TEMPLATE/blog-post-complete.md`). The post is written,
and its technical content is already sound: the author built the thing, their
organization reviewed it, or it was reviewed elsewhere. There is no generation
and no technical review. The pipeline routes the card to copyedit and records
who vouched for the technical content.

Most already-written submissions use this path. Template two is the
exception.

| Field | Machine key | Required |
|---|---|---|
| front matter | `meta.*` | `post`, `author`, `language`, `verified_by`, `copyedit` |
| Where the finished post is | `post_location` | **yes** |
| What it says in one sentence | `oneliner` | **yes** |
| Who verified the technical content | `verified_by_who` | **yes** |
| How much editing are you comfortable with | `edit_latitude` | **yes** |
| Numbers and their conditions | `numbers` | no |
| Images and assets | `assets` | no |
| Translation notes | `translation_notes` | no |
| Notes for the editor | `editor_notes` | no — **never rendered** |

### Routing

Path E always enters **Editorial review**, then moves to **Translations**. It
has no `entry_lane`, because copyedit is the only stage it needs.

Path E never passes through Technical review. If a path E card is in
Technical review, the author picked the wrong template or something re-routed
it. Post a comment; do not move it silently.

`meta.copyedit` sets how much latitude the editor has:

| `copyedit` | Means |
|---|---|
| `full` | structure, register, and clarity are the editor's, within house style |
| `light` | copyedit only — grammar, typos, consistency, formatting |

Honor `light` when it is set. The author has declined a rewrite.

### `verified_by` records who vouched

`verified_by` does not verify anything. It records who vouched for the
technical content, so a name is attached if a claim later proves wrong.

| `verified_by` | Means |
|---|---|
| `author` | the author built the thing the post describes |
| `own-org` | someone at the author's organization reviewed it |
| `external-review` | reviewed elsewhere — published, presented, or third-party |

Take it at face value. Do not re-derive it from the diff. Do not route the card
through Technical review because the attestation looks thin; that is the
round trip this path exists to avoid. If the field is missing or contradictory
(for example, `verified_by: author` on a post about someone else's subsystem),
ask in a comment.

Template three has no `sources` field, on purpose. A claims ledger would
require the technical review that this path skips.

### What still applies

Two publishing rules hold on every path. The copyeditor enforces them here.

- No number without its conditions in the same sentence or the adjacent one.
  The form asks the author to confirm this or supply what is missing. A
  missing condition is a question for the author. The editor never cuts the
  number or guesses the condition.

`editor_notes` is never rendered, as on every path.

### Count path E separately

The claims ledger exists to reduce edit minutes per piece. Path E has no
ledger and no technical review, so its pieces have a different cost profile
for reasons unrelated to pipeline improvement. **Count path E pieces
separately** so that they do not move the headline number.

## Human feedback loops

Every downstream edit is signal. The pipeline design names three capture
points:

1. Drafting: diffs between the generated draft and the author-revised draft
2. Editorial: diffs between the author-revised and the editor-approved draft
3. Localization: idiomatic changes that a localizing reviewer makes

Store the diff, the field it traces back to, and the editor's reason if one is
given. These feed prompt revisions and few-shot examples, and they reduce the
edit-minutes number over time.
