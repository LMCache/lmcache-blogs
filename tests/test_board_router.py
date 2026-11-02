# SPDX-License-Identifier: Apache-2.0
"""Tests for the content-board routing decision.

These exercise the public contract of :func:`route` and
:func:`parse_entry_lane` — the pure half of the router. The board writes are
not tested here; they are I/O against a live project and are covered by running
the workflow in dry-run mode.

The test that matters most is :func:`test_route_is_total`, which asserts the
property the router exists to guarantee: no combination of labels goes
unhandled.
"""

# Future
from __future__ import annotations

# Standard
from pathlib import Path
import itertools
import sys

# Third Party
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

# Third Party
from board_router import (  # noqa: E402
    BOARD_NUMBER_ENV,
    BOARD_OWNER_ENV,
    COLUMN_DRAFTING,
    COLUMN_EDITORIAL,
    COLUMN_IDEA,
    COLUMN_TECHNICAL,
    COLUMN_TRANSLATIONS,
    TEMPLATE_LABELS,
    Decision,
    board_location,
    parse_entry_lane,
    route,
)

ALL_LABELS = (*TEMPLATE_LABELS, "blog", "l10n", "pipeline", "bug", "documentation")


def decide(*labels: str, entry_lane: str | None = None) -> Decision:
    """Route a set of labels, for brevity in the tests below.

    Args:
        *labels: Label names on the hypothetical issue.
        entry_lane: Declared lane, if any.

    Returns:
        The routing decision.
    """
    return route(frozenset(labels), entry_lane)


class TestSkeletonPath:
    """Intake paths A, B, and C — a skeleton someone else writes up."""

    def test_skeleton_enters_drafting(self) -> None:
        result = decide("blog", "skeleton")
        assert result.column == COLUMN_DRAFTING
        assert not result.needs_triage

    def test_entry_lane_is_ignored(self) -> None:
        """A stray entry_lane on a skeleton does not divert it."""
        assert decide("blog", "skeleton", entry_lane="technical").column == (
            COLUMN_DRAFTING
        )


class TestDraftPath:
    """Intake path D — written, technical content still needs checking."""

    def test_editorial_lane(self) -> None:
        result = decide("blog", "draft", "needs-tech-review", entry_lane="editorial")
        assert result.column == COLUMN_EDITORIAL
        assert not result.needs_triage

    def test_technical_lane(self) -> None:
        result = decide("blog", "draft", "needs-tech-review", entry_lane="technical")
        assert result.column == COLUMN_TECHNICAL
        assert not result.needs_triage

    def test_missing_lane_defaults_to_editorial_without_triage(self) -> None:
        """An absent lane is the documented default, not an error."""
        result = decide("blog", "draft", "needs-tech-review", entry_lane=None)
        assert result.column == COLUMN_EDITORIAL
        assert not result.needs_triage

    @pytest.mark.parametrize("lane", ["translations", "publish", "", "editoral"])
    def test_invalid_lane_routes_but_flags(self, lane: str) -> None:
        """An unrecognised lane is a validation error, never a silent guess.

        It still lands somewhere — leaving the card off the board would be the
        worse failure — but it is flagged so a human confirms the lane.
        """
        result = decide("blog", "draft", "needs-tech-review", entry_lane=lane)
        assert result.column == COLUMN_EDITORIAL
        assert result.needs_triage
        assert lane in result.reason or "not a valid lane" in result.reason


class TestCompletePath:
    """Intake path E — written and already technically verified."""

    def test_enters_editorial_not_technical(self) -> None:
        result = decide("blog", "complete", "tech-verified")
        assert result.column == COLUMN_EDITORIAL
        assert not result.needs_triage

    def test_never_routes_to_technical_review(self) -> None:
        """Skipping Technical review is the whole point of path E."""
        for lane in (None, "editorial", "technical", "nonsense"):
            assert decide("blog", "tech-verified", entry_lane=lane).column != (
                COLUMN_TECHNICAL
            )


