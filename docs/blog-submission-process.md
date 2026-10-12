# How to get a blog post written

There are five ways to submit a post. Pick the one that is easiest for you.

If the post is not written yet, use path A, B, or C. You write a skeleton
(rough notes), and the pipeline and an editor turn it into a post. You review
the post before it publishes. Each path creates a card on the
[editorial board](https://github.com/orgs/LMCache/projects/6).

If the post is already written, use path D or E:

- [Path E](#path-e--a-finished-post-ready-for-copyedit): the technical content
  is already correct. You built the feature, or someone reviewed it. This is
  the common case.
- [Path D](#path-d--a-draft-that-needs-technical-review): the technical
  content needs a review. For example, you wrote about someone else's work.

If you pick the wrong path, an editor moves the card.

**Write in your own language.** Do not translate for us. Translation loses the
details that make a post good, and we localize every post before publishing.

---

## Path A — Issue template (default, start here)

Use this path if you work in GitHub. It is the fastest path.

1. [Open a new issue](../../../issues/new/choose) in this repo. Choose
   **Blog post from a PR**.
2. Fill in the YAML block at the top. Only the PR link and your name are
   required.
3. Fill in the `[CORE]` sections. Ten minutes is normal. Leave the other
   sections blank if you are busy.
4. Submit. The card goes to **Drafting** automatically.
5. Within one day, a generated draft is attached to the issue, and you get a
   Slack DM.
6. Answer each `QUESTION FOR AUTHOR` block in a comment. The card waits for
   you until you answer all of them.
7. Comment "looks right", or push corrections. The card moves to **Editorial
   review**.
8. You review the post again at **Technical review**.

---

## Path B — Google Doc

Use this path if you prefer to write in a doc, want a colleague to help, or
are working on a phone.

1. Open the **Blog Post Skeleton** template in Drive and make a copy
   (File → Make a copy). Do not edit the template.
2. Fill it in as in Path A. Do not delete or rename the headings.
3. Share the copy so that anyone at Tensormesh with the link can comment.
4. Open a blank issue in this repo. Title it `[blog] <your one-liner>`. Paste
   the doc link as the whole body.
5. The pipeline reads the doc, rewrites the issue body, and adds the labels.
6. Continue from Path A, step 5. Make later edits in the doc, not the issue.

---

## Path C — Attach a markdown file

Use this path if you already have notes, work in an editor, or want the
skeleton in the same PR as your code.

1. Get the skeleton:
   [`docs/templates/blog-post-skeleton.md`](templates/blog-post-skeleton.md)
   ([raw download](../../../raw/main/docs/templates/blog-post-skeleton.md)).
   You can also write plain markdown with the same `##` headings.
2. Fill it in.
3. Do one of these:
   - Drag the `.md` file onto a new blank issue in this repo.
   - Commit it to `content/skeletons/<pr-number>.md` in a PR, and open an issue
     that links to it.
4. Use any issue title, and leave the body empty. The pipeline rewrites the
   title, body, and labels from the file.
5. Continue from Path A, step 5.

---

## Path D — a draft that needs technical review

Use this path if the writing is done but nobody has checked the technical
content. If someone has, use Path E.

1. Open a new issue and choose **Blog post draft — needs technical review**.
2. Link the draft, drag the file onto the issue, or open a PR that adds it
   under [`content/drafts/`](../content/README.md#drafts) and link the PR.
3. Set the lane. Use `editorial` if nobody has edited the post (the normal
   choice). Use `technical` if an editor already has. Both lanes include
   Technical review.
4. Optional: say where your claims come from, and what you are least sure
   about. This tells the reviewer where to look first.
5. Submit. The card skips **Idea**, **Claimed**, and **Drafting**, and goes to
   the lane you set.

---

## Path E — a finished post, ready for copyedit

Use this path if the post is done and the technical content is already
correct.

1. Open a new issue and choose **Finished blog post — ready for copyedit**.
2. Link the post, drag the file onto the issue, or open a PR that adds it
   under [`content/drafts/`](../content/README.md#drafts) and link the PR.
3. Say who verified the technical content: you (you built it), someone at your
   organization, or an external reviewer. One line is enough.
4. Choose the editing level: `full` (we can change structure and phrasing,
   within house style) or `light` (grammar, typos, and consistency only).
5. Submit. The card goes to **Editorial review** for the copyedit, then to
   **Translations**. **It does not go through Technical review.**

Every number in the post must still state its test conditions. The copyedit
checks this.

If you do not know who verified the technical content, use Path D.

## If the post is not about a PR

Use the skeleton anyway. Leave `pr:` blank and set `post_type` to `why-to`.
`What was wrong before` and `The interesting part` are the two most important
fields.

## What happens to your card

```
Idea → Claimed → Drafting → Editorial review → Technical review → Translations → Published
                    ↑              ↑    ↑              ↑
                Paths A/B/C   Path D    Path E     Path D
                              (editorial)          (technical)
```

Path D always goes through **Technical review**. Path E skips it. No path
enters at **Idea** or **Claimed**: those columns hold proposed posts and posts
that someone has taken, before anyone writes.

You get a Slack DM when your card moves or needs you. If a card waits on you
for more than two days, you get a reminder.

## Who to ask

Ask Karsten Wade in `#lmcache-content`, or see
[MAINTAINERS.md](../MAINTAINERS.md). If the pipeline produces something wrong,
say so in the issue. Do not fix it silently: your corrections improve the
pipeline.
