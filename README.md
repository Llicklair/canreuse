# canreuse

**Can I reuse this?** A deterministic check for whether material under one
license may be incorporated into a project under another.

Built because its author nearly pasted copyrighted text into an Apache-2.0
repo, and caught it only by reading the license by hand. No linter, type
checker or test would have caught it. This is that missing check.

```bash
canreuse GPL-3.0-only Apache-2.0
# NO  -- GPL-3.0-only requires the whole combined work to be GPL-3.0-only.

canreuse Apache-2.0 GPL-2.0-only
# NO  -- Apache-2.0 patent terms are restrictions GPL-2.0-only forbids.

canreuse MIT Apache-2.0
# OK, with obligations -- keep MIT notice.
```

The check is **directional**: `canreuse SOURCE PROJECT` asks whether SOURCE
material may go into a project distributed under PROJECT. Reuse is asymmetric
-- permissive flows into copyleft, not the reverse.

## Why a tool and not a web search

An agent pasting a snippet needs a yes/no *at the moment of reuse*, with the
obligations it takes on. Existing scanners inventory your dependencies; they do
not answer "can this specific thing go here". And an LLM asked directly will
guess. This does not guess: unknown licenses and contested combinations fail to
UNKNOWN or REVIEW, never to a green light.

## Verdicts

| verdict | meaning | exit |
|---|---|---|
| `allowed` | no obligations worth naming | 0 |
| `allowed-with-obligations` | yes, but you must do X | 0 |
| `review` | plausibly fine; a human must decide | 2 |
| `disallowed` | not permitted as-is | 2 |
| `unknown` | license not recognised; fail safe | 2 |

Exit code carries the verdict so a script branches without parsing prose.

## Not legal advice

canreuse encodes a curated reading of well-established license rules (FSF/SPDX/OSI
classifications and the documented special cases). It is not a lawyer. Every
answer says so.

## Install

```bash
# not yet on PyPI; install from the repository:
pip install git+https://github.com/Llicklair/canreuse
```

## Licence

MIT
