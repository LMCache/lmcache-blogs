# SPDX-License-Identifier: Apache-2.0
"""Move content-board cards as the work moves.

``board_router.py`` places a new issue on the board. This module moves cards
after that, and responds when a person moves one:

``pr``
    A draft PR changed: it opened, a maintainer approved it, or it merged.
    Move its post's card. Run on ``pull_request_target`` and on
    ``pull_request_review``.
``issue``
    An issue changed. Place it if it is new, close-out a finished translation,
    restore a reopened post, and reconcile its card.
``reconcile``
    Walk the whole board. Act on every card a person moved since the last run,
    and catch up on approvals and merges the event jobs missed. Repository
    workflows cannot trigger on a card move (``projects_v2_item`` is an
    org-only webhook), so this scheduled pass is how manual moves are seen.
``setup``
    Create the two hidden text fields the reconciler keeps its state in.

The decisions themselves live in ``board_stages.py`` and are tested there. This
module only reads GitHub, asks those functions what to do, and does it.

Issue and PR writes use ``GH_TOKEN`` (the workflow's ``GITHUB_TOKEN``). Board
writes use ``PROJECT_TOKEN``. Only issues in the repository being routed are
ever touched, even if someone adds another repository's issue to the board:
upstream issues are not ours to relabel or close.
"""

# Future
from __future__ import annotations

# Standard
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import sys

# Third Party
from board_router import board_location, graphql, handle_issue, run_gh
from board_stages import (
    PUBLISHED,
    TRANSLATION_LABEL,
    CardPlan,
    CardSnapshot,
    PrState,
    Route,
    after_approval,
    approval_counts,
    describe_flags,
    on_merge,
    on_pr_opened,
    parent_should_publish,
    parse_checklists,
    parse_post_ref,
    reconcile_card,
    route_for,
    stage_label,
)

SYNCED_FIELD = "Synced status"
PRIOR_FIELD = "Prior status"
CHECKLIST_DOC = (
    Path(__file__).resolve().parents[1] / "docs" / "pipeline" / "stage-checklists.md"
)
DRAFTS_PREFIX = "content/drafts/"

STAGE_MARKER = "<!-- board-stage:{column} -->"
STAGE_MARKER_PREFIX = "<!-- board-stage:"
FLAG_MARKER = "<!-- board-flag -->"
MISSING_REF_MARKER = "<!-- board-post-ref-missing -->"
NOT_A_POST_MARKER = "<!-- board-post-ref-not-a-post -->"


@dataclass(frozen=True)
class Board:
    """Ids needed to write to the board.

    Attributes:
        project_id: The project's node id.
        status_field: The Status field's id.
        options: Column name to Status option id.
        synced_field: The hidden "Synced status" text field's id.
        prior_field: The hidden "Prior status" text field's id.
    """

    project_id: str
    status_field: str
    options: dict[str, str]
    synced_field: str
    prior_field: str


@dataclass
class Card:
    """One issue's card, as read from the board.

    Mutable on purpose: after a move, the run updates it in place so later
    decisions in the same run see the new column.

    Attributes:
        item_id: The board item's node id.
        number: The issue number.
        issue_id: The issue's node id.
        is_open: Whether the issue is open.
        labels: Label names on the issue.
        status: The current column, or None.
        status_changed_at: When the column last changed, ISO 8601, or empty.
        synced: The column the reconciler last recorded, or empty.
        prior: The column recorded on entering Published, or empty.
        parent: The parent issue's number, if this is a sub-issue.
    """

    item_id: str
    number: int
    issue_id: str
    is_open: bool
    labels: frozenset[str]
    status: str | None
    status_changed_at: str
    synced: str
    prior: str
    parent: int | None = None

    def snapshot(self) -> CardSnapshot:
        """Return the pure view of this card that the stage rules take."""
        return CardSnapshot(
            number=self.number,
            is_open=self.is_open,
            labels=self.labels,
            status=self.status,
            synced=self.synced,
            prior=self.prior,
        )


