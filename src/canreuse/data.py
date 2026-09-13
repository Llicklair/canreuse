"""The license knowledge base.

Facts about each license, keyed by exact SPDX identifier. The flags here are
read from the license texts and the FSF/SPDX/OSI classifications, not invented.
Where a project uses an identifier we do not carry, the tool says UNKNOWN rather
than guessing -- an unrecognised license is not a permissive one by default.

Coverage is deliberately the common set, not all ~600 SPDX ids. Breadth without
accuracy would be worse than a smaller set that is right.
"""

from __future__ import annotations

from .model import Category, License

_LICENSES: tuple[License, ...] = (
    # ---- public domain / no attribution ----
    License(
        "CC0-1.0",
        "Creative Commons Zero v1.0 Universal",
        Category.PUBLIC_DOMAIN,
        osi_approved=False,
        requires_attribution=False,
        requires_state_changes=False,
        requires_source_disclosure=False,
        patent_grant=False,
    ),
    License(
        "Unlicense",
        "The Unlicense",
        Category.PUBLIC_DOMAIN,
        osi_approved=True,
        requires_attribution=False,
        requires_state_changes=False,
        requires_source_disclosure=False,
        patent_grant=False,
    ),
    License(
        "0BSD",
        "BSD Zero Clause License",
        Category.PUBLIC_DOMAIN,
        osi_approved=True,
        requires_attribution=False,
        requires_state_changes=False,
        requires_source_disclosure=False,
        patent_grant=False,
    ),
    # ---- permissive ----
    License(
        "MIT",
        "MIT License",
        Category.PERMISSIVE,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=False,
        requires_source_disclosure=False,
        patent_grant=False,
    ),
    License(
        "ISC",
        "ISC License",
        Category.PERMISSIVE,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=False,
        requires_source_disclosure=False,
        patent_grant=False,
    ),
    License(
        "BSD-2-Clause",
        'BSD 2-Clause "Simplified" License',
        Category.PERMISSIVE,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=False,
        requires_source_disclosure=False,
        patent_grant=False,
    ),
    License(
        "BSD-3-Clause",
        'BSD 3-Clause "New" or "Revised" License',
        Category.PERMISSIVE,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=False,
        requires_source_disclosure=False,
        patent_grant=False,
    ),
    License(
        "Zlib",
        "zlib License",
        Category.PERMISSIVE,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=False,
        patent_grant=False,
    ),
    License(
        "Apache-2.0",
        "Apache License 2.0",
        Category.PERMISSIVE,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=False,
        patent_grant=True,
    ),
    # ---- weak copyleft (file / library scope) ----
    License(
        "MPL-2.0",
        "Mozilla Public License 2.0",
        Category.WEAK_COPYLEFT,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=True,
        patent_grant=True,
    ),
    License(
        "LGPL-2.1-only",
        "GNU Lesser General Public License v2.1 only",
        Category.WEAK_COPYLEFT,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=True,
        patent_grant=False,
    ),
    License(
        "LGPL-3.0-only",
        "GNU Lesser General Public License v3.0 only",
        Category.WEAK_COPYLEFT,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=True,
        patent_grant=True,
    ),
    License(
        "EPL-2.0",
        "Eclipse Public License 2.0",
        Category.WEAK_COPYLEFT,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=True,
        patent_grant=True,
    ),
    # ---- strong copyleft (whole combined work) ----
    License(
        "GPL-2.0-only",
        "GNU General Public License v2.0 only",
        Category.STRONG_COPYLEFT,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=True,
        patent_grant=False,
    ),
    License(
        "GPL-2.0-or-later",
        "GNU General Public License v2.0 or later",
        Category.STRONG_COPYLEFT,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=True,
        patent_grant=False,
    ),
    License(
        "GPL-3.0-only",
        "GNU General Public License v3.0 only",
        Category.STRONG_COPYLEFT,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=True,
        patent_grant=True,
    ),
    License(
        "GPL-3.0-or-later",
        "GNU General Public License v3.0 or later",
        Category.STRONG_COPYLEFT,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=True,
        patent_grant=True,
    ),
    # ---- network copyleft ----
    License(
        "AGPL-3.0-only",
        "GNU Affero General Public License v3.0 only",
        Category.NETWORK_COPYLEFT,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=True,
        patent_grant=True,
    ),
    License(
        "AGPL-3.0-or-later",
        "GNU Affero General Public License v3.0 or later",
        Category.NETWORK_COPYLEFT,
        osi_approved=True,
        requires_attribution=True,
        requires_state_changes=True,
        requires_source_disclosure=True,
        patent_grant=True,
    ),
)

LICENSES: dict[str, License] = {lic.spdx_id: lic for lic in _LICENSES}

# Common non-SPDX spellings people actually type, mapped to the canonical id.
# Kept small and obvious; anything not here stays UNKNOWN rather than being
# guessed into the wrong bucket.
_ALIASES: dict[str, str] = {
    "MIT License": "MIT",
    "BSD": "BSD-3-Clause",
    "BSD-3": "BSD-3-Clause",
    "BSD-2": "BSD-2-Clause",
    "Apache": "Apache-2.0",
    "Apache 2.0": "Apache-2.0",
    "Apache2": "Apache-2.0",
    "Apache-2": "Apache-2.0",
    "GPL": "GPL-3.0-or-later",
    "GPLv2": "GPL-2.0-only",
    "GPLv3": "GPL-3.0-only",
    "GPL-2.0": "GPL-2.0-only",
    "GPL-3.0": "GPL-3.0-only",
    "LGPL": "LGPL-3.0-only",
    "LGPL-2.1": "LGPL-2.1-only",
    "LGPL-3.0": "LGPL-3.0-only",
    "AGPL": "AGPL-3.0-only",
    "AGPL-3.0": "AGPL-3.0-only",
    "MPL": "MPL-2.0",
    "MPL 2.0": "MPL-2.0",
    "CC0": "CC0-1.0",
    "public domain": "CC0-1.0",
    "unlicense": "Unlicense",
}


def resolve(identifier: str) -> License | None:
    """Return the License for an SPDX id or a known alias, or None.

    Matching is exact first (SPDX is case-sensitive), then a case-insensitive
    alias lookup for the spellings people actually type. Returning None is a
    real answer: it means 'I do not recognise this', which the caller must
    treat as UNKNOWN, not as safe.
    """
    ident = identifier.strip()
    if ident in LICENSES:
        return LICENSES[ident]
    if ident in _ALIASES:
        return LICENSES[_ALIASES[ident]]
    lowered = ident.lower()
    for spelling, canonical in _ALIASES.items():
        if spelling.lower() == lowered:
            return LICENSES[canonical]
    for spdx_id, lic in LICENSES.items():
        if spdx_id.lower() == lowered:
            return lic
    return None
