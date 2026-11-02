# SPDX-License-Identifier: Apache-2.0
"""Tests for the content-board stage rules.

These cover the pure half of board automation: which stages a post must pass
through, where an approval, an opened PR, or a merge moves a card, how a human
move is classified, and what the reconciler decides for one card. Nothing here
touches GitHub.
"""

# Future
from __future__ import annotations

# Standard
from pathlib import Path
import sys

# Third Party
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

# Third Party
from board_stages import (  # noqa: E402
    COLUMNS,
    COPYEDIT,
    DRAFTING,
    EDITORIAL,
    IDEA,
    PUBLISHED,
    TECHNICAL,
    TRANSLATIONS,
    CardSnapshot,
    PrState,
    Route,
    after_approval,
    approval_counts,
    on_merge,
    on_pr_opened,
    parent_should_publish,
    parse_checklists,
    parse_post_ref,
    reconcile_card,
    required_gates,
    route_for,
    skipped_gates,
    stage_label,
)

REPO = "LMCache/lmcache-blogs"
CHECKLIST_DOC = (
    Path(__file__).resolve().parents[1] / "docs" / "pipeline" / "stage-checklists.md"
)


def snap(
    status: str | None,
    synced: str = "",
    *,
    labels: tuple[str, ...] = ("blog",),
    is_open: bool = True,
    prior: str = "",
) -> CardSnapshot:
    """Build a card snapshot with sensible defaults for the tests below.

    Args:
        status: The card's current column.
        synced: The column the reconciler last recorded.
        labels: Labels on the issue.
        is_open: Whether the issue is open.
        prior: The column recorded before the card entered Published.

    Returns:
        The snapshot.
    """
    return CardSnapshot(
        number=1,
        is_open=is_open,
        labels=frozenset(labels),
        status=status,
        synced=synced,
        prior=prior,
    )


class TestRoutes:
    """Which route a post takes, and which review stages it must pass."""

    def test_skeleton_needs_every_review(self) -> None:
        assert route_for(frozenset({"blog", "skeleton"})) is Route.FULL
        assert required_gates(Route.FULL) == (EDITORIAL, TECHNICAL, COPYEDIT)

    def test_bare_blog_label_takes_the_full_route(self) -> None:
        """Hand-filed posts carry only `blog`. The safe default is every gate."""
        assert route_for(frozenset({"blog"})) is Route.FULL

    def test_needs_tech_review_needs_every_review(self) -> None:
        assert route_for(frozenset({"blog", "needs-tech-review"})) is Route.FULL

    def test_tech_verified_skips_technical_review(self) -> None:
        assert route_for(frozenset({"blog", "tech-verified"})) is Route.VERIFIED
        assert required_gates(Route.VERIFIED) == (EDITORIAL, COPYEDIT)

    def test_conflicting_intake_labels_take_the_stricter_route(self) -> None:
        """When the path is ambiguous, ask for more review, not less."""
        labels = frozenset({"blog", "tech-verified", "needs-tech-review"})
        assert route_for(labels) is Route.FULL

    def test_translation_has_no_review_gates(self) -> None:
        assert route_for(frozenset({"blog", "l10n"})) is Route.TRANSLATION
        assert required_gates(Route.TRANSLATION) == ()


class TestApproval:
    """Where a maintainer's approving review moves a card."""

    @pytest.mark.parametrize(
        ("column", "expected"),
        [(EDITORIAL, TECHNICAL), (TECHNICAL, COPYEDIT), (COPYEDIT, TRANSLATIONS)],
    )
    def test_full_route_advances_one_gate(self, column: str, expected: str) -> None:
        assert after_approval(Route.FULL, column) == expected

    def test_verified_route_jumps_past_technical(self) -> None:
        assert after_approval(Route.VERIFIED, EDITORIAL) == COPYEDIT

    def test_verified_card_dragged_into_technical_still_advances(self) -> None:
        """A human may send a verified post to Technical review anyway."""
        assert after_approval(Route.VERIFIED, TECHNICAL) == COPYEDIT

    @pytest.mark.parametrize("column", [IDEA, DRAFTING, TRANSLATIONS, PUBLISHED])
    def test_outside_a_review_column_an_approval_moves_nothing(
        self, column: str
    ) -> None:
        assert after_approval(Route.FULL, column) is None

    def test_unknown_column_moves_nothing(self) -> None:
        assert after_approval(Route.FULL, "Backlog") is None


