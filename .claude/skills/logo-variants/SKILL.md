---
name: logo-variants
description: Generate and validate brand-conformant versions of the guilyx swarm mark — favicons, app icons, wordmark lockups, sub-20px and animated variants. Use this skill whenever the user asks for a logo, mark, favicon, app icon, wordmark, lockup, or brand asset for guilyx / Erwin Lejeune / elejeune.me, or asks whether an existing logo file follows the brand rules. Also reach for it before hand-writing any SVG that contains the mark: the geometry is exact, and brand/logo.md forbids gradients, extra nodes, filled triangles, outlined nodes and containers other than the favicon tile, so hand-drawn copies drift within a few pixels.
---

# Logo variants

The mark is three filled circles at the vertices of a triangle, joined by a
faint outline. Three agents holding a formation — the smallest possible drawing
of a decentralized swarm, where no node is in charge and the shape falls out of
local rules.

One idea carries the whole thing: **the nodes are the subject, the formation is
the consequence.** That is why the link path is drawn at 0.45 opacity behind
solid nodes. Every rule below is downstream of it, and a variant that inverts
the relationship — a bold triangle with faint dots — is no longer this mark.

The mark is settled. This skill makes *versions* of it. It is not for
redesigning it; see [When a request needs a rule broken](#when-a-request-needs-a-rule-broken).

## Do this first

Never hand-write an SVG containing the mark. The node coordinates carry one
decimal place and the sizes that matter most (16–32px) are exactly where a
half-pixel drift becomes visible. Build it, then check it:

```bash
cd scripts
python3 build_mark.py --list                              # the catalogue
python3 build_mark.py --variant favicon --out favicon.svg
python3 validate_mark.py favicon.svg --tile               # must print "ok"
```

`validate_mark.py` exits non-zero on any violation, so it drops straight into a
pre-commit hook or CI. Point it at files you did not generate too — it is the
fastest way to answer "is this logo on-brand?"

```bash
python3 validate_mark.py path/to/*.svg          # audit a folder
python3 test_validator.py                       # 14 cases: the checker still bites
```

## The catalogue

| Variant | Default | Use |
| :--- | ---: | :--- |
| `accent` | 32px | Accent nodes, transparent ground. The default mark. |
| `mono` | 32px | `currentColor` — inherits from context. Nav bars, buttons, footers. |
| `small` | 16px | Link path removed. The only correct way to go below 20px. |
| `favicon` | 32px | Ground tile plus accent mark. Browser tabs. |
| `app-icon` | 180px | The favicon tile at apple-touch / PWA sizes. |
| `lockup` | 32px | Mark plus the `guilyx` wordmark, horizontal. |
| `lockup-stacked` | 32px | Mark above the wordmark, centred. Narrow columns, cards. |
| `animated` | 32px | Mono mark with the 120° hover turn, honouring reduced-motion. |

`--size` overrides the default on any of them; geometry is defined in viewBox
units, so scaling never moves a node.

**Reach for `mono` more often than `accent`.** Because it inherits
`currentColor`, one file serves dark UI, light UI, hover states and print, and
it can never disagree with the surrounding text colour. Use `accent` only where
the mark stands alone with nothing to inherit from.

**`mono` must be inlined in the page, not loaded through `<img>` or
`background-image`.** An SVG referenced that way is an isolated document, so
`currentColor` resolves against *its* default — black — instead of the
surrounding text. It fails silently: the mark renders, just in the wrong
colour, and on a dark ground it disappears. If a build step forces `<img>`,
use `accent` there and accept the fixed colour.

**There is no on-light colour variant, deliberately.** The iris accent
(`#8b95f0`) is a light periwinkle and drops to roughly 2:1 against a cream
ground — unreadable. The fix is `mono` with `color` set from context, not a new
colour token: inventing one would fork the palette, and the brand repo is meant
to win those arguments.

## The rules, and why they exist

`validate_mark.py` enforces all of these. The reasoning matters more than the
list, because it tells you what to do when a request falls between the cases.

- **Exactly three nodes, on the canonical coordinates.** Three is the minimum
  count where "formation" means anything. A fourth node makes it a pattern.
- **Nodes solid, never outlined. Triangle never filled.** Both invert the
  subject/consequence relationship.
- **Link path at 0.45 opacity, 1.1 stroke.** Weaker than the nodes, always.
- **One hue, no gradients.** The accent is the only saturated value the system
  has, and it is spent deliberately. A gradient spends two.
- **Brand colours only** — `#8b95f0`, `#0d0e12`, or `currentColor`. If a
  project's colours drift from the brand repo, the brand repo wins.
- **No container** beyond the favicon/app-icon ground tile (`rect`, `rx=6`).
  Pass `--tile` when validating those; without it a wrapping shape is an error.
- **Rotation only in multiples of 120°**, about the centroid — the mark is
  rotationally symmetric at that interval, so it lands back on itself.
- **Below 20px, drop the link path** rather than shrinking the full mark. The
  stroke muddies into the nodes and the whole thing turns to soup.
- **Clear space of at least one node radius** on every side.

Full geometry table, the colour tokens, and a known deviation between the
documented construction and the shipped files are in
[`references/mark-spec.md`](references/mark-spec.md). Read it if you are adding
a variant to `build_mark.py` or reconciling this skill with an upstream change.

## Adding a variant

Add a `v_*` function to `build_mark.py` and register it in `VARIANTS`. Compose
from `nodes_svg()`, `link_svg()` and `tile_svg()` rather than writing paths —
they read the same constants the validator checks against, so anything built
from them conforms by construction. Then add a case to `test_validator.py` if
the variant exercises a rule that is not covered yet.

## When a request needs a rule broken

Someone will eventually want the mark in two colours, or in a circle, or with a
fourth node for a four-person team. The rules are not arbitrary — each one is
recorded in `brand/logo.md` with its reasoning, and one of them (the monogram)
is there because it was tried and failed.

Do not quietly comply, and do not quietly refuse. Say which rule the request
breaks and why the rule exists, then offer the nearest conforming thing — a
lockup instead of a second colour, the favicon tile instead of a circle, the
`small` variant instead of a shrunken full mark. If the user confirms they want
the exception anyway, that is their call: build it, but leave it out of the
brand repo's `assets/logo/` and say plainly that it will not pass validation.

Changing the mark itself is a different job from this skill. It means a new
entry in `brand/logo.md` with the rationale, regenerated assets everywhere the
old mark shipped, and an update to the constants in `scripts/mark.py`.

## Source of truth

Geometry and colour are mirrored from
[`guilyx/branding`](https://github.com/guilyx/branding) — `brand/logo.md` and
`tokens/tokens.json`. The mirror lives in one place, `scripts/mark.py`, which
both scripts import, so a generated file and the checker that judges it cannot
drift apart. If the upstream brand changes, edit `scripts/mark.py` and rerun
`test_validator.py`.
