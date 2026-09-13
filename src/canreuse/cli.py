"""Command line: `canreuse <source> <project>`.

Exit code carries the verdict so a script or agent can branch without parsing
prose: 0 = safe to proceed, 2 = stop and look, 1 = usage error. An agent doing
`canreuse GPL-3.0-only Apache-2.0` gets a non-zero exit and does not paste.
"""

from __future__ import annotations

import argparse
import json
import sys

from .model import Assessment, Verdict
from .rules import assess

_EXIT = {
    Verdict.ALLOWED: 0,
    Verdict.ALLOWED_WITH_OBLIGATIONS: 0,
    Verdict.REVIEW: 2,
    Verdict.DISALLOWED: 2,
    Verdict.UNKNOWN: 2,
}

_MARK = {
    Verdict.ALLOWED: "OK",
    Verdict.ALLOWED_WITH_OBLIGATIONS: "OK, with obligations",
    Verdict.REVIEW: "REVIEW -- a human must decide",
    Verdict.DISALLOWED: "NO",
    Verdict.UNKNOWN: "UNKNOWN -- license not recognised",
}


def _render(a: Assessment) -> str:
    lines = [
        f"{_MARK[a.verdict]}",
        f"  incorporate {a.source_id}  ->  project under {a.project_id}",
        "",
    ]
    for r in a.reasons:
        lines.append(f"  why:  {r}")
    if a.obligations:
        lines.append("")
        lines.append("  you must:")
        lines += [f"    - {o}" for o in a.obligations]
    if a.citations:
        lines.append("")
        lines += [f"  ref:  {c}" for c in a.citations]
    lines.append("")
    lines.append("  Not legal advice -- a curated reading of well-established terms.")
    return "\n".join(lines)


def _as_json(a: Assessment) -> str:
    return json.dumps(
        {
            "source": a.source_id,
            "project": a.project_id,
            "verdict": a.verdict.value,
            "ok_to_proceed": a.verdict.ok_to_proceed,
            "reasons": list(a.reasons),
            "obligations": list(a.obligations),
            "citations": list(a.citations),
            "not_legal_advice": a.not_legal_advice,
        },
        indent=2,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="canreuse",
        description="Can material under SOURCE be incorporated into a project under PROJECT?",
    )
    parser.add_argument("source", help="license of the material you want to reuse (SPDX id)")
    parser.add_argument("project", help="license your project is distributed under (SPDX id)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    result = assess(args.source, args.project)
    print(_as_json(result) if args.json else _render(result))
    return _EXIT[result.verdict]


if __name__ == "__main__":
    sys.exit(main())