class TestApprovalCounts:
    """Which reviews count as a stage approval."""

    def test_maintainer_approval_after_the_last_move_counts(self) -> None:
        assert approval_counts(
            state="APPROVED",
            association="MEMBER",
            reviewer="editor",
            pr_author="author",
            submitted_at="2026-10-13T10:00:00Z",
            status_changed_at="2026-10-13T09:00:00Z",
        )

    def test_approval_before_the_last_move_does_not_count_twice(self) -> None:
        """The card already moved past the stage this approval was for."""
        assert not approval_counts(
            state="APPROVED",
            association="MEMBER",
            reviewer="editor",
            pr_author="author",
            submitted_at="2026-10-13T08:00:00Z",
            status_changed_at="2026-10-13T09:00:00Z",
        )

    @pytest.mark.parametrize("association", ["CONTRIBUTOR", "NONE", "FIRST_TIMER"])
    def test_non_maintainer_approval_does_not_count(self, association: str) -> None:
        assert not approval_counts(
            state="APPROVED",
            association=association,
            reviewer="someone",
            pr_author="author",
            submitted_at="2026-10-13T10:00:00Z",
            status_changed_at="2026-10-13T09:00:00Z",
        )

    def test_author_cannot_approve_their_own_stage(self) -> None:
        assert not approval_counts(
            state="APPROVED",
            association="OWNER",
            reviewer="author",
            pr_author="author",
            submitted_at="2026-10-13T10:00:00Z",
            status_changed_at="2026-10-13T09:00:00Z",
        )

    @pytest.mark.parametrize("state", ["COMMENTED", "CHANGES_REQUESTED", "DISMISSED"])
    def test_only_approvals_count(self, state: str) -> None:
        assert not approval_counts(
            state=state,
            association="MEMBER",
            reviewer="editor",
            pr_author="author",
            submitted_at="2026-10-13T10:00:00Z",
            status_changed_at="2026-10-13T09:00:00Z",
        )

    def test_card_with_no_recorded_move_accepts_any_approval(self) -> None:
        assert approval_counts(
            state="APPROVED",
            association="MEMBER",
            reviewer="editor",
            pr_author="author",
            submitted_at="2026-10-13T10:00:00Z",
            status_changed_at="",
        )


class TestPrOpenedAndMerged:
    """Moves caused by the draft PR itself."""

    @pytest.mark.parametrize("column", [IDEA, "Claimed", DRAFTING])
    def test_opening_a_draft_pr_starts_editorial_review(self, column: str) -> None:
        assert on_pr_opened(column) == EDITORIAL

    @pytest.mark.parametrize(
        "column", [EDITORIAL, TECHNICAL, COPYEDIT, TRANSLATIONS, PUBLISHED]
    )
    def test_opening_never_moves_a_card_backwards(self, column: str) -> None:
        assert on_pr_opened(column) is None

    def test_card_with_no_column_starts_editorial_review(self) -> None:
        assert on_pr_opened(None) == EDITORIAL

    def test_merge_publishes_when_no_translation_is_open(self) -> None:
        assert on_merge(COPYEDIT, open_translations=0) == PUBLISHED
        assert on_merge(TRANSLATIONS, open_translations=0) == PUBLISHED

    def test_merge_waits_in_translations_while_any_is_open(self) -> None:
        assert on_merge(COPYEDIT, open_translations=2) == TRANSLATIONS

    def test_merge_does_not_move_a_waiting_card(self) -> None:
        assert on_merge(TRANSLATIONS, open_translations=1) is None

    def test_merge_does_not_touch_a_published_card(self) -> None:
        assert on_merge(PUBLISHED, open_translations=0) is None


class TestMoveClassification:
    """How a move is described when it is flagged."""

    def test_skipping_technical_on_the_full_route_is_flagged(self) -> None:
        assert skipped_gates(Route.FULL, EDITORIAL, COPYEDIT) == (TECHNICAL,)

    def test_skipping_technical_on_the_verified_route_is_fine(self) -> None:
        assert skipped_gates(Route.VERIFIED, EDITORIAL, COPYEDIT) == ()

    def test_jumping_from_idea_to_published_skips_every_gate(self) -> None:
        assert skipped_gates(Route.FULL, IDEA, PUBLISHED) == (
            EDITORIAL,
            TECHNICAL,
            COPYEDIT,
        )

    def test_the_gate_being_left_is_not_skipped(self) -> None:
        assert skipped_gates(Route.FULL, TECHNICAL, COPYEDIT) == ()

    def test_a_backward_move_skips_nothing(self) -> None:
        assert skipped_gates(Route.FULL, COPYEDIT, EDITORIAL) == ()


