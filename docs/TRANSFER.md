# Moving this repository to the LMCache organization

Written while preparing the move, so the steps are the ones that were actually
verified rather than the ones that sounded right.

The repository is **transfer-ready**: nothing in the code names an owner any
more. What follows is what a human still has to do, in order, and what will
break if a step is skipped.

## What GitHub moves for you

Confirmed against GitHub's own documentation:

- **Issues, pull requests, wiki, stars, and watchers** come along.
- **All links to the old location redirect** to the new one — including `git
  remote` URLs, so nobody's clone breaks.
- **Webhooks, secrets, and deploy keys stay associated** after the transfer.
  This one is easy to assume otherwise; `PROJECT_TOKEN` survives.
- Git history, forks, and LFS objects are preserved.

## What does not move, and will silently break

**The project board.** A GitHub Projects V2 board belongs to a *user or an
organization*, never to a repository. Transferring the repo leaves the board
exactly where it is. The cards keep pointing at the issues, and the workflow
keeps writing to the old board, because as far as it is concerned nothing
happened.

This is the one that bites, because nothing errors.

### The board cannot be transferred, but it can be copied

There is no `transferProjectV2`. The GraphQL schema has no such mutation —
checked by introspection, not assumed — and a board stays with the account that
created it, permanently.

`copyProjectV2` does exist, takes an `ownerId`, and that owner may be an
organization. A copy carries **more than is obvious**:

| Copied | Not copied |
|---|---|
| Views | **Existing items** — real issues and PRs |
| Custom fields, **including `Status` and its column options** | Collaborators |
| Configured workflows, *except* auto-add workflows | Repository and team links |
| Insights | |
| Draft issues, only if asked | |

Copying is worth doing rather than rebuilding by hand, for one specific reason:
**the router matches columns by name and raises if one is missing.** Retyping
seven column names is an invitation to land `Editorial Review` where the code
expects `Editorial review`, and find out when the first card fails to route. A
copy reproduces them exactly.

That the items do not come across costs nothing here — the hourly sweep adds
every open issue that is not already on the board, so the cards rebuild
themselves on the next run.

## Before the transfer

1. **Karsten needs membership in the LMCache org with permission to create
   repositories.** GitHub requires create-repo rights in the *target* org to
   transfer into it. Without it the transfer cannot be initiated at all — this
   is a hard blocker, not a formality.
2. Decide who ends up with **admin** on the repo afterwards. A transfer makes
   the receiving org's owners admins; confirm the humans who need it have it.

## The transfer

Initiated by the source owner, from Settings → General → Danger Zone →
Transfer, or:

```bash
gh api -X POST repos/quaid/lmcache-blogs/transfer -f new_owner=LMCache
```

## After the transfer, in order

