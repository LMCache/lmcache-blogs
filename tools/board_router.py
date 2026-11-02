# SPDX-License-Identifier: Apache-2.0
"""Route content-board cards from issue labels.

Decides which column an issue belongs in, adds it to the project board, and sets
its status. Two modes:

``route``
    Handle one issue, named by number. Used by the ``issues`` event trigger.
``sweep``
    Walk every open issue in the repository and route any that is missing from
    the board or sitting with no status. This is the safety net: it catches
    issues created while the workflow was failing, issues that predate the
    workflow, and anything the event trigger missed.

The routing decision itself is :func:`route`, a pure function with no I/O, so it
can be tested exhaustively. Its defining property is **totality**: every
combination of labels produces a decision, and no input is silently ignored. An
issue the router cannot place is labelled ``needs-triage`` and commented on
rather than dropped.

Board writes need a **classic** token with the ``project`` scope, which the
workflow passes as a separate secret. ``GITHUB_TOKEN`` cannot write to Projects
V2, and a fine-grained PAT has no account-level Projects permission, so it
cannot reach a user-owned board. See ``docs/pipeline/board-routing.md``.
"""

# Future
from __future__ import annotations

# Standard
from dataclasses import dataclass
import argparse
import json
import os
import re
import subprocess
import sys

# Third Party
import board_stages as stages

# The board is located at runtime, never hardcoded, so this repo survives being
# transferred to another owner. See docs/pipeline/board-routing.md.
#
#   BOARD_OWNER  -- the login that owns the project. Defaults to the owner of
#                   the repository being routed, which is right whenever the
#                   board and the repo live under the same account or org.
#   BOARD_NUMBER -- the project number. No default: a wrong guess would write
#                   to somebody else's board, so an unset value is an error.
#
# The owner may be a user or an organization and the code does not care; the
# GraphQL uses `repositoryOwner`, which resolves either.
BOARD_OWNER_ENV = "BOARD_OWNER"
BOARD_NUMBER_ENV = "BOARD_NUMBER"

# The three blog intake templates, and the column each one enters. Path D is
# refined further by its `entry_lane` front matter; see route().
TEMPLATE_LABELS = ("skeleton", "needs-tech-review", "tech-verified")

# Column names come from the stage rules, so there is one list of them.
COLUMN_IDEA = stages.IDEA
COLUMN_DRAFTING = stages.DRAFTING
COLUMN_EDITORIAL = stages.EDITORIAL
COLUMN_TECHNICAL = stages.TECHNICAL
COLUMN_TRANSLATIONS = stages.TRANSLATIONS

TRIAGE_LABEL = "needs-triage"

# Valid `entry_lane` values on intake path D, and the column each selects.
ENTRY_LANES = {"editorial": COLUMN_EDITORIAL, "technical": COLUMN_TECHNICAL}


@dataclass(frozen=True)
class Decision:
    """What the router decided to do with one issue.

    Attributes:
        column: Board column to place the issue in, or None to leave it off the
            board entirely (it is not editorial work).
        needs_triage: Whether a human must look at this issue. Drives the
            ``needs-triage`` label and an explanatory comment.
        reason: One sentence naming why this decision was reached. Always
            populated, so every issue has a recorded rationale whether or not it
            needed triage.
    """

    column: str | None
    needs_triage: bool
    reason: str


def parse_entry_lane(body: str) -> str | None:
    """Extract ``entry_lane`` from an issue body's fenced YAML block.

    Path D's template asks the author which review lane the draft has earned.
    That value lives in the fenced ``yaml`` block, not in a label, so it has to
    be read out of the body text.

    Args:
        body: Raw issue body. May be empty.

    Returns:
        The declared lane, lowercased and stripped of trailing comments, or None
        if the body has no ``entry_lane`` line or the field was left blank. A
        blank field is not an error: the contract treats an absent lane as
        editorial.
    """
    # Horizontal whitespace only. A bare ``\s*`` would cross the newline and
    # capture the next YAML key, routing the card off an unrelated field.
    match = re.search(r"^[ \t]*entry_lane:[ \t]*([^\s#]*)", body, re.MULTILINE)
    if match is None:
        return None
    return match.group(1).strip().lower() or None


