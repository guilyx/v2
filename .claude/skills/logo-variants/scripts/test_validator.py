#!/usr/bin/env python3
"""Prove validate_mark.py actually rejects each documented misuse.

A checker that passes everything is worse than no checker, because it buys
false confidence. Each case below breaks exactly one rule from brand/logo.md
and asserts the matching failure is raised - and that a conforming file still
passes, so the rules are not simply rejecting everything.

    python3 test_validator.py
"""

import os
import sys
import tempfile

from validate_mark import Check

GOOD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <path d="M16 8.5 L8.5 21 L23.5 21 Z" fill="none" stroke="#8b95f0" stroke-width="1.1" opacity="0.45"/>
  <g fill="#8b95f0">
    <circle cx="16" cy="8.5" r="2.1"/>
    <circle cx="8.5" cy="21" r="2.1"/>
    <circle cx="23.5" cy="21" r="2.1"/>
  </g>
</svg>"""

# Inherited-attribute style: same mark, attributes hoisted onto the groups.
GOOD_INHERITED = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <g stroke="#8b95f0" stroke-width="1.1" opacity="0.45" fill="none">
    <path d="M16 8.5 L8.5 21 L23.5 21 Z"/>
  </g>
  <g fill="#8b95f0">
    <circle cx="16" cy="8.5" r="2.1"/>
    <circle cx="8.5" cy="21" r="2.1"/>
    <circle cx="23.5" cy="21" r="2.1"/>
  </g>
</svg>"""

FOURTH_NODE = GOOD.replace(
    '<circle cx="23.5" cy="21" r="2.1"/>',
    '<circle cx="23.5" cy="21" r="2.1"/>\n    <circle cx="16" cy="16" r="2.1"/>')

MOVED_NODE = GOOD.replace('cx="8.5" cy="21"', 'cx="7" cy="22"')
FAT_NODE = GOOD.replace('cx="16" cy="8.5" r="2.1"', 'cx="16" cy="8.5" r="3.4"')
OUTLINED = GOOD.replace('<g fill="#8b95f0">',
                        '<g fill="#8b95f0" stroke="#8b95f0">')
FILLED_TRIANGLE = GOOD.replace('d="M16 8.5 L8.5 21 L23.5 21 Z" fill="none"',
                               'd="M16 8.5 L8.5 21 L23.5 21 Z" fill="#8b95f0"')
LOUD_LINK = GOOD.replace('opacity="0.45"', 'opacity="1"')
OFF_BRAND = GOOD.replace("#8b95f0", "#3cb1f0")
BAD_ROTATION = GOOD.replace('<g fill="#8b95f0">',
                            '<g fill="#8b95f0" transform="rotate(45 16 16.83)">')
CONTAINED = GOOD.replace(
    "<path", '<rect width="32" height="32" rx="16" fill="#15171d"/>\n  <path')

GRADIENT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <defs><linearGradient id="g"><stop stop-color="#8b95f0"/><stop offset="1" stop-color="#f72585"/></linearGradient></defs>
  <path d="M16 8.5 L8.5 21 L23.5 21 Z" fill="none" stroke="url(#g)" stroke-width="1.1" opacity="0.45"/>
  <g fill="url(#g)">
    <circle cx="16" cy="8.5" r="2.1"/>
    <circle cx="8.5" cy="21" r="2.1"/>
    <circle cx="23.5" cy="21" r="2.1"/>
  </g>
</svg>"""

TOO_SMALL_WITH_PATH = GOOD.replace('width="32" height="32"', 'width="14" height="14"')

CRAMPED = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 26 26" width="26" height="26">
  <path d="M16 8.5 L8.5 21 L23.5 21 Z" fill="none" stroke="#8b95f0" stroke-width="1.1" opacity="0.45"/>
  <g fill="#8b95f0">
    <circle cx="16" cy="8.5" r="2.1"/>
    <circle cx="8.5" cy="21" r="2.1"/>
    <circle cx="23.5" cy="21" r="2.1"/>
  </g>
</svg>"""

# (name, svg, allow_tile, expected substring in a failure - None means must pass)
CASES = [
    ("conforming mark",            GOOD,                False, None),
    ("conforming, inherited attrs", GOOD_INHERITED,     False, None),
    ("fourth node",                FOURTH_NODE,         False, "node count"),
    ("node off the triangle",      MOVED_NODE,          False, "node geometry"),
    ("oversized node",             FAT_NODE,            False, "node radius"),
    ("outlined nodes",             OUTLINED,            False, "outlined node"),
    ("filled triangle",            FILLED_TRIANGLE,     False, "filled triangle"),
    ("link as loud as nodes",      LOUD_LINK,           False, "link opacity"),
    ("off-brand accent",           OFF_BRAND,           False, "off-brand colour"),
    ("rotation off the 120 grid",  BAD_ROTATION,        False, "rotation"),
    ("container shape",            CONTAINED,           False, "container"),
    ("gradient",                   GRADIENT,            False, "gradient"),
    ("link path below 20px",       TOO_SMALL_WITH_PATH, False, "minimum size"),
    ("no clear space",             CRAMPED,             False, "clear space"),
]


def main():
    passed = failed = 0
    for name, body, tile, expect in CASES:
        with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as fh:
            fh.write(body)
            path = fh.name
        try:
            errors = Check(path, allow_tile=tile).run().errors
        finally:
            os.unlink(path)

        joined = " | ".join(errors)
        if expect is None:
            ok = not errors
            detail = "" if ok else f"unexpected: {joined}"
        else:
            ok = any(expect in e for e in errors)
            detail = "" if ok else f"expected {expect!r}, got: {joined or 'no errors'}"

        print(f"{'PASS' if ok else 'FAIL'}  {name}{'  -> ' + detail if detail else ''}")
        passed, failed = (passed + ok, failed + (not ok))

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
