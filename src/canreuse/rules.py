"""The judgement: may material under SOURCE go into a project under PROJECT?

The question is directional and asymmetric. Putting a permissive component into
a GPL project is fine; putting a GPL component into a permissive project is not,
because the GPL's terms would have to spread to the whole project. `assess`
answers in that direction: source *into* project.

What this module encodes:

  * The category logic -- permissive flows into anything, copyleft constrains the
    whole (strong) or the touched files (weak), network-copyleft adds the
    service trigger.
  * A small table of well-established special cases the category logic would get
    wrong, most famously Apache-2.0 into GPL-2.0-only.

What it deliberately does NOT do is pretend to resolve every pair. Genuinely
contested or version-sensitive combinations return REVIEW. The tool's value is
that it is right where it speaks and honest where it stops -- a wrong "allowed"
is the only truly expensive output.
"""

from __future__ import annotations

from .data import resolve
from .model import Assessment, Category, License, Verdict

FSF = "https://www.gnu.org/licenses/license-list.html"
APACHE_GPL = "https://www.apache.org/licenses/GPL-compatibility.html"

# (source_spdx, project_spdx) -> (verdict, reason, citation)
# Only pairs where the plain category logic is known to be wrong. Order of the
# pair is source-into-project, matching `assess`.
_SPECIAL_CASES: dict[tuple[str, str], tuple[Verdict, str, str]] = {
    # Apache-2.0's patent-termination and notice terms are "further
    # restrictions" GPLv2 does not allow. FSF and Apache both state this.
    ("Apache-2.0", "GPL-2.0-only"): (
        Verdict.DISALLOWED,
        "Apache-2.0 imposes patent-termination and notice terms that GPL-2.0-only "
        "treats as additional restrictions, so the two cannot be combined. "
        "(Apache-2.0 IS compatible with GPL-3.0.)",
        APACHE_GPL,
    ),
    ("Apache-2.0", "GPL-2.0-or-later"): (
        Verdict.REVIEW,
        "Apache-2.0 is incompatible with GPL-2.0 but compatible with GPL-3.0. "
        "'or-later' lets the project move to GPL-3.0, which resolves it -- but "
        "only if you actually take the GPL-3.0 option. A human must confirm that.",
        APACHE_GPL,
    ),
    # GPLv2-only and GPLv3 cannot be combined: neither is a subset of the other.
    ("GPL-2.0-only", "GPL-3.0-only"): (
        Verdict.DISALLOWED,
        "GPL-2.0-only and GPL-3.0-only are mutually incompatible: v2-only forbids "
        "moving to v3, and v3 code cannot be relicensed back to v2.",
        FSF,
    ),
    ("GPL-3.0-only", "GPL-2.0-only"): (
        Verdict.DISALLOWED,
        "GPL-3.0-only material cannot be placed in a GPL-2.0-only project; v2 has "
        "no upgrade path to v3.",
        FSF,
    ),
    ("GPL-2.0-only", "GPL-2.0-or-later"): (
        Verdict.ALLOWED_WITH_OBLIGATIONS,
        "GPL-2.0-only fixes the combined work at v2; the project's 'or-later' "
        "option narrows to v2-only as a result.",
        FSF,
    ),
}


def _attribution_obligations(lic: License) -> list[str]:
    out: list[str] = []
    if lic.requires_attribution:
        out.append(f"Keep {lic.spdx_id}'s copyright and license notice with the material.")
    if lic.requires_state_changes:
        out.append("Mark the files you changed as modified.")
    if lic.patent_grant:
        out.append(f"Preserve {lic.spdx_id}'s patent-related notices.")
    return out


def _copyleft_obligations(lic: License, whole_work: bool) -> list[str]:
    scope = "the entire combined work" if whole_work else f"the {lic.spdx_id} files themselves"
    out = [
        f"Distribute {scope} under {lic.spdx_id} (or a compatible later version).",
        f"Offer the corresponding source for {scope}.",
    ]
    if lic.category is Category.NETWORK_COPYLEFT:
        out.append(
            "Because it is network-copyleft, offering the app over a network counts "
            "as distribution: users interacting with it remotely can demand the source."
        )
    return out


