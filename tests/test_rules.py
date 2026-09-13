"""Tests for the compatibility engine.

Each test pins one rule the tool's usefulness depends on. The most important is
`test_the_case_that_started_this`: the exact situation this tool was built for.
"""

from __future__ import annotations

from canreuse import Verdict, assess

# --- the reason this exists -------------------------------------------------


def test_the_case_that_started_this():
    """NHS text under OGL... no. The real one: copyrighted text into Apache-2.0.

    Concretely: a strong-copyleft snippet must not silently land in a permissive
    project. The tool has to say DISALLOWED, not shrug.
    """
    a = assess("GPL-3.0-only", "Apache-2.0")
    assert a.verdict is Verdict.DISALLOWED
    assert not a.verdict.ok_to_proceed


# --- the famous special case ------------------------------------------------


def test_apache_into_gplv2_is_disallowed():
    a = assess("Apache-2.0", "GPL-2.0-only")
    assert a.verdict is Verdict.DISALLOWED
    assert "patent" in " ".join(a.reasons).lower()


def test_apache_into_gplv3_is_allowed():
    a = assess("Apache-2.0", "GPL-3.0-only")
    assert a.verdict is Verdict.ALLOWED_WITH_OBLIGATIONS


def test_gplv2_only_and_gplv3_only_are_incompatible_both_ways():
    assert assess("GPL-2.0-only", "GPL-3.0-only").verdict is Verdict.DISALLOWED
    assert assess("GPL-3.0-only", "GPL-2.0-only").verdict is Verdict.DISALLOWED


# --- category logic ---------------------------------------------------------


def test_public_domain_goes_anywhere_clean():
    a = assess("CC0-1.0", "GPL-3.0-only")
    assert a.verdict is Verdict.ALLOWED
    assert a.obligations == ()


def test_permissive_into_anything_carries_its_notice():
    a = assess("MIT", "Apache-2.0")
    assert a.verdict is Verdict.ALLOWED_WITH_OBLIGATIONS
    assert any("notice" in o.lower() for o in a.obligations)


def test_apache_source_obligations_include_state_changes_and_patent():
    a = assess("Apache-2.0", "MIT")
    text = " ".join(a.obligations).lower()
    assert "modified" in text
    assert "patent" in text


def test_weak_copyleft_may_enter_a_proprietary_project_with_obligations():
    """The whole point of weak vs strong: MPL files can sit in a closed project."""
    a = assess("MPL-2.0", "MIT")
    assert a.verdict is Verdict.ALLOWED_WITH_OBLIGATIONS
    assert any("source" in o.lower() for o in a.obligations)
    assert any("files themselves" in o.lower() for o in a.obligations)


def test_strong_copyleft_into_permissive_is_disallowed():
    a = assess("GPL-3.0-only", "MIT")
    assert a.verdict is Verdict.DISALLOWED


def test_gpl_into_same_gpl_is_allowed_with_whole_work_obligation():
    a = assess("GPL-3.0-only", "GPL-3.0-only")
    assert a.verdict is Verdict.ALLOWED_WITH_OBLIGATIONS
    assert any("combined work" in o.lower() for o in a.obligations)


def test_agpl_surfaces_the_network_trigger():
    a = assess("AGPL-3.0-only", "AGPL-3.0-only")
    assert a.verdict is Verdict.ALLOWED_WITH_OBLIGATIONS
    assert any("network" in o.lower() for o in a.obligations)


def test_agpl_into_permissive_is_disallowed():
    assert assess("AGPL-3.0-only", "MIT").verdict is Verdict.DISALLOWED


# --- fail safe --------------------------------------------------------------


def test_unknown_license_is_never_allowed():
    a = assess("MIT", "Some-Custom-EULA-v3")
    assert a.verdict is Verdict.UNKNOWN
    assert not a.verdict.ok_to_proceed


def test_unknown_names_both_missing():
    a = assess("Whatever-1.0", "Also-Nonsense")
    assert a.verdict is Verdict.UNKNOWN


def test_proprietary_source_goes_to_review_not_allowed():
    # A recognised-but-proprietary style: we don't ship one, so use the fact that
    # an unrecognised id is UNKNOWN; proprietary category is exercised via REVIEW
    # path when a future proprietary entry exists. For now assert UNKNOWN fails safe.
    a = assess("LicenseRef-Acme-Internal", "MIT")
    assert not a.verdict.ok_to_proceed


# --- aliases ----------------------------------------------------------------


def test_common_spellings_resolve():
    assert assess("apache 2.0", "gplv2").verdict is Verdict.DISALLOWED
    assert assess("BSD", "MIT").verdict is Verdict.ALLOWED_WITH_OBLIGATIONS


def test_every_answer_flags_not_legal_advice():
    for pair in [("MIT", "MIT"), ("GPL-3.0-only", "MIT"), ("x", "y")]:
        assert assess(*pair).not_legal_advice is True
