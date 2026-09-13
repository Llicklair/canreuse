"""The vocabulary: licenses, categories, verdicts.

Everything here is data or a plain enum. No policy lives in this module; the
rules that turn two licenses into a verdict live in `rules.py`. Keeping the
facts (what a license *is*) separate from the judgement (what you may *do*)
means the facts can be checked against SPDX independently of the logic.

A standing rule for the whole project: when we are not sure, we do not say
"allowed". Uncertainty resolves to REVIEW or UNKNOWN, never to a green light.
License mistakes are cheap to warn about and expensive to ship.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Category(StrEnum):
    """How a license constrains combined and derivative works.

    Ordered from least to most constraining. The order is meaningful:
    incorporating a *more* constraining license into a *less* constraining
    project is where obligations and conflicts arise.
    """

    PUBLIC_DOMAIN = "public-domain"
    PERMISSIVE = "permissive"  # MIT, BSD, Apache-2.0
    WEAK_COPYLEFT = "weak-copyleft"  # MPL-2.0, LGPL, EPL -- file/library scope
    STRONG_COPYLEFT = "strong-copyleft"  # GPL family -- whole combined work
    NETWORK_COPYLEFT = "network-copyleft"  # AGPL -- triggers on network use
    PROPRIETARY = "proprietary"  # all rights reserved / custom terms

    @property
    def rank(self) -> int:
        return _RANK[self]


_RANK = {
    Category.PUBLIC_DOMAIN: 0,
    Category.PERMISSIVE: 1,
    Category.WEAK_COPYLEFT: 2,
    Category.STRONG_COPYLEFT: 3,
    Category.NETWORK_COPYLEFT: 4,
    Category.PROPRIETARY: 5,
}


class Verdict(StrEnum):
    """The answer to 'may I incorporate source into project?'"""

    ALLOWED = "allowed"  # no strings beyond none-to-speak-of
    ALLOWED_WITH_OBLIGATIONS = "allowed-with-obligations"  # yes, but you must...
    REVIEW = "review"  # plausibly fine, but a human must decide
    DISALLOWED = "disallowed"  # the combination is not permitted as-is
    UNKNOWN = "unknown"  # we can't identify a license; fail safe

    @property
    def ok_to_proceed(self) -> bool:
        """True only for verdicts a machine may act on without a human.

        REVIEW and UNKNOWN both return False on purpose: they are the
        fail-safe states, and an agent must stop at them.
        """
        return self in (Verdict.ALLOWED, Verdict.ALLOWED_WITH_OBLIGATIONS)


@dataclass(frozen=True, slots=True)
class License:
    """One license the tool knows about.

    `spdx_id` is the identity and must match SPDX exactly (case-sensitive).
    The flags are the levers the rules read; they are facts about the licence
    text, not opinions.
    """

    spdx_id: str
    name: str
    category: Category
    osi_approved: bool
    requires_attribution: bool  # you must keep the copyright/licence notice
    requires_state_changes: bool  # you must note that you modified it
    requires_source_disclosure: bool  # you must offer the (modified) source
    patent_grant: bool  # the licence includes an explicit patent grant

    def __post_init__(self) -> None:
        if not self.spdx_id.strip():
            raise ValueError("spdx_id must be non-empty")


@dataclass(frozen=True, slots=True)
class Assessment:
    """The result of a check. The only thing the engine returns.

    `reasons` explain the verdict in plain words. `obligations` are the things
    you take on if you proceed. `not_legal_advice` is always True and always
    surfaced -- this tool encodes a curated reading of well-established rules,
    not the judgement of a lawyer.
    """

    source_id: str
    project_id: str
    verdict: Verdict
    reasons: tuple[str, ...] = ()
    obligations: tuple[str, ...] = ()
    not_legal_advice: bool = True
    citations: tuple[str, ...] = field(default_factory=tuple)