class TestPostRef:
    """Finding which post a PR belongs to."""

    def test_post_line(self) -> None:
        ref = parse_post_ref("Adds the draft.\n\nPost: #36\n", REPO)
        assert ref is not None and ref.number == 36

    def test_post_line_is_case_insensitive_and_spacing_tolerant(self) -> None:
        ref = parse_post_ref("post:   #7", REPO)
        assert ref is not None and ref.number == 7

    def test_post_line_with_a_full_url(self) -> None:
        body = f"Post: https://github.com/{REPO}/issues/12"
        ref = parse_post_ref(body, REPO)
        assert ref is not None and ref.number == 12

    def test_url_to_another_repo_is_ignored(self) -> None:
        assert parse_post_ref("Post: https://github.com/x/y/issues/12", REPO) is None

    def test_single_refs_is_accepted(self) -> None:
        """content/README.md told authors to write Refs #N before Post: existed."""
        ref = parse_post_ref("Refs #28", REPO)
        assert ref is not None and ref.number == 28

    def test_post_line_wins_over_refs(self) -> None:
        ref = parse_post_ref("Refs #5\nPost: #9", REPO)
        assert ref is not None and ref.number == 9

    def test_several_refs_are_ambiguous(self) -> None:
        assert parse_post_ref("Refs #5, Refs #6", REPO) is None

    def test_closing_keyword_is_not_a_post_ref(self) -> None:
        """Fixes #N would close the post on merge; it does not name one."""
        assert parse_post_ref("Fixes #36", REPO) is None

    def test_empty_body(self) -> None:
        assert parse_post_ref("", REPO) is None


class TestChecklists:
    """The checklists live in a doc that humans edit, not in the code."""

    def test_parses_headings_into_columns(self) -> None:
        doc = (
            "# Title\n\nIntro.\n\n"
            "## Copyedit\n\n- [ ] one\n\n"
            "## Technical review\n\n- [ ] two\n"
        )
        parsed = parse_checklists(doc)
        assert parsed[COPYEDIT].strip() == "- [ ] one"
        assert parsed[TECHNICAL].strip() == "- [ ] two"

    def test_real_doc_names_only_real_columns(self) -> None:
        parsed = parse_checklists(CHECKLIST_DOC.read_text(encoding="utf-8"))
        assert set(parsed) <= set(COLUMNS)

    def test_real_doc_covers_every_review_stage_and_translations(self) -> None:
        parsed = parse_checklists(CHECKLIST_DOC.read_text(encoding="utf-8"))
        for column in (EDITORIAL, TECHNICAL, COPYEDIT, TRANSLATIONS):
            assert parsed.get(column, "").strip(), f"no checklist for {column}"


