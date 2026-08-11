# v2

The second version of my portfolio — [guilyx.github.io](https://guilyx.github.io).

It sits between [v1](https://github.com/guilyx/v1) and [v3](https://github.com/guilyx/v3),
and it is deliberately the smallest of the three.

## What it is

One page. Three files. No framework, no build step, no dependencies to install.

```
index.html      the whole site
css/style.css   hand-written, CSS custom properties, dark + light
js/main.js      ~100 lines: nav, scrollspy, filters, theme
favicon.svg
```

Open `index.html` in a browser and it works. Deploy by pushing — GitHub Pages
serves it as-is.

## Sections

About · Experience · Projects · Open Source · Writing · Education · Contact

## Where it sits between v1 and v3

|                | v1 (2020)                        | **v2**                     | v3 (2025)                                     |
| -------------- | -------------------------------- | -------------------------- | --------------------------------------------- |
| Stack          | Bootstrap + jQuery template      | **Plain HTML/CSS/JS**      | React + Vite + Tailwind + framer-motion + d3   |
| Build          | none                             | **none**                   | `tsc && vite build`                            |
| Dependencies   | 6 vendored libraries             | **0**                      | 30+ npm packages                               |
| Pages          | 9                                | **1**                      | 15 routes                                      |
| Assets         | 46 MB of GIFs                    | **~40 KB total**           | optimised images                               |
| Theme          | light, blue `#2c98f0`            | **dark + light toggle**    | dark, neon `#f72585` / `#4cc9f0`               |
| Colour source  | template defaults                | **`guilyx/branding`**      | its own                                        |

The left sidebar is v1's signature, kept and cleaned up.

## Brand

Colour and the mark come from [`guilyx/branding`](https://github.com/guilyx/branding),
which is the source of truth. If this repo drifts from it, this repo is wrong.

- **Dark** is *Ink & Iris* — `#0d0e12` ground, `#8b95f0` accent.
- **Light** is *Bone & Rust* — `#f5f3ee` ground, `#b0472b` accent. It is the
  runner-up palette documented in `brand/palette.md`, used here because it is
  the only light ground the brand defines; the iris accent falls to roughly
  2:1 on cream and darkening it would fork the palette.
- The accent is the only saturated value, and it is spent deliberately: mono
  keys, links, one active control per view, the mark, focus rings. No
  gradients.

The logo is the swarm mark — three agents holding a formation. It is inlined in
`index.html` rather than loaded through `<img>`, because `currentColor` does not
cross that boundary and the mark would render black.

Regenerate brand assets with the bundled skill; never hand-write the SVG:

```bash
cd .claude/skills/logo-variants/scripts
python3 build_mark.py --list
python3 build_mark.py --variant favicon --out ../../../../favicon.svg
python3 validate_mark.py ../../../../favicon.svg --tile
python3 test_validator.py          # 14 cases covering every documented misuse
```

## Notes

- Content is current as of late 2022.
- Ships dark by default, respects `prefers-color-scheme` on first visit, and
  remembers the choice in `localStorage`.
- Everything readable without JavaScript; the script only adds the nav toggle,
  scrollspy, project filters and the theme switch.
- Honours `prefers-reduced-motion`, has a skip link, visible focus rings and a
  print stylesheet.

## Licence

[MIT](LICENSE)