def route(labels: frozenset[str], entry_lane: str | None) -> Decision:
    """Decide where an issue belongs.

    Total by construction: every input returns a Decision. Nothing falls through
    to an implicit default, because an issue that quietly goes nowhere is the
    failure this router exists to prevent.

    Precedence is deliberate. A label conflict is checked before any single
    label is honoured, so an issue carrying two template labels is triaged
    rather than routed by whichever branch happened to run first.

    Args:
        labels: Label names on the issue.
        entry_lane: Value parsed from the body's YAML, or None. Only consulted
            for intake path D.

    Returns:
        The routing decision, always with a populated reason.
    """
    if stages.TRANSLATION_LABEL in labels:
        # A translation sub-issue usually copies its post's labels, intake
        # labels included. It is still a translation, so this comes first.
        return Decision(
            column=COLUMN_TRANSLATIONS,
            needs_triage=False,
            reason="a translation of a post, so it starts in Translations",
        )

    template_labels = sorted(labels & frozenset(TEMPLATE_LABELS))

    if len(template_labels) > 1:
        return Decision(
            column=COLUMN_IDEA,
            needs_triage=True,
            reason=(
                f"carries more than one intake label ({', '.join(template_labels)}), "
                "so the intended path is ambiguous"
            ),
        )

    if template_labels == ["skeleton"]:
        return Decision(
            column=COLUMN_DRAFTING,
            needs_triage=False,
            reason="intake path A/B/C: a skeleton to be written up",
        )

    if template_labels == ["tech-verified"]:
        return Decision(
            column=COLUMN_EDITORIAL,
            needs_triage=False,
            reason=(
                "intake path E: written and technically verified, so it enters the "
                "copyedit and skips Technical review"
            ),
        )

    if template_labels == ["needs-tech-review"]:
        if entry_lane is None:
            return Decision(
                column=COLUMN_EDITORIAL,
                needs_triage=False,
                reason=(
                    "intake path D with no entry_lane declared, which the contract "
                    "treats as editorial"
                ),
            )
        if entry_lane in ENTRY_LANES:
            return Decision(
                column=ENTRY_LANES[entry_lane],
                needs_triage=False,
                reason=f"intake path D, entry_lane: {entry_lane}",
            )
        # The parse contract is explicit that an unrecognised lane is a
        # validation error rather than something to guess at, because guessing
        # silently skips a review.
        return Decision(
            column=COLUMN_EDITORIAL,
            needs_triage=True,
            reason=(
                f"intake path D declares entry_lane: {entry_lane!r}, which is not a "
                f"valid lane ({' or '.join(sorted(ENTRY_LANES))}); routed to "
                "Editorial review pending a human decision"
            ),
        )

    if "blog" in labels:
        # Maintainers file posts by hand with only the blog label. That is the
        # normal way an idea starts, so it lands in Idea without a triage flag.
        return Decision(
            column=COLUMN_IDEA,
            needs_triage=False,
            reason="a post filed by hand with the blog label, so it starts as an Idea",
        )

    if "pipeline" in labels:
        return Decision(
            column=None,
            needs_triage=False,
            reason=(
                "pipeline work rather than editorial content; the content board's "
                "columns do not apply, so it stays off the board"
            ),
        )

    return Decision(
        column=None,
        needs_triage=True,
        reason=(
            "carries neither a blog nor a pipeline label, so it has not been "
            "classified as either kind of work"
        ),
    )


def run_gh(args: list[str], token_env: str = "GH_TOKEN") -> str:
    """Run a ``gh`` command and return its stdout.

    Args:
        args: Arguments to pass to ``gh``, without the leading ``gh``.
        token_env: Environment variable holding the token to authenticate with.
            Board operations need a project-scoped token, which is a different
            secret from the one used for issue operations.

    Returns:
        Captured stdout, stripped.

    Raises:
        RuntimeError: If the named token variable is unset, or ``gh`` exits
            non-zero. Both are raised rather than swallowed so a broken run
            fails visibly instead of silently skipping issues.
    """
    token = os.environ.get(token_env, "")
    if not token:
        raise RuntimeError(
            f"{token_env} is not set. Board writes need a classic token with "
            "the project scope; see docs/pipeline/board-routing.md."
        )
    env = dict(os.environ, GH_TOKEN=token)
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, env=env, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def graphql(query: str, token_env: str = "PROJECT_TOKEN", **variables: str) -> dict:
    """Run a GraphQL query through ``gh api`` and return the ``data`` object.

    Args:
        query: GraphQL document.
        token_env: Environment variable holding the token to use.
        **variables: Query variables, passed as ``-F`` field arguments.

    Returns:
        The response's ``data`` object.

    Raises:
        RuntimeError: If the response carries an ``errors`` array.
    """
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        args += ["-F", f"{key}={value}"]
    payload = json.loads(run_gh(args, token_env=token_env) or "{}")
    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"GraphQL response had no data object: {payload}")
    return data


