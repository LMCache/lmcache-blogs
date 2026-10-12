# Moving this repository to the LMCache organization

**Status:** The transfer is done. The repository is `LMCache/lmcache-blogs`,
and the board is `github.com/orgs/LMCache/projects/6`.

This document records the procedure used for the move. Use it again for any
similar move. No code in the repository names an owner. The steps below are
the manual work, in order, and what breaks if you skip one.

## What GitHub moves for you

According to GitHub's documentation:

- Issues, pull requests, wiki, stars, and watchers move with the repository.
- All links to the old location redirect to the new one, including `git
  remote` URLs, so existing clones keep working.
- Webhooks, secrets, and deploy keys stay associated after the transfer.
  `PROJECT_TOKEN` survives.
- Git history, forks, and LFS objects are preserved.

## What does not move

The project board does not move. A GitHub Projects V2 board belongs to a user
or an organization, never to a repository. After a transfer, the board stays
where it was, and the workflow keeps writing to it. Nothing reports an error.

### Copy the board; you cannot transfer it

The GraphQL schema has no `transferProjectV2` mutation. A board stays with the
account that created it.

`copyProjectV2` exists and takes an `ownerId`, which can be an organization. A
copy includes:

| Copied | Not copied |
|---|---|
| Views | **Existing items** — real issues and PRs |
| Custom fields, **including `Status` and its column options** | Collaborators |
| Configured workflows, *except* auto-add workflows | Repository and team links |
| Insights | |
| Draft issues, only if asked | |

Copy the board instead of rebuilding it by hand. The router matches columns by
name and raises an error if one is missing. A retyped `Editorial Review` would
not match the expected `Editorial review`. A copy reproduces the names exactly.

The copy has no items, but the hourly sweep adds every open issue that is not
on the board, so the cards return on the next run.

## Before the transfer

1. Karsten needs membership in the LMCache org with permission to create
   repositories. GitHub requires create-repo rights in the target org. Without
   them, the transfer cannot start.
2. Decide who has **admin** on the repo afterward. A transfer makes the
   receiving org's owners admins. Confirm that everyone who needs admin has it.

## The transfer

The source owner starts it from Settings → General → Danger Zone → Transfer,
or with:

```bash
gh api -X POST repos/quaid/lmcache-blogs/transfer -f new_owner=LMCache
```

## After the transfer, in order

1. Copy the board into the org. From the board's ⋯ menu, choose *Make a copy*
   with `LMCache` as the owner, or run:

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

   Confirm that the seven columns exist, in this order, with these exact
   names:

   ```
   Idea → Claimed → Drafting → Editorial review → Technical review → Translations → Published
   ```

   Link the board to `lmcache-blogs` and to no other repository. Links are not
   copied, so a copied board starts with no links.

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

   Do not link it to `LMCache/LMCache`. That repo's Projects tab is for engine
   work. An editorial board there adds noise for engine contributors and
   invites people to file blog issues against the engine repo.

   A repository cannot own a board. `ProjectV2Owner` resolves only to an
   Organization or a User. The `LMCache` org owns the board, at
   `github.com/orgs/LMCache/projects/N`. Linking is the only control: it shows
   the board on the blogs repo's Projects tab and keeps it off other repos'
   tabs.

2. Set `BOARD_NUMBER` (Settings → Secrets and variables → Actions → Variables)
   to the new board's number. Leave `BOARD_OWNER` unset. It defaults to the
   repository owner, which is now `LMCache`.

3. Keep the classic `PROJECT_TOKEN`. It survives the transfer and works with
   the org board; it routed `orgs/LMCache/projects/6` after this move. A
   fine-grained token is not available to org Members: GitHub offers the
   org-level `Projects` permission only to org owners.

   To stop using a personal token, ask an org owner to install a GitHub App on
   the org with Projects permission. Until then, the classic token works.

4. Let the sweep rebuild the cards. The copied board starts empty. The hourly
   sweep adds every open issue that is not on it. Do not move cards by hand.

5. Archive or delete the old board after the new one routes cards, so that
   nobody files against a board that nothing updates.

6. Do a dry run before a real run:

   ```bash
   gh workflow run content-board.yml --repo LMCache/lmcache-blogs -f dry_run=true
   ```

   Read the run summary. At the time of the move, both open issues had the
   `pipeline` label, so the correct result was that both stay off the board
   with no triage flag. If the dry run puts them in `Idea`, the routing table
   and the board disagree. Fix that before a real run.

7. Optional: update local clones. The redirect already handles this.

   ```bash
   git remote set-url origin git@github.com:LMCache/lmcache-blogs.git
   ```

## Decisions the move forces

Make both decisions deliberately. They are not part of running the transfer.

**The dual sign-off convention.** `AGENTS.md` requires two `Signed-off-by`
trailers, because the repo sat in two contexts: a personal namespace that held
LMCache content produced for Tensormesh. With LMCache as the owner, that
reason no longer holds. There is one context, and the convention could become
a single sign-off under the LMCache/Tensormesh identity. The rule is unchanged
for now, so nothing changed mid-move. Revisit it after the move.

**Where Code of Conduct and security reports go.** `CODE_OF_CONDUCT.md` and
`SECURITY.md` send reports to `karsten@tensormesh.ai`, which suited a personal
repo. An LMCache-owned repository should send them to the project's own
contact, so enforcement does not depend on one person's mailbox.

## What is still not built

The move did not change these, and they are not transfer damage:

- Nothing moves a card forward. Routing sets the entry column only.
- No stall detection, though the process doc promises a nudge at two days.
- No closed-issue policy. Whether "closed" means published or abandoned is
  [an open question](../../../issues).