def assess(source: str, project: str) -> Assessment:
    """Can material under `source` be incorporated into a project under `project`?

    Both arguments are license identifiers (SPDX ids or common aliases).
    """
    src = resolve(source)
    prj = resolve(project)

    if src is None or prj is None:
        missing = [name for name, lic in (("source", src), ("project", prj)) if lic is None]
        which = " and ".join(source if n == "source" else project for n in missing)
        return Assessment(
            source_id=source,
            project_id=project,
            verdict=Verdict.UNKNOWN,
            reasons=(
                f"Could not identify the license for {' and '.join(missing)}: {which!r}. "
                "An unrecognised license is not assumed to be safe.",
            ),
        )

    # Special cases first: they exist precisely because the general logic below
    # would get them wrong.
    special = _SPECIAL_CASES.get((src.spdx_id, prj.spdx_id))
    if special is not None:
        verdict, reason, citation = special
        obligations = tuple(_attribution_obligations(src)) if verdict.ok_to_proceed else ()
        return Assessment(
            source_id=src.spdx_id,
            project_id=prj.spdx_id,
            verdict=verdict,
            reasons=(reason,),
            obligations=obligations,
            citations=(citation,),
        )

    return _by_category(src, prj)


def _by_category(src: License, prj: License) -> Assessment:
    reasons: list[str] = []
    obligations: list[str] = []
    citations: tuple[str, ...] = (FSF,)

    # Public-domain source: goes anywhere, no strings.
    if src.category is Category.PUBLIC_DOMAIN:
        return Assessment(
            source_id=src.spdx_id,
            project_id=prj.spdx_id,
            verdict=Verdict.ALLOWED,
            reasons=(f"{src.spdx_id} places no conditions on reuse; it can go into any project.",),
            citations=citations,
        )

    # Permissive source: goes into anything, but you carry its notice.
    if src.category is Category.PERMISSIVE:
        reasons.append(
            f"{src.spdx_id} is permissive, so it can be incorporated into a {prj.spdx_id} project."
        )
        obligations += _attribution_obligations(src)
        return Assessment(
            source_id=src.spdx_id,
            project_id=prj.spdx_id,
            verdict=Verdict.ALLOWED_WITH_OBLIGATIONS,
            reasons=tuple(reasons),
            obligations=tuple(obligations),
            citations=citations,
        )

    # Weak copyleft: the licensed files keep their license and their source must
    # be offered, but the rest of the project is unaffected. So it can enter a
    # more-permissive or even proprietary project, with obligations scoped to
    # those files.
    if src.category is Category.WEAK_COPYLEFT:
        reasons.append(
            f"{src.spdx_id} is weak copyleft: its own files stay under {src.spdx_id}, "
            f"but they can live inside a {prj.spdx_id} project without relicensing the rest."
        )
        obligations += _attribution_obligations(src)
        obligations += _copyleft_obligations(src, whole_work=False)
        return Assessment(
            source_id=src.spdx_id,
            project_id=prj.spdx_id,
            verdict=Verdict.ALLOWED_WITH_OBLIGATIONS,
            reasons=tuple(reasons),
            obligations=tuple(obligations),
            citations=citations,
        )

    # Strong / network copyleft source.
    if src.category in (Category.STRONG_COPYLEFT, Category.NETWORK_COPYLEFT):
        # Into a project that is at least as copyleft (same family) → obligations.
        if prj.category is src.category and prj.spdx_id == src.spdx_id:
            obligations += _attribution_obligations(src)
            obligations += _copyleft_obligations(src, whole_work=True)
            return Assessment(
                source_id=src.spdx_id,
                project_id=prj.spdx_id,
                verdict=Verdict.ALLOWED_WITH_OBLIGATIONS,
                reasons=(
                    f"{src.spdx_id} into a {prj.spdx_id} project is consistent; the "
                    "whole combined work stays under that license.",
                ),
                obligations=tuple(obligations),
                citations=citations,
            )
        # Into anything less constraining → the project would have to relicense.
        if prj.category.rank < src.category.rank:
            return Assessment(
                source_id=src.spdx_id,
                project_id=prj.spdx_id,
                verdict=Verdict.DISALLOWED,
                reasons=(
                    f"{src.spdx_id} requires the whole combined work to be {src.spdx_id}. "
                    f"A {prj.spdx_id} project cannot absorb it without relicensing the "
                    "entire project -- which is usually not what you want.",
                ),
                citations=citations,
            )
        # Different copyleft families, or same rank but different id → contested.
        return Assessment(
            source_id=src.spdx_id,
            project_id=prj.spdx_id,
            verdict=Verdict.REVIEW,
            reasons=(
                f"Combining {src.spdx_id} into a {prj.spdx_id} project depends on the "
                "specific version-compatibility between two copyleft licenses. This "
                "needs a human to confirm the exact combination is permitted.",
            ),
            citations=citations,
        )

    # Proprietary source, or anything unclassified: never a machine green light.
    return Assessment(
        source_id=src.spdx_id,
        project_id=prj.spdx_id,
        verdict=Verdict.REVIEW,
        reasons=(
            f"{src.spdx_id} carries custom or proprietary terms. Whether it may enter "
            f"a {prj.spdx_id} project depends on the actual grant, which only a human "
            "reading the terms can decide.",
        ),
        citations=citations,
    )
