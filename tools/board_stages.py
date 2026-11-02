# SPDX-License-Identifier: Apache-2.0
"""Stage rules for the content board.

The pure half of board automation. It decides where a card goes when a draft
PR opens, when a maintainer approves it, and when it merges, and what the
reconciler should do about a card a human moved. Nothing here calls GitHub;
``board_router.py`` reads the board, asks these functions what to do, and does
it. That split is what lets every transition be tested.

The column order below is the board's order. Moving a column on the board
without changing it here changes what counts as "backwards" and "skipped", so
keep the two in step. ``docs/pipeline/board-automation.md`` describes the
rules in prose.
"""

# Future
from __future__ import annotations

# Standard
from dataclasses import dataclass
from enum import Enum
import re

IDEA = "Idea"
CLAIMED = "Claimed"
DRAFTING = "Drafting"
EDITORIAL = "Editorial review"
TECHNICAL = "Technical review"
COPYEDIT = "Copyedit"
TRANSLATIONS = "Translations"
PUBLISHED = "Published"

COLUMNS = (
    IDEA,
    CLAIMED,
    DRAFTING,
    EDITORIAL,
    TECHNICAL,
    COPYEDIT,
    TRANSLATIONS,
    PUBLISHED,
)

# Review associations that may approve a stage. GitHub reports these on every
# review; anyone outside them is a drive-by reviewer, welcome but not a gate.
MAINTAINER_ASSOCIATIONS = frozenset({"OWNER", "MEMBER", "COLLABORATOR"})

TRANSLATION_LABEL = "l10n"
STAGE_LABEL_PREFIX = "stage:"


class Route(Enum):
    """Which review stages a card must pass through."""

    FULL = "full"
    VERIFIED = "verified"
    TRANSLATION = "translation"


class PrState(Enum):
    """State of the draft PR that belongs to a post."""

    NONE = "none"
    OPEN = "open"
    MERGED = "merged"


_GATES = {
    Route.FULL: (EDITORIAL, TECHNICAL, COPYEDIT),
    Route.VERIFIED: (EDITORIAL, COPYEDIT),
    Route.TRANSLATION: (),
}

_REVIEW_COLUMNS = (EDITORIAL, TECHNICAL, COPYEDIT)


def _index(column: str | None) -> int:
    """Return a column's position on the board, or -1 if it is unknown."""
    if column in COLUMNS:
        return COLUMNS.index(column)
    return -1


def route_for(labels: frozenset[str]) -> Route:
    """Decide which route a card takes from its labels.

    A translation sub-issue has no review gates of its own. A post labelled
    ``tech-verified`` skips Technical review. Everything else, including a
    hand-filed post with only the ``blog`` label and a post whose intake labels
    conflict, takes the full route: when the path is unclear, ask for more
    review rather than less.

    Args:
        labels: Label names on the issue.

    Returns:
        The route.
    """
    if TRANSLATION_LABEL in labels:
        return Route.TRANSLATION
    if "tech-verified" in labels and "needs-tech-review" not in labels:
        if "skeleton" not in labels:
            return Route.VERIFIED
    return Route.FULL


def required_gates(route: Route) -> tuple[str, ...]:
    """Return the review columns a card on ``route`` must pass, in order.

    Args:
        route: The card's route.

    Returns:
        The review columns.
    """
    return _GATES[route]


def stage_label(column: str) -> str:
    """Return the issue label that mirrors a column, e.g. ``stage:copyedit``.

    Args:
        column: A board column name.

    Returns:
        The label name.
    """
    return STAGE_LABEL_PREFIX + column.lower().replace(" ", "-")


def after_approval(route: Route, column: str | None) -> str | None:
    """Return where a maintainer's approval moves a card, if anywhere.

    An approval completes the review stage the card is in, so the card goes to
    the next review stage its route requires, or to Translations after the
    last one. A card outside the review columns is not moved: an approval on a
    PR whose card sits in Drafting is not a stage sign-off.

    Args:
        route: The card's route.
        column: The card's current column.

    Returns:
        The target column, or None.
    """
    if column not in _REVIEW_COLUMNS:
        return None
    here = _index(column)
    for gate in required_gates(route):
        if _index(gate) > here:
            return gate
    return TRANSLATIONS


def approval_counts(
    *,
    state: str,
    association: str,
    reviewer: str,
    pr_author: str,
    submitted_at: str,
    status_changed_at: str,
) -> bool:
    """Decide whether one review should advance the card.

    Only an approval from a maintainer who is not the PR's author counts, and
    only if it was submitted after the card last changed column. That last rule
    makes the reconciler safe to run repeatedly: once an approval has moved the
    card, the card's change time is later than the approval, so it never counts
    twice. Timestamps are GitHub's ISO 8601 UTC strings, which sort correctly as
    text.

    Args:
        state: The review state, e.g. ``APPROVED``.
        association: The reviewer's author association.
        reviewer: The reviewer's login.
        pr_author: The PR author's login.
        submitted_at: When the review was submitted.
        status_changed_at: When the card's column last changed, or empty if
            unknown.

    Returns:
        True if the review advances the card.
    """
    if state != "APPROVED":
        return False
    if association not in MAINTAINER_ASSOCIATIONS:
        return False
    if reviewer == pr_author:
        return False
    return not status_changed_at or submitted_at > status_changed_at


