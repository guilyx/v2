#!/usr/bin/env python3
"""Check an SVG against the rules in guilyx/branding brand/logo.md.

The rules in that document are mostly negative - no gradient, no fourth node,
no filled triangle, no container - which makes them easy to violate by accident
and hard to spot by eye at 20px. This turns them into a pass/fail.

    python3 validate_mark.py assets/logo/mark-accent.svg
    python3 validate_mark.py favicon.svg --tile        # ground tile is expected
    python3 validate_mark.py *.svg --quiet             # CI mode

Exit code is 0 when every file passes, 1 otherwise.
"""

import argparse
import colorsys
import re
import sys
import xml.etree.ElementTree as ET

from mark import (
    ALLOWED_FILLS, GRID, GROUND, LINK_OPACITY, LINK_PATH, LINK_STROKE_W,
    MIN_SIZE_PX, NODE_R, NODES, ROTATION_STEP_DEG, TILE_RX,
)

TOL = 0.01
HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
ROTATE_RE = re.compile(r"rotate\(\s*(-?[\d.]+)")
CONTAINERS = {"rect", "ellipse", "polygon"}


def tag(el):
    return el.tag.split("}")[-1]


def num(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def hue_of(hex_colour):
    """Hue in degrees, or None for greys - greys carry no hue to conflict."""
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    return None if sat < 0.12 else round(hue * 360)


class Check:
    def __init__(self, path, allow_tile=False):
        self.path = path
        self.allow_tile = allow_tile
        self.errors = []
        self.notes = []

    def fail(self, rule, detail):
        self.errors.append(f"{rule}: {detail}")

    def resolve(self, el, attr, default=None):
        """Read a presentation attribute, walking up for an inherited value.

        SVG lets fill/stroke/opacity sit on an ancestor <g>, and the shipped
        marks use both styles, so checking only the leaf element reports
        conforming files as broken.
        """
        node = el
        while node is not None:
            val = node.get(attr)
            if val:
                return val.strip()
            style = node.get("style") or ""
            m = re.search(rf"(?:^|;)\s*{re.escape(attr)}\s*:\s*([^;]+)", style)
            if m:
                return m.group(1).strip()
            node = self.parents.get(id(node))
        return default

    def run(self):
        try:
            root = ET.parse(self.path).getroot()
        except (ET.ParseError, OSError) as exc:
            self.fail("parse", str(exc))
            return self

        els = list(root.iter())
        self.parents = {id(child): parent for parent in els for child in parent}
        self._nodes(els)
        self._link(els, root)
        self._colour(root, els)
        self._containers(els)
        self._rotation(root, els)
        self._clear_space(root, els)
        return self

    # -- three solid nodes, exact geometry -------------------------------
    def _nodes(self, els):
        circles = [e for e in els if tag(e) == "circle"]
        if len(circles) != 3:
            self.fail("node count",
                      f"expected 3 nodes, found {len(circles)} - the mark is "
                      f"three agents; a fourth changes what it means")
            return

        found = sorted(((num(c.get("cx"), 0), num(c.get("cy"), 0), c)
                        for c in circles), key=lambda t: (t[1], t[0]))
        canon = sorted(NODES, key=lambda t: (t[1], t[0]))

        dx = found[0][0] - canon[0][0]
        dy = found[0][1] - canon[0][1]
        for (ax, ay, el), (cx, cy) in zip(found, canon):
            if abs(ax - (cx + dx)) > TOL or abs(ay - (cy + dy)) > TOL:
                self.fail("node geometry",
                          f"node at ({ax:g}, {ay:g}) is off the canonical "
                          f"triangle (expected ({cx + dx:g}, {cy + dy:g}))")
            r = num(el.get("r"))
            if r is None or abs(r - NODE_R) > TOL:
                self.fail("node radius", f"r={r}, expected {NODE_R}")
            stroke = self.resolve(el, "stroke", "none")
            if stroke != "none":
                self.fail("outlined node",
                          "nodes are solid; outlining them is listed as misuse")

    # -- link path, and it must stay weaker than the nodes ---------------
    def _link(self, els, root):
        paths = [e for e in els if tag(e) == "path"]
        width = num(root.get("width"))
        small = width is not None and width < MIN_SIZE_PX

        if not paths:
            if not small:
                self.fail("link path",
                          "no link path - only the sub-20px variant may drop it")
            else:
                self.notes.append(
                    f"link path dropped at {width:g}px, per the minimum-size rule")
            return

        if small:
            self.fail("minimum size",
                      f"width={width:g}px is below {MIN_SIZE_PX}px but the link "
                      f"path is still present; it muddies at this size")

        for p in paths:
            if " ".join(p.get("d", "").split()) != LINK_PATH:
                self.fail("link path", f'unexpected geometry: d="{p.get("d")}"')
            fill = self.resolve(p, "fill", "none")
            if fill != "none":
                self.fail("filled triangle",
                          "the formation is an outline; filling it is misuse")
            sw = num(self.resolve(p, "stroke-width"))
            if sw is None or abs(sw - LINK_STROKE_W) > TOL:
                self.fail("link weight", f"stroke-width={sw}, expected {LINK_STROKE_W}")
            op = num(self.resolve(p, "opacity"), 1.0)
            if abs(op - LINK_OPACITY) > TOL:
                self.fail("link opacity",
                          f"opacity={op}, expected {LINK_OPACITY} - the path is "
                          f"deliberately weaker than the nodes")

    # -- one hue, brand colours only, no gradients -----------------------
    def _colour(self, root, els):
        for el in els:
            if tag(el) in {"linearGradient", "radialGradient", "pattern"}:
                self.fail("gradient",
                          f"<{tag(el)}> present - the mark is never a gradient")

        raw = ET.tostring(root, encoding="unicode")
        if "url(#" in raw:
            self.fail("gradient", "a paint server is referenced via url(#...)")

        used = set()
        for el in els:
            for attr in ("fill", "stroke", "stop-color", "color"):
                val = (el.get(attr) or "").strip()
                if val:
                    used.add(val)
            style = el.get("style") or ""
            used.update(HEX_RE.findall(style))
            if el.text and tag(el) == "style":
                used.update(HEX_RE.findall(el.text))

        stray = {c for c in used if c not in ALLOWED_FILLS}
        if stray:
            self.fail("off-brand colour",
                      f"{', '.join(sorted(stray))} - the palette lives in "
                      f"tokens.json; if a project drifts, the brand repo wins")

        # The ground is excluded: it is a near-black with a few degrees of blue
        # left in it by design, and it paints the tile, not the mark. The rule
        # is about how many hues the mark itself carries.
        hues = {h for h in (hue_of(c) for c in used
                            if c.startswith("#") and c.lower() != GROUND)
                if h is not None}
        if len(hues) > 1:
            self.fail("multiple hues",
                      f"{len(hues)} hues present ({sorted(hues)}) - never more "
                      f"than one")

    # -- no container beyond the favicon tile ----------------------------
    def _containers(self, els):
        shapes = [e for e in els if tag(e) in CONTAINERS]
        if not shapes:
            return
        if not self.allow_tile:
            self.fail("container",
                      f"<{tag(shapes[0])}> wraps the mark - only the favicon "
                      f"tile may do that (pass --tile if this is the favicon)")
            return
        if len(shapes) > 1:
            self.fail("container", f"{len(shapes)} container shapes, expected 1")
        tile = shapes[0]
        if tag(tile) != "rect":
            self.fail("container", f"tile is <{tag(tile)}>, expected <rect>")
        rx = num(tile.get("rx"))
        if rx is None or abs(rx - TILE_RX) > TOL:
            self.fail("tile radius", f"rx={rx}, expected {TILE_RX}")
        if (tile.get("fill") or "").lower() != GROUND:
            self.fail("tile fill", f"{tile.get('fill')}, expected ground {GROUND}")

    # -- rotation only in multiples of 120 -------------------------------
    def _rotation(self, root, els):
        blob = ET.tostring(root, encoding="unicode")
        for angle in ROTATE_RE.findall(blob):
            deg = float(angle)
            if deg % ROTATION_STEP_DEG != 0:
                self.fail("rotation",
                          f"{deg:g} degrees - the mark is only rotationally "
                          f"symmetric every {ROTATION_STEP_DEG} degrees")

    # -- clear space of at least one node radius -------------------------
    def _clear_space(self, root, els):
        vb = (root.get("viewBox") or "").split()
        if len(vb) != 4:
            self.fail("viewBox", "missing or malformed")
            return
        _, _, vw, vh = (num(v, 0) for v in vb)

        circles = [(num(c.get("cx"), 0), num(c.get("cy"), 0))
                   for c in els if tag(c) == "circle"]
        if not circles:
            return

        # Translations on ancestor groups shift the drawn mark.
        tx = ty = 0.0
        for el in els:
            m = re.search(r"translate\(\s*(-?[\d.]+)[ ,]+(-?[\d.]+)",
                          el.get("transform") or "")
            if m:
                tx, ty = float(m.group(1)), float(m.group(2))

        left = min(x for x, _ in circles) + tx - NODE_R
        right = max(x for x, _ in circles) + tx + NODE_R
        top = min(y for _, y in circles) + ty - NODE_R
        bottom = max(y for _, y in circles) + ty + NODE_R

        edges = {"left": left, "top": top, "bottom": vh - bottom}
        if abs(vw - vh) < TOL:  # square box: no wordmark to the right
            edges["right"] = vw - right

        for name, gap in edges.items():
            if gap < NODE_R - TOL:
                self.fail("clear space",
                          f"{gap:.2f} on the {name}, needs at least {NODE_R}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--tile", action="store_true",
                    help="Expect the favicon/app-icon ground tile.")
    ap.add_argument("--quiet", action="store_true", help="Only report failures.")
    args = ap.parse_args()

    bad = 0
    for path in args.files:
        result = Check(path, allow_tile=args.tile).run()
        if result.errors:
            bad += 1
            print(f"FAIL {path}")
            for err in result.errors:
                print(f"     {err}")
        elif not args.quiet:
            print(f"ok   {path}")
            for note in result.notes:
                print(f"     {note}")

    if bad:
        print(f"\n{bad} of {len(args.files)} file(s) violate brand/logo.md",
              file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
