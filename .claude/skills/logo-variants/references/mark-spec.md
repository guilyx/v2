# Mark spec

Mirrored from [`guilyx/branding`](https://github.com/guilyx/branding):
`brand/logo.md` for geometry and rules, `tokens/tokens.json` for colour.
The machine-readable copy is `scripts/mark.py` — both scripts import it, so
this file is documentation and that file is the authority.

## Geometry

On a 32 × 32 grid:

| Element | Geometry |
| :--- | :--- |
| Apex node | centre `(16, 8.5)`, r `2.1` |
| Left node | centre `(8.5, 21)`, r `2.1` |
| Right node | centre `(23.5, 21)`, r `2.1` |
| Link path | `M16 8.5 L8.5 21 L23.5 21 Z`, stroke `1.1`, opacity `0.45`, fill `none` |
| Ground tile | `rect` 32 × 32, `rx` `6`, fill `#0d0e12` — favicon and app icons only |
| Centroid | `(16, 16.833)` — the rotation origin |

Draw order is link path first, nodes second, so the nodes sit on top. That is
not incidental: the mark says the agents are the subject and the formation is
what falls out of them, and stacking order is part of saying it.

### Known deviation: the triangle is not quite equilateral

`brand/logo.md` describes "an equilateral triangle", but the shipped
coordinates are not:

| Side | Length |
| :--- | ---: |
| left → right | 15.000 |
| apex → left | 14.577 |
| apex → right | 14.577 |

The mark is about 2.8% squatter than a true equilateral. A correct equilateral
on the same 15-unit base would put the apex at `y ≈ 8.01` rather than `8.5`.

**Keep the shipped coordinates.** They are what renders on every surface that
already carries the mark, and the difference is invisible at every size the
mark is used at. "Correcting" the geometry toward the prose would silently
change the live logo and desynchronise every generated asset from the ones
already deployed — a much worse outcome than a slightly loose word in the
documentation.

If it is ever worth reconciling, that is an upstream decision: fix the wording
in `brand/logo.md` (cheap, no visual change) rather than the coordinates
(expensive, changes everything).

## Colour

From `tokens/tokens.json`:

| Role | Token | Value |
| :--- | :--- | :--- |
| Accent | `--color-accent` | `#8b95f0` |
| Ground | `--color-bg` | `#0d0e12` |

`currentColor` and `none` are also permitted. Nothing else is — the accent is
the only saturated value the system has.

The ground is excluded from the "one hue" count on purpose. It is a near-black
with a few degrees of blue left in it by design, so it reads as ink rather than
navy, and a naive hue count sees that residue as a second hue. It paints the
tile, not the mark.

## Rules with a number attached

| Rule | Value | Consequence if broken |
| :--- | :--- | :--- |
| Minimum size with link path | 20px | Stroke muddies into the nodes; use the `small` variant |
| Clear space | ≥ 1 node radius (2.1) | Mark crowds whatever it sits next to |
| Rotation interval | 120° | Any other angle does not land back on itself |
| Link opacity | 0.45 | Formation stops reading as secondary |
| Link stroke | 1.1 | Same |

## Wordmark

`guilyx` — lowercase, always, in the mono face (JetBrains Mono, 400), falling
back to `ui-monospace`. The lowercase is not a stylisation; it is how the handle
is written everywhere else.

The full name **Erwin Lejeune** is set in the display face (Space Grotesk) and
is *not* part of the mark. It is typography, and it changes size and weight
with context — which is why `build_mark.py` never emits it.

## Documented misuse

From `brand/logo.md`, all enforced by `validate_mark.py`:

- a fourth node
- filling the triangle
- outlining the nodes
- a gradient, or more than one hue
- placing the mark on a busy photo *(not machine-checkable — reviewer's job)*
- setting it in a circle or rounded square other than the favicon tile

A monogram in a hexagon was tried before this mark and rejected: it did not
survive being small. That history is why "make it a fancy monogram" is not an
open question.