class TestAmbiguousAndUnclassified:
    """The cases that would otherwise become dead ends."""

    @pytest.mark.parametrize("pair", list(itertools.combinations(TEMPLATE_LABELS, 2)))
    def test_conflicting_intake_labels_are_triaged(self, pair: tuple[str, str]) -> None:
        """Two intake labels means the author's intent is unknowable.

        Precedence would let one label win arbitrarily, which silently picks a
        review path. Triage instead.
        """
        result = decide("blog", *pair)
        assert result.needs_triage
        assert result.column == COLUMN_IDEA
        for label in pair:
            assert label in result.reason

    def test_all_three_intake_labels_are_triaged(self) -> None:
        assert decide("blog", *TEMPLATE_LABELS).needs_triage

    def test_bare_blog_label_goes_to_idea_without_triage(self) -> None:
        """Hand-filed posts carry only `blog`; that is normal, not unknown."""
        result = decide("blog")
        assert result.column == COLUMN_IDEA
        assert not result.needs_triage

    def test_translation_goes_to_translations(self) -> None:
        result = decide("blog", "l10n")
        assert result.column == COLUMN_TRANSLATIONS
        assert not result.needs_triage

    def test_translation_label_wins_over_intake_labels(self) -> None:
        """A translation copies its post's labels; it is still a translation."""
        result = decide("blog", "l10n", "tech-verified")
        assert result.column == COLUMN_TRANSLATIONS

    def test_pipeline_stays_off_board_without_triage(self) -> None:
        """Pipeline work is classified, just not editorial. Not a dead end."""
        result = decide("pipeline")
        assert result.column is None
        assert not result.needs_triage
        assert result.reason

    def test_pipeline_bug_stays_off_board(self) -> None:
        result = decide("pipeline", "bug")
        assert result.column is None
        assert not result.needs_triage

    def test_unclassified_issue_is_triaged(self) -> None:
        """A blank issue with neither label is the case most likely to rot."""
        result = decide()
        assert result.column is None
        assert result.needs_triage

    def test_unrelated_labels_alone_are_triaged(self) -> None:
        assert decide("documentation", "bug").needs_triage


class TestTotality:
    """The property the router exists to provide."""

    @pytest.mark.parametrize("size", [0, 1, 2, 3])
    def test_route_is_total(self, size: int) -> None:
        """Every label combination yields a decision with a reason.

        This is the guarantee that nothing is ignored. Any input either lands in
        a real column, or is explicitly and justifiably left off the board, and
        in every case carries a human-readable reason. Nothing returns an empty
        decision and nothing raises.
        """
        lanes: list[str | None] = [None, "editorial", "technical", "bogus"]
        for combo in itertools.combinations(ALL_LABELS, size):
            for lane in lanes:
                result = route(frozenset(combo), lane)
                assert result.reason, f"no reason for {combo} lane={lane}"
                assert result.column is None or isinstance(result.column, str)
                # Off-board without triage must be a deliberate classification.
                if result.column is None and not result.needs_triage:
                    assert "pipeline" in combo

    @pytest.mark.parametrize("size", [0, 1, 2, 3])
    def test_every_routed_column_is_a_real_column(self, size: int) -> None:
        """The router never names a column that does not exist on the board.

        The seven live columns are asserted against in the workflow itself;
        here we pin the four this router can ever produce.
        """
        allowed = {
            COLUMN_IDEA,
            COLUMN_DRAFTING,
            COLUMN_EDITORIAL,
            COLUMN_TECHNICAL,
            COLUMN_TRANSLATIONS,
        }
        for combo in itertools.combinations(ALL_LABELS, size):
            column = route(frozenset(combo), None).column
            assert column is None or column in allowed


