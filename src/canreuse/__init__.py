"""canreuse — can material under one license go into a project under another?

    from canreuse import assess
    a = assess("GPL-3.0-only", "Apache-2.0")
    a.verdict            # Verdict.DISALLOWED
    a.verdict.ok_to_proceed   # False

The check is directional: assess(source, project) asks whether SOURCE material
may be incorporated into a project distributed under PROJECT.
"""

from .data import LICENSES, resolve
from .model import Assessment, Category, License, Verdict
from .rules import assess

__version__ = "0.1.0"

__all__ = [
    "LICENSES",
    "Assessment",
    "Category",
    "License",
    "Verdict",
    "assess",
    "resolve",
]
