"""Canonical geometry and colour for the guilyx swarm mark.

Single source of truth for both build_mark.py and validate_mark.py, so a
generated file and the checker that judges it can never disagree.

Mirrors guilyx/branding: brand/logo.md (geometry) and tokens/tokens.json
(colour). If either changes upstream, change it here.
"""

# --- geometry, on the 32x32 grid defined in brand/logo.md ---

GRID = 32.0

NODES = (
    (16.0, 8.5),   # apex
    (8.5, 21.0),   # left
    (23.5, 21.0),  # right
)
NODE_R = 2.1

LINK_PATH = "M16 8.5 L8.5 21 L23.5 21 Z"
LINK_STROKE_W = 1.1
LINK_OPACITY = 0.45

TILE_RX = 6.0  # favicon / app-icon ground tile corner radius

# --- colour, from tokens/tokens.json ---

ACCENT = "#8b95f0"
GROUND = "#0d0e12"

# Colours a mark file is allowed to reference. Anything else is drift.
ALLOWED_FILLS = {ACCENT, GROUND, "currentColor", "none"}

# --- rules that carry a number, from brand/logo.md ---

MIN_SIZE_PX = 20          # below this the link path muddies; drop it instead
ROTATION_STEP_DEG = 120   # the mark is rotationally symmetric at this interval

WORDMARK = "guilyx"       # lowercase, always
MONO_STACK = "ui-monospace, 'JetBrains Mono', 'SF Mono', monospace"


def mark_bbox():
    """(min_x, min_y, max_x, max_y) of the drawn mark, nodes included."""
    xs = [x for x, _ in NODES]
    ys = [y for _, y in NODES]
    return (
        min(xs) - NODE_R,
        min(ys) - NODE_R,
        max(xs) + NODE_R,
        max(ys) + NODE_R,
    )