class TestParseEntryLane:
    """Reading entry_lane out of an issue body."""

    def test_reads_from_yaml_block(self) -> None:
        body = "```yaml\ndraft: http://x\nentry_lane: technical\nauthor: kw\n```"
        assert parse_entry_lane(body) == "technical"

    def test_strips_trailing_comment(self) -> None:
        assert parse_entry_lane("entry_lane: editorial # editorial | technical") == (
            "editorial"
        )

    def test_lowercases(self) -> None:
        assert parse_entry_lane("entry_lane: Editorial") == "editorial"

    def test_tolerates_leading_whitespace(self) -> None:
        assert parse_entry_lane("  entry_lane:   technical  ") == "technical"

    def test_missing_returns_none(self) -> None:
        assert parse_entry_lane("no yaml here at all") is None

    def test_empty_body_returns_none(self) -> None:
        assert parse_entry_lane("") is None

    def test_blank_value_returns_none(self) -> None:
        """An author who deleted the value gets the documented default."""
        assert parse_entry_lane("entry_lane:\nauthor: kw") is None


class TestBoardLocation:
    """Resolving which board to write to.

    This is what makes the repository survive a transfer: nothing about the
    board's location is compiled in.
    """

    def test_owner_defaults_to_the_repo_owner(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The common case: board and repo under the same account or org."""
        monkeypatch.delenv(BOARD_OWNER_ENV, raising=False)
        monkeypatch.setenv(BOARD_NUMBER_ENV, "5")
        assert board_location("LMCache/lmcache-blogs") == ("LMCache", 5)

    def test_owner_default_follows_a_transfer(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Same code, new owner, no edit required.

        This is the property the whole change exists for: moving the repo
        changes the resolved owner without anyone touching the source.
        """
        monkeypatch.delenv(BOARD_OWNER_ENV, raising=False)
        monkeypatch.setenv(BOARD_NUMBER_ENV, "5")
        assert board_location("quaid/lmcache-blogs")[0] == "quaid"
        assert board_location("LMCache/lmcache-blogs")[0] == "LMCache"

    def test_explicit_owner_wins(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """For a board that lives under a different owner than the repo."""
        monkeypatch.setenv(BOARD_OWNER_ENV, "LMCache")
        monkeypatch.setenv(BOARD_NUMBER_ENV, "3")
        assert board_location("quaid/lmcache-blogs") == ("LMCache", 3)

    def test_missing_number_raises_rather_than_guessing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The failure that matters.

        Project numbers are small integers reused across every account on
        GitHub, so a default would not fail loudly -- it would write cards onto
        somebody else's board. Unset must raise.
        """
        monkeypatch.delenv(BOARD_OWNER_ENV, raising=False)
        monkeypatch.delenv(BOARD_NUMBER_ENV, raising=False)
        with pytest.raises(RuntimeError, match=BOARD_NUMBER_ENV):
            board_location("LMCache/lmcache-blogs")

    @pytest.mark.parametrize("bad", ["", "   ", "abc", "5.5", "0", "-1"])
    def test_rejects_a_number_that_is_not_a_positive_integer(
        self, monkeypatch: pytest.MonkeyPatch, bad: str
    ) -> None:
        monkeypatch.delenv(BOARD_OWNER_ENV, raising=False)
        monkeypatch.setenv(BOARD_NUMBER_ENV, bad)
        with pytest.raises(RuntimeError):
            board_location("LMCache/lmcache-blogs")

    def test_rejects_a_repo_that_is_not_owner_slash_name(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv(BOARD_OWNER_ENV, raising=False)
        monkeypatch.setenv(BOARD_NUMBER_ENV, "5")
        with pytest.raises(RuntimeError, match="owner/name"):
            board_location("lmcache-blogs")

    def test_whitespace_is_tolerated(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A value pasted from a settings page often carries a space."""
        monkeypatch.setenv(BOARD_OWNER_ENV, "  LMCache  ")
        monkeypatch.setenv(BOARD_NUMBER_ENV, " 7 ")
        assert board_location("quaid/x") == ("LMCache", 7)