def board_location(repo: str) -> tuple[str, int]:
    """Resolve which project board to write to.

    Reads ``BOARD_OWNER`` and ``BOARD_NUMBER`` from the environment. The owner
    defaults to the owner of ``repo``, which is correct whenever the board and
    the repository sit under the same account or organization -- including
    after the repository is transferred, which is the point of not hardcoding
    it.

    ``BOARD_NUMBER`` has no default on purpose. Project numbers are small
    integers that are reused across every account on GitHub, so a guessed value
    would not fail: it would quietly write cards onto a stranger's board.

    Args:
        repo: Repository in ``owner/name`` form.

    Returns:
        A tuple of (owner login, project number).

    Raises:
        RuntimeError: If ``BOARD_NUMBER`` is unset or is not a positive
            integer, or if ``repo`` is not in ``owner/name`` form.
    """
    owner = os.environ.get(BOARD_OWNER_ENV, "").strip()
    if not owner:
        if "/" not in repo:
            raise RuntimeError(
                f"cannot infer the board owner: {repo!r} is not owner/name, and "
                f"{BOARD_OWNER_ENV} is unset"
            )
        owner = repo.split("/", 1)[0]

    raw = os.environ.get(BOARD_NUMBER_ENV, "").strip()
    if not raw:
        raise RuntimeError(
            f"{BOARD_NUMBER_ENV} is not set. It has no default because project "
            "numbers are reused across accounts, so a guess would write to the "
            "wrong board rather than fail. Set it to the board's number; see "
            "docs/pipeline/board-routing.md."
        )
    try:
        number = int(raw)
    except ValueError:
        raise RuntimeError(
            f"{BOARD_NUMBER_ENV} must be an integer, got {raw!r}"
        ) from None
    if number < 1:
        raise RuntimeError(f"{BOARD_NUMBER_ENV} must be positive, got {number}")
    return owner, number


def board_context(repo: str) -> tuple[str, str, dict[str, str]]:
    """Fetch the board's ids and its Status option ids.

    Args:
        repo: Repository in ``owner/name`` form, used to resolve the board.

    Returns:
        A tuple of (project id, Status field id, mapping of column name to
        option id).

    Raises:
        RuntimeError: If the board has no Status field, which would mean the
            columns were never configured.
    """
    owner, number = board_location(repo)
    data = graphql(
        """
        query($owner: String!, $number: Int!) {
          repositoryOwner(login: $owner) {
            __typename
            ... on ProjectV2Owner {
              projectV2(number: $number) {
                id
                field(name: "Status") {
                  ... on ProjectV2SingleSelectField { id options { id name } }
                }
              }
            }
          }
        }
        """,
        owner=owner,
        number=str(number),
    )
    holder = data.get("repositoryOwner")
    if not holder:
        raise RuntimeError(f"no GitHub account or organization named {owner!r}")
    project = holder.get("projectV2")
    if not project:
        raise RuntimeError(
            f"{owner!r} ({holder.get('__typename', 'unknown')}) has no project "
            f"number {number}, or the token cannot see it"
        )
    field = project.get("field")
    if not field:
        raise RuntimeError(
            "the board has no Status field; its columns have not been configured"
        )
    options = {option["name"]: option["id"] for option in field["options"]}
    return project["id"], field["id"], options


def place_on_board(repo: str, issue_node_id: str, column: str) -> None:
    """Add an issue to the board and set its Status.

    Adding is idempotent: GitHub returns the existing item if the issue is
    already on the board, so a re-run moves the card rather than duplicating it.

    Args:
        repo: Repository in ``owner/name`` form, used to resolve the board.
        issue_node_id: The issue's GraphQL node id.
        column: Target column name, which must exist on the board.

    Raises:
        RuntimeError: If the column does not exist on the board. A routing table
            naming a column nobody created is a silent dead end, so it fails.
    """
    project_id, field_id, options = board_context(repo)
    if column not in options:
        raise RuntimeError(
            f"column {column!r} does not exist on the board. Present: {sorted(options)}"
        )
    added = graphql(
        """
        mutation($project: ID!, $content: ID!) {
          addProjectV2ItemById(input: {projectId: $project, contentId: $content}) {
            item { id }
          }
        }
        """,
        project=project_id,
        content=issue_node_id,
    )
    item_id = added["addProjectV2ItemById"]["item"]["id"]
    graphql(
        """
        mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $project, itemId: $item, fieldId: $field,
            value: {singleSelectOptionId: $option}
          }) { projectV2Item { id } }
        }
        """,
        project=project_id,
        item=item_id,
        field=field_id,
        option=options[column],
    )


def issue_details(repo: str, number: int) -> dict:
    """Fetch the fields of one issue that routing depends on.

    Args:
        repo: Repository in ``owner/name`` form.
        number: Issue number.

    Returns:
        The issue's ``number``, ``id``, ``body``, ``labels``, and ``state``.
    """
    raw = run_gh(
        [
            "issue",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            "number,id,body,labels,state",
        ]
    )
    parsed = json.loads(raw)
    return dict(parsed)