def on_pr_opened(column: str | None) -> str | None:
    """Return where opening a draft PR moves the post's card, if anywhere.

    The draft has arrived, so review starts. A card already in review or later
    is left alone: opening a PR never moves a card backwards.

    Args:
        column: The card's current column, or None if it has none.

    Returns:
        The target column, or None.
    """
    if _index(column) < _index(EDITORIAL):
        return EDITORIAL
    return None


def on_merge(column: str | None, *, open_translations: int) -> str | None:
    """Return where merging the draft PR moves the post's card, if anywhere.

    The draft PR stays open until the post is published, so a merge means the
    English post is out. If any translation is still open, the card waits in
    Translations until the last one closes.

    Args:
        column: The card's current column.
        open_translations: How many translation sub-issues are still open.

    Returns:
        The target column, or None.
    """
    target = TRANSLATIONS if open_translations else PUBLISHED
    if _index(column) >= _index(target):
        return None
    return target


def parent_should_publish(
    column: str | None, open_translations: int, total_translations: int, pr: PrState
) -> bool:
    """Decide whether a post moves to Published because translation finished.

    Only a post waiting in Translations, with at least one translation and none
    still open, and whose draft PR is not still open. A post with no
    translations at all is published by a human, not by this rule.

    Args:
        column: The post's current column.
        open_translations: Translation sub-issues still open.
        total_translations: All translation sub-issues.
        pr: The state of the post's draft PR.

    Returns:
        True if the post should move to Published.
    """
    return (
        column == TRANSLATIONS
        and total_translations > 0
        and open_translations == 0
        and pr is not PrState.OPEN
    )


def skipped_gates(route: Route, from_col: str, to_col: str) -> tuple[str, ...]:
    """Return the required review columns a move jumped over.

    Only a forward move can skip anything. The column being left is not
    skipped: leaving Technical review for Copyedit finishes it.

    Args:
        route: The card's route.
        from_col: The column the card left.
        to_col: The column the card entered.

    Returns:
        The skipped review columns, in board order.
    """
    lo, hi = _index(from_col), _index(to_col)
    if lo < 0 or hi < 0 or hi <= lo:
        return ()
    return tuple(g for g in required_gates(route) if lo < _index(g) < hi)


@dataclass(frozen=True)
class PostRef:
    """The post issue a PR belongs to.

    Attributes:
        number: The post's issue number.
        source: ``post`` for a ``Post:`` line, ``refs`` for a lone ``Refs``.
    """

    number: int
    source: str


_POST_LINE = re.compile(r"^\s*post:\s*(\S+)", re.IGNORECASE | re.MULTILINE)
_REFS = re.compile(r"\brefs\s+#(\d+)\b", re.IGNORECASE)


def parse_post_ref(body: str, repo: str) -> PostRef | None:
    """Find which post a PR belongs to from its body.

    A ``Post: #N`` line, or ``Post:`` followed by this repository's issue URL,
    is the canonical form. Before it existed, authors were told to write
    ``Refs #N``, so a body with exactly one ``Refs`` also counts. Closing
    keywords such as ``Fixes #N`` do not: they would close the post on merge,
    which is the router's job, not the PR's.

    Args:
        body: The PR body. May be empty.
        repo: This repository, ``owner/name``.

    Returns:
        The reference, or None if there is none or it is ambiguous.
    """
    match = _POST_LINE.search(body or "")
    if match:
        target = match.group(1)
        number = re.fullmatch(r"#(\d+)", target)
        if number:
            return PostRef(int(number.group(1)), "post")
        url = re.fullmatch(
            rf"https://github\.com/{re.escape(repo)}/issues/(\d+)/?", target
        )
        if url:
            return PostRef(int(url.group(1)), "post")
        return None
    refs = {int(n) for n in _REFS.findall(body or "")}
    if len(refs) == 1:
        return PostRef(refs.pop(), "refs")
    return None