@dataclass
class Run:
    """State shared across one invocation.

    Attributes:
        repo: Repository being routed, ``owner/name``.
        dry_run: Decide and print, but change nothing.
        board: Board ids.
        cards: Cards by issue number, for this repository only.
        checklists: Column to checklist text.
        known_labels: Labels that exist in the repository.
        prs: Recent PRs, loaded on first use.
    """

    repo: str
    dry_run: bool
    board: Board
    cards: dict[int, Card]
    checklists: dict[str, str]
    known_labels: set[str] = field(default_factory=set)
    prs: list[dict] | None = None


# Module-level helpers --------------------------------------------------------


def _now() -> str:
    """Return the current UTC time in GitHub's ISO 8601 form."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _api(path: str) -> object:
    """GET a REST path with the issue token and return the parsed JSON."""
    return json.loads(run_gh(["api", path]) or "null")


def load_board(repo: str) -> Board:
    """Read the board's field ids.

    Args:
        repo: Repository being routed, ``owner/name``.

    Returns:
        The board ids.

    Raises:
        RuntimeError: If the Status field or either hidden field is missing.
            The hidden fields are created by ``setup``.
    """
    owner, number = board_location(repo)
    data = graphql(
        """
        query($owner: String!, $number: Int!) {
          repositoryOwner(login: $owner) {
            ... on ProjectV2Owner {
              projectV2(number: $number) {
                id
                fields(first: 50) {
                  nodes {
                    ... on ProjectV2SingleSelectField { id name options { id name } }
                    ... on ProjectV2Field { id name }
                  }
                }
              }
            }
          }
        }
        """,
        owner=owner,
        number=str(number),
    )
    project = (data.get("repositoryOwner") or {}).get("projectV2")
    if not project:
        raise RuntimeError(f"cannot see project {number} owned by {owner!r}")
    by_name = {f["name"]: f for f in project["fields"]["nodes"] if f.get("name")}
    status = by_name.get("Status")
    if not status or "options" not in status:
        raise RuntimeError("the board has no Status field")
    missing = [n for n in (SYNCED_FIELD, PRIOR_FIELD) if n not in by_name]
    if missing:
        raise RuntimeError(
            f"the board is missing {', '.join(missing)}; run "
            "`python tools/board_automation.py setup --repo <owner/name>` once"
        )
    return Board(
        project_id=project["id"],
        status_field=status["id"],
        options={o["name"]: o["id"] for o in status["options"]},
        synced_field=by_name[SYNCED_FIELD]["id"],
        prior_field=by_name[PRIOR_FIELD]["id"],
    )


def load_cards(repo: str) -> dict[int, Card]:
    """Read every card on the board that belongs to an issue in ``repo``.

    Paginates, so the board can grow past 100 items. Pull requests, draft
    items, and other repositories' issues are skipped.

    Args:
        repo: Repository being routed, ``owner/name``.

    Returns:
        Cards by issue number.
    """
    owner, number = board_location(repo)
    cards: dict[int, Card] = {}
    cursor = "null"
    while True:
        data = graphql(
            f"""
            query($owner: String!, $number: Int!, $cursor: String) {{
              repositoryOwner(login: $owner) {{
                ... on ProjectV2Owner {{
                  projectV2(number: $number) {{
                    items(first: 100, after: $cursor) {{
                      pageInfo {{ hasNextPage endCursor }}
                      nodes {{
                        id
                        content {{
                          ... on Issue {{
                            id number state
                            repository {{ nameWithOwner }}
                            labels(first: 30) {{ nodes {{ name }} }}
                            parent {{ number }}
                          }}
                        }}
                        status: fieldValueByName(name: "Status") {{
                          ... on ProjectV2ItemFieldSingleSelectValue {{
                            name updatedAt
                          }}
                        }}
                        synced: fieldValueByName(name: "{SYNCED_FIELD}") {{
                          ... on ProjectV2ItemFieldTextValue {{ text }}
                        }}
                        prior: fieldValueByName(name: "{PRIOR_FIELD}") {{
                          ... on ProjectV2ItemFieldTextValue {{ text }}
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """,
            owner=owner,
            number=str(number),
            cursor=cursor,
        )
        page = data["repositoryOwner"]["projectV2"]["items"]
        for node in page["nodes"]:
            issue = node.get("content") or {}
            if "number" not in issue:
                continue
            if issue["repository"]["nameWithOwner"].lower() != repo.lower():
                continue
            status = node.get("status") or {}
            cards[issue["number"]] = Card(
                item_id=node["id"],
                number=issue["number"],
                issue_id=issue["id"],
                is_open=issue["state"] == "OPEN",
                labels=frozenset(x["name"] for x in issue["labels"]["nodes"]),
                status=status.get("name"),
                status_changed_at=status.get("updatedAt") or "",
                synced=(node.get("synced") or {}).get("text") or "",
                prior=(node.get("prior") or {}).get("text") or "",
                parent=(issue.get("parent") or {}).get("number"),
            )
        if not page["pageInfo"]["hasNextPage"]:
            return cards
        cursor = page["pageInfo"]["endCursor"]


def start(repo: str, dry_run: bool) -> Run:
    """Load everything a run needs.

    Args:
        repo: Repository being routed, ``owner/name``.
        dry_run: Decide and print, but change nothing.

    Returns:
        The run.
    """
    labels = json.loads(
        run_gh(["label", "list", "--repo", repo, "--limit", "500", "--json", "name"])
        or "[]"
    )
    return Run(
        repo=repo,
        dry_run=dry_run,
        board=load_board(repo),
        cards=load_cards(repo),
        checklists=parse_checklists(CHECKLIST_DOC.read_text(encoding="utf-8")),
        known_labels={x["name"] for x in labels},
    )


def load_prs(run: Run) -> list[dict]:
    """Return the 100 most recently updated PRs, cached for the run.

    Args:
        run: The run.

    Returns:
        PRs as returned by the REST API.
    """
    if run.prs is None:
        found = _api(
            f"repos/{run.repo}/pulls?state=all&per_page=100&sort=updated&direction=desc"
        )
        run.prs = list(found) if isinstance(found, list) else []
    return run.prs


def pr_state_for(run: Run, post: int) -> PrState:
    """Return the state of the draft PR that names ``post``.

    An open PR wins over a merged one: a post with a follow-up PR still open is
    not finished.

    Args:
        run: The run.
        post: The post's issue number.

    Returns:
        The state.
    """
    state = PrState.NONE
    for pr in load_prs(run):
        ref = parse_post_ref(pr.get("body") or "", run.repo)
        if ref is None or ref.number != post:
            continue
        if pr["state"] == "open":
            return PrState.OPEN
        if pr.get("merged_at"):
            state = PrState.MERGED
    return state


def translation_counts(run: Run, post: int) -> tuple[int, int]:
    """Count a post's translation sub-issues.

    Args:
        run: The run.
        post: The post's issue number.

    Returns:
        (open, total) translation sub-issues.
    """
    subs = _api(f"repos/{run.repo}/issues/{post}/sub_issues?per_page=100")
    rows = subs if isinstance(subs, list) else []
    l10n = [s for s in rows if any(x["name"] == TRANSLATION_LABEL for x in s["labels"])]
    return sum(1 for s in l10n if s["state"] == "open"), len(l10n)


# Writes ----------------------------------------------------------------------


def _set_text(run: Run, card: Card, field_id: str, value: str) -> None:
    """Set or clear one of the hidden text fields on a card."""
    if value:
        graphql(
            """
            mutation($p: ID!, $i: ID!, $f: ID!, $v: String!) {
              updateProjectV2ItemFieldValue(input: {
                projectId: $p, itemId: $i, fieldId: $f, value: {text: $v}
              }) { projectV2Item { id } }
            }
            """,
            p=run.board.project_id,
            i=card.item_id,
            f=field_id,
            v=value,
        )
    else:
        graphql(
            """
            mutation($p: ID!, $i: ID!, $f: ID!) {
              clearProjectV2ItemFieldValue(input: {
                projectId: $p, itemId: $i, fieldId: $f
              }) { projectV2Item { id } }
            }
            """,
            p=run.board.project_id,
            i=card.item_id,
            f=field_id,
        )


def _set_status(run: Run, card: Card, column: str) -> None:
    """Move a card to ``column``."""
    option = run.board.options.get(column)
    if option is None:
        raise RuntimeError(
            f"column {column!r} is not on the board; "
            f"present: {sorted(run.board.options)}"
        )
    graphql(
        """
        mutation($p: ID!, $i: ID!, $f: ID!, $o: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $p, itemId: $i, fieldId: $f,
            value: {singleSelectOptionId: $o}
          }) { projectV2Item { id } }
        }
        """,
        p=run.board.project_id,
        i=card.item_id,
        f=run.board.status_field,
        o=option,
    )


def _ensure_label(run: Run, name: str) -> None:
    """Create a stage label if the repository does not have it yet."""
    if name in run.known_labels:
        return
    run_gh(
        [
            "label",
            "create",
            name,
            "--repo",
            run.repo,
            "--color",
            "bfd4f2",
            "--description",
            "Mirrors the card's column on the content board. Set by automation.",
        ]
    )
    run.known_labels.add(name)


def _last_stage_comment(run: Run, number: int) -> str:
    """Return the column named by the issue's most recent stage comment."""
    comments = _api(f"repos/{run.repo}/issues/{number}/comments?per_page=100")
    last = ""
    for comment in comments if isinstance(comments, list) else []:
        body = comment.get("body") or ""
        start_at = body.find(STAGE_MARKER_PREFIX)
        if start_at >= 0:
            end_at = body.find(" -->", start_at)
            last = body[start_at + len(STAGE_MARKER_PREFIX) : end_at]
    return last


def _comment(run: Run, number: int, body: str) -> None:
    """Post a comment on an issue or PR."""
    run_gh(["issue", "comment", str(number), "--repo", run.repo, "--body", body])


def apply_plan(run: Run, card: Card, plan: CardPlan, why: str) -> None:
    """Carry out a plan for one card, or print it on a dry run.

    Args:
        run: The run.
        card: The card. Updated in place to reflect the plan.
        plan: What to do.
        why: Short reason, printed with the action.
    """
    if plan.is_empty():
        return
    parts = []
    if plan.move_to:
        parts.append(f"move {card.status} -> {plan.move_to}")
    if plan.labels_add or plan.labels_remove:
        parts.append(f"labels +{list(plan.labels_add)} -{list(plan.labels_remove)}")
    if plan.checklist:
        parts.append(f"checklist {plan.checklist}")
    if plan.flags:
        parts.append(f"{len(plan.flags)} flag(s)")
    if plan.close:
        parts.append("close")
    if plan.set_synced is not None:
        parts.append(f"synced={plan.set_synced or '(clear)'}")
    print(f"#{card.number}: {'; '.join(parts)}  ({why})")
    if run.dry_run:
        _update_in_memory(card, plan)
        return

    if plan.move_to:
        _set_status(run, card, plan.move_to)
    for name in plan.labels_add:
        _ensure_label(run, name)
    if plan.labels_add or plan.labels_remove:
        args = ["issue", "edit", str(card.number), "--repo", run.repo]
        for name in plan.labels_add:
            args += ["--add-label", name]
        for name in plan.labels_remove:
            args += ["--remove-label", name]
        run_gh(args)
    if plan.checklist:
        text = run.checklists.get(plan.checklist, "")
        if text and _last_stage_comment(run, card.number) != plan.checklist:
            _comment(
                run,
                card.number,
                f"{STAGE_MARKER.format(column=plan.checklist)}\n"
                f"This post is now in **{plan.checklist}**.\n\n{text}",
            )
    if plan.flags:
        _comment(run, card.number, FLAG_MARKER + "\n" + "\n\n".join(plan.flags))
    if plan.set_prior is not None:
        _set_text(run, card, run.board.prior_field, plan.set_prior)
    if plan.set_synced is not None:
        _set_text(run, card, run.board.synced_field, plan.set_synced)
    if plan.close:
        run_gh(
            [
                "issue",
                "close",
                str(card.number),
                "--repo",
                run.repo,
                "--reason",
                "completed",
            ]
        )
    _update_in_memory(card, plan)


def _update_in_memory(card: Card, plan: CardPlan) -> None:
    """Reflect an applied plan on the in-memory card."""
    if plan.move_to:
        card.status = plan.move_to
        card.status_changed_at = _now()
    if plan.set_synced is not None:
        card.synced = plan.set_synced
    if plan.set_prior is not None:
        card.prior = plan.set_prior
    labels = (set(card.labels) - set(plan.labels_remove)) | set(plan.labels_add)
    card.labels = frozenset(labels)
    if plan.close:
        card.is_open = False


def move_card(
    run: Run, card: Card, column: str, why: str, flags: tuple[str, ...] = ()
) -> None:
    """Move a card as automation, with everything a move implies.

    Sets the column and the recorded column together, so the reconciler does
    not mistake this move for a human one. Mirrors the stage label, posts the
    checklist for the new column, and on Published closes the issue and records
    where it came from. A translation reaching Published re-checks its post.

    Args:
        run: The run.
        card: The card to move.
        column: Target column.
        why: Short reason, printed with the action.
        flags: Sentences to post if the move skipped something.
    """
    if card.status == column:
        return
    from_col = card.status or ""
    labels_add = () if stage_label(column) in card.labels else (stage_label(column),)
    labels_remove = tuple(
        sorted(
            x
            for x in card.labels
            if x.startswith("stage:") and x != stage_label(column)
        )
    )
    publishing = column == PUBLISHED
    apply_plan(
        run,
        card,
        CardPlan(
            set_synced=column,
            set_prior=from_col if publishing else None,
            move_to=column,
            labels_add=labels_add,
            labels_remove=labels_remove,
            checklist=column,
            flags=flags,
            close=publishing and card.is_open,
            check_parent=publishing and route_for(card.labels) is Route.TRANSLATION,
        ),
        why,
    )
    if publishing and card.parent and route_for(card.labels) is Route.TRANSLATION:
        check_parent(run, card.parent)


def check_parent(run: Run, post: int) -> None:
    """Publish a post whose last translation just finished, if it is ready.

    Args:
        run: The run.
        post: The post's issue number.
    """
    card = run.cards.get(post)
    if card is None:
        return
    open_count, total = translation_counts(run, post)
    if parent_should_publish(card.status, open_count, total, pr_state_for(run, post)):
        move_card(run, card, PUBLISHED, f"all {total} translation(s) closed")


# PR handling -----------------------------------------------------------------


def advance_from_pr(run: Run, pr: dict) -> None:
    """Apply what one draft PR implies for its post's card.

    Opening starts review, a maintainer's approval after the card's last move
    advances one stage, and a merge after the card's last move publishes it
    (or parks it in Translations while a translation is open). At most one
    approval counts per call, because each stage needs its own sign-off.

    Args:
        run: The run.
        pr: The PR, as returned by the REST API.
    """
    ref = parse_post_ref(pr.get("body") or "", run.repo)
    if ref is None:
        return
    card = run.cards.get(ref.number)
    if card is None:
        return
    label = f"PR #{pr['number']}"

    if pr.get("merged_at"):
        if card.status_changed_at and pr["merged_at"] <= card.status_changed_at:
            return
        open_count, _ = translation_counts(run, card.number)
        target = on_merge(card.status, open_translations=open_count)
        if target:
            flags = describe_flags(route_for(card.labels), card.status or "", target)
            move_card(run, card, target, f"{label} merged", flags)
        return

    if pr["state"] != "open":
        return
    target = on_pr_opened(card.status)
    if target:
        move_card(run, card, target, f"{label} opened")
        return

    route = route_for(card.labels)
    reviews = _api(f"repos/{run.repo}/pulls/{pr['number']}/reviews?per_page=100")
    for review in sorted(
        reviews if isinstance(reviews, list) else [],
        key=lambda r: r.get("submitted_at") or "",
    ):
        if not approval_counts(
            state=review.get("state") or "",
            association=review.get("author_association") or "",
            reviewer=(review.get("user") or {}).get("login") or "",
            pr_author=(pr.get("user") or {}).get("login") or "",
            submitted_at=review.get("submitted_at") or "",
            status_changed_at=card.status_changed_at,
        ):
            continue
        target = after_approval(route, card.status)
        if target:
            who = (review.get("user") or {}).get("login")
            move_card(run, card, target, f"{label} approved by {who}")
        return


def handle_pr(repo: str, number: int, dry_run: bool) -> None:
    """Handle one PR event.

    A PR that adds a draft but names no post gets one comment asking for a
    ``Post: #N`` line, and one that names an issue that is not a post gets one
    comment saying so. Neither is silently ignored.

    Args:
        repo: Repository, ``owner/name``.
        number: PR number.
        dry_run: Decide and print, but change nothing.
    """
    pr = _api(f"repos/{repo}/pulls/{number}")
    if not isinstance(pr, dict):
        return
    ref = parse_post_ref(pr.get("body") or "", repo)
    files = _api(f"repos/{repo}/pulls/{number}/files?per_page=100")
    adds_draft = any(
        (f.get("filename") or "").startswith(DRAFTS_PREFIX)
        for f in (files if isinstance(files, list) else [])
    )

    if ref is None:
        if adds_draft and pr["state"] == "open":
            print(f"PR #{number}: draft PR names no post")
            if not dry_run and not _has_marker(repo, number, MISSING_REF_MARKER):
                run_gh(
                    [
                        "issue",
                        "comment",
                        str(number),
                        "--repo",
                        repo,
                        "--body",
                        f"{MISSING_REF_MARKER}\nThis PR adds a draft under "
                        "`content/drafts/`, but it does not say which post it "
                        "belongs to, so the content board cannot follow it. Add "
                        "a line `Post: #<issue>` to the description, using the "
                        "post's issue number.",
                    ]
                )
        return

    post = _api(f"repos/{repo}/issues/{ref.number}")
    is_post = (
        isinstance(post, dict)
        and "pull_request" not in post
        and any(x["name"] == "blog" for x in post.get("labels", []))
    )
    if not is_post:
        print(f"PR #{number}: #{ref.number} is not a blog post issue")
        if not dry_run and not _has_marker(repo, number, NOT_A_POST_MARKER):
            run_gh(
                [
                    "issue",
                    "comment",
                    str(number),
                    "--repo",
                    repo,
                    "--body",
                    f"{NOT_A_POST_MARKER}\nThis PR names #{ref.number} as its "
                    "post, but that is not a blog post issue, so the content "
                    "board cannot follow it. Point `Post:` at the post's issue.",
                ]
            )
        return

    run = start(repo, dry_run)
    if ref.number not in run.cards:
        handle_issue(repo, ref.number, dry_run)
        run.cards = load_cards(repo)
    advance_from_pr(run, pr)


def _has_marker(repo: str, number: int, marker: str) -> bool:
    """Return whether any comment on an issue or PR carries ``marker``."""
    comments = _api(f"repos/{repo}/issues/{number}/comments?per_page=100")
    return any(
        marker in (c.get("body") or "")
        for c in (comments if isinstance(comments, list) else [])
    )


# Issue events and the reconciler ---------------------------------------------


def handle_issue_event(repo: str, number: int, action: str, dry_run: bool) -> None:
    """Handle one issue event.

    Places a new issue, then reconciles its card. A translation that is closed
    outside the board is moved to Published, which in turn checks whether its
    post is ready.

    Args:
        repo: Repository, ``owner/name``.
        number: Issue number.
        action: The event's action, e.g. ``closed``.
        dry_run: Decide and print, but change nothing.
    """
    handle_issue(repo, number, dry_run)
    run = start(repo, dry_run)
    card = run.cards.get(number)
    if card is None:
        return
    if (
        action == "closed"
        and route_for(card.labels) is Route.TRANSLATION
        and card.status != PUBLISHED
    ):
        move_card(run, card, PUBLISHED, "translation closed")
        return
    plan = reconcile_card(card.snapshot())
    apply_plan(run, card, plan, f"issue {action}")
    if plan.check_parent and card.parent:
        check_parent(run, card.parent)


def reconcile(repo: str, dry_run: bool) -> None:
    """Walk the board and act on everything that changed since the last run.

    First, every card a person moved: mirror its label, post its checklist,
    flag an odd move, close it on Published, restore it if reopened. Then the
    draft PRs, to catch approvals and merges whose event job did not run, such
    as reviews on a PR from a fork, which get no secrets.

    Args:
        repo: Repository, ``owner/name``.
        dry_run: Decide and print, but change nothing.
    """
    run = start(repo, dry_run)
    print(f"cards: {len(run.cards)}")
    for card in sorted(run.cards.values(), key=lambda c: c.number):
        plan = reconcile_card(card.snapshot())
        moved = bool(card.synced) and card.status != card.synced
        apply_plan(run, card, plan, "moved by hand" if moved else "recorded")
        if plan.check_parent and card.parent:
            check_parent(run, card.parent)
    for pr in load_prs(run):
        advance_from_pr(run, pr)


def setup(repo: str, dry_run: bool) -> None:
    """Create the hidden text fields the reconciler keeps its state in.

    Safe to run more than once: existing fields are left alone. The fields are
    not added to any view, so they do not clutter the board.

    Args:
        repo: Repository, ``owner/name``.
        dry_run: Decide and print, but change nothing.
    """
    try:
        load_board(repo)
        print("both hidden fields already exist")
        return
    except RuntimeError as err:
        if "missing" not in str(err):
            raise
    owner, number = board_location(repo)
    data = graphql(
        """
        query($owner: String!, $number: Int!) {
          repositoryOwner(login: $owner) {
            ... on ProjectV2Owner {
              projectV2(number: $number) {
                id fields(first: 50) { nodes { ... on ProjectV2Field { name } } }
              }
            }
          }
        }
        """,
        owner=owner,
        number=str(number),
    )
    project = data["repositoryOwner"]["projectV2"]
    have = {f.get("name") for f in project["fields"]["nodes"]}
    for name in (SYNCED_FIELD, PRIOR_FIELD):
        if name in have:
            continue
        print(f"create field {name!r}")
        if dry_run:
            continue
        graphql(
            """
            mutation($p: ID!, $n: String!) {
              createProjectV2Field(input: {projectId: $p, dataType: TEXT, name: $n}) {
                projectV2Field { ... on ProjectV2Field { id } }
              }
            }
            """,
            p=project["id"],
            n=name,
        )


def main(argv: list[str]) -> int:
    """Parse arguments and dispatch.

    Args:
        argv: Command-line arguments, without the program name.

    Returns:
        Process exit status.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["pr", "issue", "reconcile", "setup"])
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--number", type=int, help="PR or issue number")
    parser.add_argument("--action", default="", help="the issue event's action")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.mode in ("pr", "issue") and args.number is None:
        parser.error(f"{args.mode} mode needs --number")
    if args.mode == "pr":
        handle_pr(args.repo, args.number, args.dry_run)
    elif args.mode == "issue":
        handle_issue_event(args.repo, args.number, args.action, args.dry_run)
    elif args.mode == "reconcile":
        reconcile(args.repo, args.dry_run)
    else:
        setup(args.repo, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