1. **Copy the board into the org**, rather than rebuilding it. From the board's
   ⋯ menu → *Make a copy*, choosing `LMCache` as the owner — or:

   ```bash
   # The source board's node id, and the org's:
   gh api graphql -f query='{ repositoryOwner(login:"quaid"){
     ... on ProjectV2Owner { projectV2(number:5){ id } } } }'
   gh api graphql -f query='{ organization(login:"LMCache"){ id } }'

   gh api graphql -f query='
     mutation($src: ID!, $owner: ID!, $title: String!) {
       copyProjectV2(input: {projectId:$src, ownerId:$owner, title:$title}) {
         projectV2 { number url }
       }
     }' -F src=<PROJECT_ID> -F owner=<ORG_ID> \
        -F title="LMCache Blogs [Editorial Kanban]"
   ```

   Then confirm the seven columns survived, in order:

   ```
   Idea → Claimed → Drafting → Editorial review → Technical review → Translations → Published
   ```

   The names must match exactly — the router looks them up by name and raises
   rather than guessing if one is missing.

   **Link the board to `lmcache-blogs`, and only to it.** Links are not copied,
   so a copied board starts linked to nothing.

   ```bash
   # The blogs repo's node id -- check the output says lmcache-blogs
   gh api graphql -f query='{ repository(owner:"LMCache", name:"lmcache-blogs"){
     id nameWithOwner } }'

   gh api graphql -f query='
     mutation($p: ID!, $r: ID!) {
       linkProjectV2ToRepository(input: {projectId:$p, repositoryId:$r}) {
         repository { nameWithOwner }
       }
     }' -F p=<NEW_PROJECT_ID> -F r=<BLOGS_REPO_ID>
   ```

   **Do not link it to `LMCache/LMCache`.** The engine repo's Projects tab is
   for engine work; an editorial board with columns like *Translations* and
   *Published* appearing there is noise for every contributor who opens it, and
   it invites blog issues being filed against the engine repo.

   A note on what "in the repo" can and cannot mean here: **a repository cannot
   own a board.** `ProjectV2Owner` resolves to an Organization or a User and
   nothing else — `Repository` is not among them, checked by introspection. So
   the board is owned by the `LMCache` org no matter what, and lives at
   `github.com/orgs/LMCache/projects/N`. Linking is the whole of the control
   available: it is what makes the board appear on the blogs repo's Projects
   tab, and what keeps it off everyone else's.

2. **Set `BOARD_NUMBER`** (Settings → Secrets and variables → Actions →
   Variables) to the new board's number. Leave `BOARD_OWNER` unset; it defaults
   to the repository owner, which is now `LMCache`.

3. **Keep the classic `PROJECT_TOKEN`.** It survives the transfer and works
   against the org board — it is what routed `orgs/LMCache/projects/6` after
   this move. Do not expect to swap it for a fine-grained token: the org-level
   `Projects` permission is offered only to org **owners**, and a Member creating
   one with `LMCache` as resource owner will not see it.

   To get off a personal token, ask an org owner to install a **GitHub App** on
   the org with Projects permission. That is the long-term answer; until then the
   classic token is fine.

4. **Let the sweep rebuild the cards.** Copying a board does not bring its
   items, so the new board starts empty. The hourly sweep adds every open issue
   that is not already on it; no card needs moving by hand.

5. **Archive or delete the old board** once the new one is routing, so nobody
   files against a board that nothing writes to any more.

6. **Dry-run before trusting it:**

   ```bash
   gh workflow run content-board.yml --repo LMCache/lmcache-blogs -f dry_run=true
   ```

   Read the run summary. Both current issues are `pipeline`-labelled, so the
   correct outcome is that they stay **off** the board with no triage flag. If
   the dry run wants to file them under `Idea`, the routing table and the board
   disagree about something — fix that before a real run.

7. **Re-point local clones** (optional; the redirect handles it):

   ```bash
   git remote set-url origin git@github.com:LMCache/lmcache-blogs.git
   ```

## Decisions the move forces

Neither is mechanical, and neither should be made by whoever happens to run the
transfer.

**The dual sign-off convention.** `AGENTS.md` requires two `Signed-off-by`
trailers, on the reasoning that this repo sits in two contexts at once — a
personal namespace holding LMCache content produced for Tensormesh. Once the
repo is owned by LMCache that justification no longer holds: there is one
context, and the convention collapses to a single sign-off under the
LMCache/Tensormesh identity. The rule is left as-is here so nothing changes
mid-move. Revisit it deliberately afterwards.

**Where Code of Conduct and security reports go.** `CODE_OF_CONDUCT.md` and
`SECURITY.md` currently route to `karsten@tensormesh.ai`, which was right for a
personal repo. An LMCache-owned repository should route to whatever the project
uses, so that enforcement does not depend on one person's mailbox.

## What is still not built

Unchanged by the move, listed so it is not mistaken for transfer damage:

- Nothing moves a card *forward*; routing sets the entry column only.
- No stall detection, though the process doc promises a nudge at two days.
- No closed-issue policy — whether "closed" means published or abandoned is
  [an open question](../../../issues).
