#!/usr/bin/env python3
"""Emit a brand-conformant version of the guilyx swarm mark.

Every variant is drawn from the same constants in mark.py, so the nodes land
on identical coordinates whether the output is a 20px favicon or a 512px app
icon. That is the whole point: hand-written copies of the mark drift a
half-pixel at a time until the small sizes stop lining up.

    python3 build_mark.py --variant favicon --out favicon.svg
    python3 build_mark.py --list

Validate whatever comes out:

    python3 validate_mark.py favicon.svg --tile
"""

import argparse
import sys

from mark import (
    ACCENT, GRID, GROUND, LINK_OPACITY, LINK_PATH, LINK_STROKE_W,
    MONO_STACK, NODE_R, NODES, TILE_RX, WORDMARK, mark_bbox,
)

SWIFT = "cubic-bezier(0.645, 0.045, 0.355, 1)"  # tokens.json -> easing.swift


def n(value):
    """Trim trailing zeros so the SVG reads like the hand-written originals."""
    text = f"{float(value):.4f}".rstrip("0").rstrip(".")
    return text or "0"


def nodes_svg(colour, indent="  "):
    circles = "\n".join(
        f'{indent}  <circle cx="{n(x)}" cy="{n(y)}" r="{n(NODE_R)}"/>'
        for x, y in NODES
    )
    return f'{indent}<g fill="{colour}">\n{circles}\n{indent}</g>'


def link_svg(colour, indent="  "):
    return (
        f'{indent}<path d="{LINK_PATH}" fill="none" stroke="{colour}" '
        f'stroke-width="{n(LINK_STROKE_W)}" opacity="{n(LINK_OPACITY)}"/>'
    )


def tile_svg(size=GRID, indent="  "):
    return (
        f'{indent}<rect width="{n(size)}" height="{n(size)}" '
        f'rx="{n(TILE_RX)}" fill="{GROUND}"/>'
    )


def svg(view_w, view_h, width, height, body, label="guilyx swarm mark"):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {n(view_w)} {n(view_h)}" '
        f'width="{n(width)}" height="{n(height)}" '
        f'role="img" aria-label="{label}">\n{body}\n</svg>\n'
    )


# --- variants -------------------------------------------------------------
#
# The link path is drawn before the nodes so the nodes sit on top. brand/logo.md
# is explicit that the agents are the subject and the formation is the
# consequence, and stacking order is part of saying that.


def v_accent(size):
    body = f"{link_svg(ACCENT)}\n{nodes_svg(ACCENT)}"
    return svg(GRID, GRID, size, size, body)


def v_mono(size):
    body = f'{link_svg("currentColor")}\n{nodes_svg("currentColor")}'
    return svg(GRID, GRID, size, size, body)


def v_small(size):
    """No link path. Below ~20px the stroke muddies into the nodes.

    brand/logo.md calls for exactly this instead of shrinking the full mark,
    but never shipped the file. Three dots still read as a formation.
    """
    return svg(GRID, GRID, size, size, nodes_svg("currentColor"))


def v_favicon(size):
    body = f"{tile_svg()}\n{link_svg(ACCENT)}\n{nodes_svg(ACCENT)}"
    return svg(GRID, GRID, size, size, body, label=WORDMARK)


def v_app_icon(size):
    """Same tile as the favicon, sized for apple-touch-icon / PWA manifests."""
    return v_favicon(size)


def v_lockup(size):
    scale = size / GRID
    body = (
        f'{link_svg("currentColor")}\n{nodes_svg("currentColor")}\n'
        f'  <text x="40" y="21" fill="currentColor" font-family="{MONO_STACK}" '
        f'font-size="14" letter-spacing="0.02em">{WORDMARK}</text>'
    )
    return svg(140, GRID, 140 * scale, size, body, label=WORDMARK)


def v_lockup_stacked(size):
    """Vertical lockup for narrow contexts - sidebars, cards, stamps."""
    scale = size / GRID
    dx = (64 - GRID) / 2  # centre the 32-wide mark in a 64-wide box
    body = (
        f'  <g transform="translate({n(dx)} 0)">\n'
        f'{link_svg("currentColor", indent="    ")}\n'
        f'{nodes_svg("currentColor", indent="    ")}\n'
        f"  </g>\n"
        f'  <text x="32" y="40" fill="currentColor" font-family="{MONO_STACK}" '
        f'font-size="12" letter-spacing="0.02em" text-anchor="middle">{WORDMARK}</text>'
    )
    return svg(64, 46, 64 * scale, 46 * scale, body, label=WORDMARK)


def v_animated(size):
    """The 120-degree turn brand/logo.md says the nav uses, as a standalone file.

    Rotation is about the centroid, not the box centre, which is what makes the
    mark land back on itself rather than wobble.
    """
    cx = sum(x for x, _ in NODES) / 3
    cy = sum(y for _, y in NODES) / 3
    style = (
        "  <style>\n"
        f"    .swarm {{ transform-origin: {n(cx)}px {n(cy)}px; "
        f"transition: transform .5s {SWIFT}; }}\n"
        "    svg:hover .swarm { transform: rotate(120deg); }\n"
        "    @media (prefers-reduced-motion: reduce) {\n"
        "      .swarm { transition: none; }\n"
        "      svg:hover .swarm { transform: none; }\n"
        "    }\n"
        "  </style>"
    )
    body = (
        f"{style}\n"
        f'  <g class="swarm">\n'
        f'{link_svg("currentColor", indent="    ")}\n'
        f'{nodes_svg("currentColor", indent="    ")}\n'
        f"  </g>"
    )
    return svg(GRID, GRID, size, size, body)


VARIANTS = {
    "accent": (v_accent, 32, "Accent nodes on transparent ground. The default."),
    "mono": (v_mono, 32, "currentColor - inherits from context. Nav bars, buttons."),
    "small": (v_small, 16, "Link path removed, for use below 20px."),
    "favicon": (v_favicon, 32, "Ground tile plus accent mark. Browser tabs."),
    "app-icon": (v_app_icon, 180, "Favicon tile at apple-touch / PWA sizes."),
    "lockup": (v_lockup, 32, "Mark plus guilyx wordmark, horizontal."),
    "lockup-stacked": (v_lockup_stacked, 32, "Mark above the wordmark, centred."),
    "animated": (v_animated, 32, "Mono mark with the 120-degree hover turn."),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", choices=sorted(VARIANTS))
    ap.add_argument("--size", type=float, help="Rendered px. Defaults per variant.")
    ap.add_argument("--out", help="Write here instead of stdout.")
    ap.add_argument("--list", action="store_true", help="Show the catalogue and exit.")
    args = ap.parse_args()

    if args.list:
        width = max(len(k) for k in VARIANTS)
        for name in sorted(VARIANTS):
            fn, default, blurb = VARIANTS[name]
            print(f"{name:<{width}}  {default:>4}px  {blurb}")
        return 0

    if not args.variant:
        ap.error("--variant is required (or --list)")

    fn, default, _ = VARIANTS[args.variant]
    out = fn(args.size or default)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