class TestReconcile:
    """What the reconciler decides for one card."""

    def test_first_sight_records_quietly(self) -> None:
        """Rollout must not bury every existing card in comments."""
        plan = reconcile_card(snap(TECHNICAL, synced=""))
        assert plan.set_synced == TECHNICAL
        assert plan.checklist is None
        assert plan.flags == ()
        assert not plan.close
        assert plan.labels_add == (stage_label(TECHNICAL),)

    def test_first_sight_of_an_open_published_card_does_not_close_it(self) -> None:
        plan = reconcile_card(snap(PUBLISHED, synced=""))
        assert not plan.close

    def test_unmoved_card_needs_nothing(self) -> None:
        plan = reconcile_card(
            snap(COPYEDIT, synced=COPYEDIT, labels=("blog", stage_label(COPYEDIT)))
        )
        assert plan.is_empty()

    def test_unmoved_card_with_a_wrong_stage_label_is_healed(self) -> None:
        plan = reconcile_card(
            snap(COPYEDIT, synced=COPYEDIT, labels=("blog", stage_label(EDITORIAL)))
        )
        assert plan.labels_add == (stage_label(COPYEDIT),)
        assert plan.labels_remove == (stage_label(EDITORIAL),)
        assert plan.checklist is None

    def test_forward_move_gets_label_and_checklist(self) -> None:
        plan = reconcile_card(
            snap(TECHNICAL, synced=EDITORIAL, labels=("blog", stage_label(EDITORIAL)))
        )
        assert plan.set_synced == TECHNICAL
        assert plan.labels_add == (stage_label(TECHNICAL),)
        assert plan.labels_remove == (stage_label(EDITORIAL),)
        assert plan.checklist == TECHNICAL
        assert plan.flags == ()

    def test_skipping_a_gate_is_flagged_not_reverted(self) -> None:
        plan = reconcile_card(snap(COPYEDIT, synced=EDITORIAL))
        assert plan.move_to is None
        assert any(TECHNICAL in flag for flag in plan.flags)

    def test_verified_post_skipping_technical_is_not_flagged(self) -> None:
        plan = reconcile_card(
            snap(COPYEDIT, synced=EDITORIAL, labels=("blog", "tech-verified"))
        )
        assert plan.flags == ()

    def test_backward_move_is_flagged(self) -> None:
        plan = reconcile_card(snap(EDITORIAL, synced=COPYEDIT))
        assert any("back" in flag for flag in plan.flags)

    def test_reaching_published_closes_and_remembers_the_prior_column(self) -> None:
        plan = reconcile_card(snap(PUBLISHED, synced=TRANSLATIONS))
        assert plan.close
        assert plan.set_prior == TRANSLATIONS

    def test_reaching_published_when_already_closed_does_not_close_again(
        self,
    ) -> None:
        plan = reconcile_card(snap(PUBLISHED, synced=TRANSLATIONS, is_open=False))
        assert not plan.close

    def test_reopened_published_card_returns_to_its_prior_column(self) -> None:
        plan = reconcile_card(
            snap(PUBLISHED, synced=PUBLISHED, prior=TRANSLATIONS, is_open=True)
        )
        assert plan.move_to == TRANSLATIONS
        assert plan.set_synced == TRANSLATIONS
        assert plan.set_prior == ""

    def test_open_published_card_without_a_prior_is_left_alone(self) -> None:
        """A card that predates the reconciler has no prior column to restore."""
        plan = reconcile_card(snap(PUBLISHED, synced=PUBLISHED, prior=""))
        assert plan.move_to is None
        assert not plan.close

    def test_translation_reaching_published_checks_its_parent(self) -> None:
        plan = reconcile_card(
            snap(PUBLISHED, synced=TRANSLATIONS, labels=("blog", "l10n"))
        )
        assert plan.check_parent

    def test_card_with_no_column_is_left_alone(self) -> None:
        assert reconcile_card(snap(None, synced="")).is_empty()

    def test_renamed_column_in_synced_is_not_flagged(self) -> None:
        """If a column was renamed, the old name is unknown: no flags."""
        plan = reconcile_card(snap(COPYEDIT, synced="Line edit"))
        assert plan.set_synced == COPYEDIT
        assert plan.flags == ()


class TestParentPublishing:
    """When a post moves to Published because its translations finished."""

    def test_all_translations_closed_and_pr_merged(self) -> None:
        assert parent_should_publish(TRANSLATIONS, 0, 3, PrState.MERGED)

    def test_all_translations_closed_and_no_pr(self) -> None:
        assert parent_should_publish(TRANSLATIONS, 0, 2, PrState.NONE)

    def test_draft_pr_still_open_holds_it(self) -> None:
        """The English post merges at publication. Until then, it waits."""
        assert not parent_should_publish(TRANSLATIONS, 0, 2, PrState.OPEN)

    def test_a_translation_still_open_holds_it(self) -> None:
        assert not parent_should_publish(TRANSLATIONS, 1, 2, PrState.MERGED)

    def test_no_translations_at_all_is_a_human_decision(self) -> None:
        assert not parent_should_publish(TRANSLATIONS, 0, 0, PrState.MERGED)

    def test_only_from_translations(self) -> None:
        assert not parent_should_publish(COPYEDIT, 0, 2, PrState.MERGED)


class TestStageLabel:
    def test_slug(self) -> None:
        assert stage_label(EDITORIAL) == "stage:editorial-review"
        assert stage_label(COPYEDIT) == "stage:copyedit"
