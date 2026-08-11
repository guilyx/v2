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

The accent colour, `#3cb1f0`, is the literal midpoint of v1's blue and v3's cyan.
v3's pink shows up only on active states — the earliest version of the palette
the later site would eventually commit to. The left sidebar is v1's signature,
kept and cleaned up.

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