def apply_triage(repo: str, number: int, reason: str) -> None:
    """Label an issue for triage and say why, once.

    The comment is what stops a triaged issue from becoming a silent dead end:
    the label makes it findable, the comment makes it actionable. Re-running is
    safe — an issue that already carries the label is left alone rather than
    commented on again.

    Args:
        repo: Repository in ``owner/name`` form.
        number: Issue number.
        reason: The routing decision's reason, quoted to the reader.
    """
    existing = issue_details(repo, number)
    if any(label["name"] == TRIAGE_LABEL for label in existing["labels"]):
        return
    run_gh(["issue", "edit", str(number), "--repo", repo, "--add-label", TRIAGE_LABEL])
    body = (
        f"The content-board router could not place this automatically: {reason}.\n\n"
        f"It has been labelled `{TRIAGE_LABEL}` so it does not get lost. A human "
        "should either add the right intake label, or move the card by hand.\n\n"
        "Routing rules are in "
        "[`docs/pipeline/board-routing.md`](../blob/main/docs/pipeline/board-routing.md)."
    )
    run_gh(["issue", "comment", str(number), "--repo", repo, "--body", body])


def handle_issue(repo: str, number: int, dry_run: bool) -> Decision:
    """Route one issue and report what happened.

    Args:
        repo: Repository in ``owner/name`` form.
        number: Issue number.
        dry_run: When true, decide and print but change nothing.

    Returns:
        The decision that was reached.
    """
    issue = issue_details(repo, number)
    labels = frozenset(label["name"] for label in issue["labels"])
    decision = route(labels, parse_entry_lane(issue["body"] or ""))

    # Placement is for issues not on the board yet. Once a card exists, its
    # column belongs to whoever moved it last, human or automation, so an
    # edit or a new label must never send it back to its entry column.
    if decision.column is not None and number in board_issue_numbers(repo):
        print(f"#{number} is already on the board; left where it is")
        return decision

    target = decision.column or "(off board)"
    flag = " [needs-triage]" if decision.needs_triage else ""
    print(f"#{number} -> {target}{flag}: {decision.reason}")

    if dry_run:
        return decision
    if decision.column is not None:
        place_on_board(repo, issue["id"], decision.column)
    if decision.needs_triage:
        apply_triage(repo, number, decision.reason)
    return decision


def board_issue_numbers(repo: str) -> set[int]:
    """Return the numbers of this repository's issues already on the board.

    Pages through every item, so it stays correct past 100 cards. Only issues
    from ``repo`` count: an issue from another repository with the same number
    must not make this repository's issue look placed.

    Args:
        repo: Repository in ``owner/name`` form, used to resolve the board.

    Returns:
        Issue numbers. Pull requests, draft items, and other repositories'
        issues are ignored.
    """
    owner, number = board_location(repo)
    found: set[int] = set()
    cursor = "null"
    while True:
        data = graphql(
            """
            query($owner: String!, $number: Int!, $cursor: String) {
              repositoryOwner(login: $owner) {
                ... on ProjectV2Owner {
                  projectV2(number: $number) {
                    items(first: 100, after: $cursor) {
                      pageInfo { hasNextPage endCursor }
                      nodes {
                        content {
                          ... on Issue {
                            number repository { nameWithOwner }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
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
            if issue["repository"]["nameWithOwner"].lower() == repo.lower():
                found.add(issue["number"])
        if not page["pageInfo"]["hasNextPage"]:
            return found
        cursor = page["pageInfo"]["endCursor"]


def sweep(repo: str, dry_run: bool) -> int:
    """Route every open issue that is not already on the board.

    This is the safety net. The event trigger handles issues as they arrive, but
    it cannot handle issues that predate the workflow, arrived while it was
    failing, or were missed for any other reason. Running this on a schedule
    means an issue can be late to the board but never absent from it.

    Args:
        repo: Repository in ``owner/name`` form.
        dry_run: When true, decide and print but change nothing.

    Returns:
        Count of issues acted on.
    """
    raw = run_gh(
        [
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--limit",
            "200",
            "--json",
            "number",
        ]
    )
    open_numbers = {entry["number"] for entry in json.loads(raw or "[]")}
    on_board = board_issue_numbers(repo)
    missing = sorted(open_numbers - on_board)

    print(f"open issues: {len(open_numbers)}; on board: {len(on_board)}")
    if not missing:
        print("nothing missing from the board")
        return 0

    print(f"routing {len(missing)} issue(s) absent from the board: {missing}")
    for number in missing:
        handle_issue(repo, number, dry_run)
    return len(missing)


def main(argv: list[str]) -> int:
    """Parse arguments and dispatch.

    Args:
        argv: Command-line arguments, without the program name.

    Returns:
        Process exit status.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["route", "sweep"])
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--issue", type=int, help="issue number, for route mode")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.mode == "route":
        if args.issue is None:
            parser.error("route mode needs --issue")
        handle_issue(args.repo, args.issue, args.dry_run)
        return 0

    sweep(args.repo, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