def parse_checklists(markdown: str) -> dict[str, str]:
    """Read per-column checklists from the checklist doc.

    Each ``## <Column>`` heading starts a checklist that runs to the next
    ``##`` heading. Text before the first ``##`` is the doc's introduction and
    is ignored. Headings that do not name a column are kept, so a test can
    catch them; the router only ever asks for real columns.

    Args:
        markdown: The doc's text.

    Returns:
        A mapping of heading to checklist body.
    """
    sections: dict[str, str] = {}
    current = ""
    lines: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if current:
                sections[current] = "\n".join(lines).strip()
            current, lines = line[3:].strip(), []
        elif current:
            lines.append(line)
    if current:
        sections[current] = "\n".join(lines).strip()
    return sections


@dataclass(frozen=True)
class CardSnapshot:
    """What the reconciler knows about one card.

    Attributes:
        number: The issue number.
        is_open: Whether the issue is open.
        labels: Label names on the issue.
        status: The card's current column, or None if it has none.
        synced: The column the reconciler last recorded, or empty.
        prior: The column recorded when the card entered Published, or empty.
    """

    number: int
    is_open: bool
    labels: frozenset[str]
    status: str | None
    synced: str
    prior: str


@dataclass(frozen=True)
class CardPlan:
    """What the reconciler should do for one card.

    Every field defaults to "do nothing", so an empty plan is safe to execute.

    Attributes:
        set_synced: Record this column as last seen, or None to leave it.
        set_prior: Record this prior column (``""`` clears it), or None.
        move_to: Move the card to this column, or None.
        labels_add: Stage labels to add.
        labels_remove: Stage labels to remove.
        checklist: Post this column's checklist, or None.
        flags: Sentences describing an odd move, each posted as a comment.
        close: Whether to close the issue.
        check_parent: Whether to re-check the parent post's translations.
    """

    set_synced: str | None = None
    set_prior: str | None = None
    move_to: str | None = None
    labels_add: tuple[str, ...] = ()
    labels_remove: tuple[str, ...] = ()
    checklist: str | None = None
    flags: tuple[str, ...] = ()
    close: bool = False
    check_parent: bool = False

    def is_empty(self) -> bool:
        """Return whether the plan does nothing."""
        return self == CardPlan()


def _label_sync(labels: frozenset[str], column: str) -> tuple[tuple[str, ...], ...]:
    """Return (add, remove) to make the stage labels match ``column``."""
    want = stage_label(column)
    stale = tuple(
        sorted(x for x in labels if x.startswith(STAGE_LABEL_PREFIX) and x != want)
    )
    add = () if want in labels else (want,)
    return add, stale


def describe_flags(route: Route, from_col: str, to_col: str) -> tuple[str, ...]:
    """Describe what is odd about a move, as sentences for a comment.

    Args:
        route: The card's route.
        from_col: The column the card left.
        to_col: The column the card entered.

    Returns:
        Zero or more sentences.
    """
    if from_col not in COLUMNS or to_col not in COLUMNS:
        return ()
    flags: list[str] = []
    if _index(to_col) < _index(from_col):
        flags.append(
            f"This card moved back from **{from_col}** to **{to_col}**. "
            "If that was to send it for rework, say what needs to change."
        )
    skipped = skipped_gates(route, from_col, to_col)
    if skipped:
        names = ", ".join(f"**{g}**" for g in skipped)
        flags.append(
            f"This card moved from **{from_col}** to **{to_col}** and skipped "
            f"{names}, which this post's route requires. If that stage happened "
            "somewhere else, say where."
        )
    return tuple(flags)


def reconcile_card(card: CardSnapshot) -> CardPlan:
    """Decide what the reconciler should do for one card.

    The board column is the source of truth: a human move is never reverted.
    The reconciler compares the column with the one it last recorded; a
    difference is a move to act on. The first time it sees a card it only
    records it, so turning automation on does not comment on every card.

    Args:
        card: The card's current state.

    Returns:
        The plan. Execute it as given; an empty plan does nothing.
    """
    if card.status is None:
        return CardPlan()
    route = route_for(card.labels)

    # Reopened after publishing: Published closed it and recorded where it
    # was, so put it back there. A card without a recorded prior predates the
    # reconciler, so it stays where a human left it.
    if card.status == PUBLISHED and card.is_open and card.prior:
        add, remove = _label_sync(card.labels, card.prior)
        return CardPlan(
            set_synced=card.prior,
            set_prior="",
            move_to=card.prior,
            labels_add=add,
            labels_remove=remove,
        )

    add, remove = _label_sync(card.labels, card.status)

    if not card.synced:
        return CardPlan(set_synced=card.status, labels_add=add, labels_remove=remove)

    if card.status == card.synced:
        return CardPlan(labels_add=add, labels_remove=remove)

    publishing = card.status == PUBLISHED
    return CardPlan(
        set_synced=card.status,
        set_prior=card.synced if publishing else None,
        labels_add=add,
        labels_remove=remove,
        checklist=card.status,
        flags=describe_flags(route, card.synced, card.status),
        close=publishing and card.is_open,
        check_parent=publishing and route is Route.TRANSLATION,
    )
