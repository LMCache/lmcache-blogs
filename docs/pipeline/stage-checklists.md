# Stage checklists

When a card enters a column, the board automation posts that column's checklist
on the issue, once for each time the card enters it. Edit a checklist here; the
next card to enter that column gets the new text. No code change is needed.

Each `## <Column>` heading must match a column on the content board exactly. A
column with no section here gets no comment. Everything under a heading, up to
the next `##`, is posted as written, so keep each list short enough to read in
the issue.

## Claimed

- [ ] Assign yourself, so the card has an owner people can ask.
- [ ] Fill in the five `[CORE]` sections of the skeleton. Ten minutes is normal.
- [ ] Write in the language you think in. We localize later.

## Drafting

- [ ] The draft names its PR in the first two paragraphs.
- [ ] Every `QUESTION FOR AUTHOR` block is answered in a comment.
- [ ] For a written post, open a PR under `content/drafts/<slug>/` with a
      `Post: #<this issue>` line in its body.

## Editorial review

- [ ] The post is useful to a reader who never adopts the change.
- [ ] The opening is the problem, not the fix.
- [ ] Structure, register, and clarity follow house style. The author's own
      descriptions of their work stay in their words.
- [ ] `Notes for the editor` has been read, and nothing from it appears in the
      post.
- [ ] Approve the draft PR when this stage is done. The approval moves the card.

## Technical review

- [ ] Every item in the claims ledger is checked against its source.
- [ ] Every number carries its conditions (hardware, model, batch size,
      workload shape) in the same sentence or the next one.
- [ ] No capability is claimed that the diff does not show.
- [ ] Code is shown exactly as it is in the source, with its file path. Nobody
      edited it for the post.
- [ ] Approve the draft PR when this stage is done. The approval moves the card.

## Copyedit

- [ ] Spelling, grammar, and consistency are correct. Write "KV cache" with
      "cache" in lowercase, and with no hyphen unless grammar requires one.
- [ ] Remove phrases that read as machine-written, such as "leverage",
      "seamlessly", and "delve", and several short sentences in a row with the
      same rhythm.
- [ ] Every image has alt text and its source is credited.
- [ ] If the author asked for a light copyedit, keep to that.
- [ ] Approve the draft PR when this stage is done. The approval moves the card.

## Translations

- [ ] Open one sub-issue of this post for each target language, labelled
      `l10n`. Each one gets its own card here.
- [ ] Leave product names, flags, config keys, and API names in English unless
      the author asked otherwise.
- [ ] Record each change that the translator makes for idioms. We use these
      records to improve the prompts.
- [ ] This card moves to Published when the draft PR merges and every
      translation sub-issue is closed.
