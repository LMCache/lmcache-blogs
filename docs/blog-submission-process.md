# How to get a blog post written

Five ways in. Pick whichever is least annoying for you.

**If the post is not written yet**, paths A, B, and C all end in the same
place: a card on the board with a skeleton attached. **You do not write the
post** — you write a skeleton, rough notes in your own language, and the
pipeline plus an editor turn it into a post. You review it before it goes
out.

**If the post is already written**, there are two paths and the difference
is only this: *does the technical content still need checking?*

- **No — it is already sound**, because you built the thing, or because
  someone at your org or a third party already reviewed it. That is the
  common case. → [Path E](#path-e--a-finished-post-ready-for-copyedit)
- **Yes — it wants a technical review**, because you wrote up work that is
  not yours, or you would rather a second pair of eyes confirmed the details.
  → [Path D](#path-d--a-draft-that-needs-technical-review)

Picking wrong is not a disaster — a card moves lanes and nobody minds — but
picking right saves a round trip.

**Write in your own language.** Do not translate for us. Translating on the
way in loses the details that make a post good, and we localize on the way
out anyway.

---

## Path A — Issue template (default, start here)

Best for: most people, most of the time. Fastest path if you are already in
GitHub.

1. Go to the content board and [open a new
   issue](../../../issues/new/choose). Choose
   **Blog post from a PR**.
2. Fill in the YAML block at the top — the PR link and your name are the
   only ones that matter.
3. Fill in the five `[CORE]` sections. Ten minutes is a normal amount of
   time to spend. Leave the rest blank if you are busy.
4. Submit. Your card lands in **Drafting** automatically.
5. Within a day you get a Slack DM with a generated draft attached to the
   issue.
6. Read it. If there are `QUESTION FOR AUTHOR` blocks, answer them in a
   comment — the card comes back to you until they are cleared.
7. Comment "looks right" or push corrections. Card moves to **Editorial
   review**.
8. You get one more look at technical review before it publishes.

---

## Path B — Google Doc

Best for: you would rather write in a doc, you want a colleague to help you
fill it in, or you are drafting on a phone.

1. Open the **Blog Post Skeleton** template in Drive and make a copy.
   (File → Make a copy. Do not edit the template itself.)
2. Fill it in the same way as Path A. Keep the headings — do not delete or
   rename them.
3. Share the copy so anyone at Tensormesh with the link can comment.
4. Open a blank issue on the content board, title it `[blog] <your one-liner>`,
   and paste the doc link as the whole body.
5. The pipeline reads the doc, pulls the fields, and rewrites the issue body
   with the parsed skeleton and the right labels.
6. From here it is identical to Path A, step 5 onward. Edits continue in the
   doc — the issue is the tracking record, the doc is the working surface.

---

## Path C — Attach a markdown file

Best for: you already wrote notes somewhere, you live in your editor, or you
want this in the same PR as your code.

1. Grab the skeleton from this repo — [`docs/templates/blog-post-skeleton.md`](templates/blog-post-skeleton.md),
   or download it straight from
   [raw](../../../raw/main/docs/templates/blog-post-skeleton.md)
   — or write plain markdown using the same `##` headings.
2. Fill it in.
3. Either:
   - drag the `.md` file onto a new blank issue on the content board, or
   - commit it to `content/skeletons/<pr-number>.md` in a PR and open an
     issue linking to it.
4. Title the issue anything. You do not need to fill in the body.
5. The pipeline reads the attachment, derives the metadata from the front
   matter, and **rewrites the issue title, body, and labels to match**. You
   do not have to keep them in sync by hand.
6. From here it is identical to Path A, step 5 onward.

---

---

## Path D — a draft that needs technical review

Best for: the writing is done, the verification is not. You wrote up work
that is not yours, or you are describing a system you do not own, or you
would rather someone confirmed the details before your name is on it.

**"Draft" here means the technical content still wants checking.** If it does
not, you want [Path E](#path-e--a-finished-post-ready-for-copyedit) — most
already-written posts do.

1. Open a new issue and choose **Blog post draft — needs technical review**.
2. Link the draft, drag the file onto the issue, or open a PR that adds it under
   [`content/drafts/`](../content/README.md#drafts) and link the PR.
3. Pick the lane — `editorial` if nobody has edited it (the normal choice),
   `technical` if an editor already has. Either way it passes through
   Technical review; that is the point of this path.
4. Optionally, say where your claims came from, and — more useful — **what
   you are least sure about**. Neither is required. Anything you put there
   points the reviewer at the part that needs them instead of the whole
   piece. Any format works; the template lists several and does not care
   what you drafted in.
5. Submit. Your card skips **Idea**, **Claimed**, and **Drafting** and lands
   in the lane you picked.

---

## Path E — a finished post, ready for copyedit

Best for: the post is done *and* the technical content is already sound. This
is the normal path for a post written by the person who built the thing, and
for a post from another organization that already reviewed it.

1. Open a new issue and choose **Finished blog post — ready for copyedit**.
2. Link the post, drag the file onto the issue, or open a PR that adds it under
   [`content/drafts/`](../content/README.md#drafts) and link the PR.
3. Say **who verified the technical content** — you, because you built it;
   someone at your org; or an external review. Usually one line. We take your
   word for it; this is just the record of whose word it was.
4. Say how much editing you are comfortable with: `full` (structure and
   phrasing are ours to adjust, within house style) or `light` (copyedit
   only — grammar, typos, consistency). Either is fine and nobody will argue.
5. Submit. Your card enters **Editorial review** for the copyedit, then goes
   to **Translations**. **It does not pass through Technical review.**

Two checks still apply, because they apply to everything we publish
regardless of who verified it: every number carries the conditions it holds
under, and placement respects the LMCache/Tensormesh boundary. Both are
one-liners on the form.

If you get to "who verified the technical content" and are not sure what to
put, that is worth noticing — the post probably wants Path D. No harm in it,
and it is faster than a correction after publishing.

## If it is not about a PR

The skeleton still works — leave `pr:` blank and set `post_type` to `why-to`.
`What was wrong before` and `The interesting part` are still the two fields
that carry the piece.

## What happens to your card

```
Idea → Claimed → Drafting → Editorial review → Technical review → Translations → Published
                    ↑              ↑    ↑              ↑
                Paths A/B/C   Path D    Path E     Path D
                              (editorial)          (technical)
```

Seven columns.

- **Paths A, B, C** enter at **Drafting** — the skeleton needs turning into a
  post first.
- **Path D** enters at **Editorial review** or **Technical review**, and
  always passes through Technical review.
- **Path E** enters at **Editorial review** for the copyedit and then goes
  **straight to Translations, skipping Technical review.** That skip is the
  whole difference between D and E.
- **Idea** and **Claimed** take no intake path. They are where a post gets
  proposed and picked up before anyone has written anything.

You get a Slack DM when your card moves and when something needs you. If a
card sits waiting on you for more than two days, you get a nudge.

## Who to ask

Karsten, in `#lmcache-content`. If the pipeline produces something wrong,
say so in the issue rather than fixing it silently — the corrections are how
it gets better.
