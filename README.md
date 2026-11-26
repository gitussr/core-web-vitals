# CWV — The 100/100 Handbook

**How to score 100 on PageSpeed Insights with WordPress.**

A Core Web Vitals and Lighthouse field guide: how PageSpeed Insights awards its points in
Performance, Accessibility, Best Practices and SEO, the hidden criteria that quietly cost points,
and the decisions to make from the first line of HTML — long before the site becomes a WordPress theme.

**Live site:** https://gitussr.github.io/core-web-vitals/

The handbook practises what it preaches: every page is a single static HTML file with inline CSS,
a few KB of JavaScript, system fonts, inline SVG icons and no third parties.

| Tested on PageSpeed Insights (26 Nov 2026) | Performance | Accessibility | Best Practices | SEO |
|---|:-:|:-:|:-:|:-:|
| Mobile | 100 | 100 | 100 | 100 |
| Desktop | 100 | 100 | 100 | 100 |

*Tested pages: home, Performance scoring, Converting to WordPress, Launch checklist.*

---

## Contents

**Understand the score**

| Page | What it covers |
|---|---|
| [What “100” really means](https://gitussr.github.io/core-web-vitals/) | Field data (CrUX) vs. lab data (Lighthouse) |
| [Performance scoring](https://gitussr.github.io/core-web-vitals/lighthouse-performance-score/) | Metric weights, log-normal curves, mobile/desktop thresholds |
| [Core Web Vitals](https://gitussr.github.io/core-web-vitals/core-web-vitals/) | LCP, INP, CLS thresholds, LCP sub-parts, why FID was retired |
| [Accessibility scoring](https://gitussr.github.io/core-web-vitals/accessibility-score/) | axe-core weighting and the audits WordPress sites fail |
| [Best Practices scoring](https://gitussr.github.io/core-web-vitals/best-practices-score/) | Every scored audit and how to fix it |
| [SEO scoring](https://gitussr.github.io/core-web-vitals/seo-score/) | Indexability, metadata, link text, canonical, hreflang |
| [Hidden criteria](https://gitussr.github.io/core-web-vitals/hidden-criteria/) | 17 things that cost points on sites that “did everything right” |

**Build it right**

| Page | What it covers |
|---|---|
| [0 · Plan & budgets](https://gitussr.github.io/core-web-vitals/performance-budgets/) | Size/request budgets and design decisions |
| [1 · HTML foundations](https://gitussr.github.io/core-web-vitals/html-best-practices/) | Head order, LCP hero markup, semantic skeleton |
| [2 · CSS](https://gitussr.github.io/core-web-vitals/css-performance/) | Critical CSS, reserved space, font fallbacks |
| [3 · JavaScript](https://gitussr.github.io/core-web-vitals/javascript-performance/) | TBT/INP, deferring third parties, facades |
| [4 · Images, fonts, media](https://gitussr.github.io/core-web-vitals/image-font-optimization/) | Formats, `srcset`, lazy-loading rules |
| [5 · Converting to WordPress](https://gitussr.github.io/core-web-vitals/wordpress-optimization/) | Enqueueing, removing core bloat, plugin discipline |
| [6 · Hosting & server](https://gitussr.github.io/core-web-vitals/wordpress-hosting-caching/) | Page cache, CDN, compression, headers |
| [7 · Testing & monitoring](https://gitussr.github.io/core-web-vitals/testing-monitoring/) | DevTools, PSI, Lighthouse CI, Search Console, RUM |
| [Launch checklist](https://gitussr.github.io/core-web-vitals/launch-checklist/) | 33 items, progress saved in the browser |

Official reference: [Understanding Core Web Vitals and Google search results](https://developers.google.com/search/docs/appearance/core-web-vitals) — Google Search Central.

---

## Project structure

```
.
├── _src/
│   └── handbook.html      # The single editable source (all chapters, CSS, icons)
├── build.py               # Splits the source into one page per chapter + sitemap
├── index.html             # Generated: home page
├── <chapter-slug>/
│   └── index.html         # Generated: one folder per chapter (clean URLs)
├── sitemap.xml            # Generated
├── manifest.webmanifest   # Generated: PWA manifest
├── sw.js                  # Generated: offline service worker
├── icons/                 # App icons (any, maskable, Apple touch)
├── _config.yml            # Keeps build files out of GitHub Pages
├── LICENSE
└── README.md
```

Folders starting with `_` are not published by GitHub Pages, so the source never appears as duplicate content.

## Editing

1. Edit `_src/handbook.html` (each chapter is a `<section class="doc" id="…">`).
2. Regenerate the site:

   ```bash
   python build.py
   ```

3. Commit and push — GitHub Pages deploys from the `main` branch root.

Page titles, meta descriptions and URL slugs live in the `PAGES` list at the top of `build.py`.
The build checks that titles stay within 60 characters and descriptions within 160.

Requirements: Python 3.8+ (standard library only).

## How the 100s are kept

- **Small pages.** The handbook started as one 4,000-element page and scored 83–95 on mobile —
  layout of that much text is one long main-thread task. One chapter per page fixed it.
- **No render-blocking requests.** CSS is inlined; JavaScript is at the end of `<body>`.
- **No web fonts.** SF Pro on Apple devices, Segoe UI on Windows, Roboto on Android.
- **No layout shift.** Sidebar state is restored before first paint; tables are labelled at build time.
- **CSS-only hero animation**, disabled for `prefers-reduced-motion` and print.
- **Accessible by default.** AA contrast, skip link, landmarks, sequential headings, keyboard-operable
  sidebar, tabs and checklist.
- **SEO.** Unique titles and descriptions, canonical URLs, Open Graph tags, `TechArticle` and
  `BreadcrumbList` structured data, and a sitemap.

Scores vary between runs; always confirm with [PageSpeed Insights](https://pagespeed.web.dev/)
rather than a single local Lighthouse run.

## Installable app (PWA)

The handbook is a Progressive Web App:

- **Install it** from the **Install** button in the toolbar (Chrome/Edge), the install icon in the
  address bar, or *Share → Add to Home Screen* on iPhone/iPad. It opens in its own window.
- **Works offline.** After the first visit, the service worker caches all 16 pages, so the whole
  handbook can be read without a connection.
- **Always fresh online.** Pages are fetched network-first; the cached copy is only used offline.
  Every `python build.py` changes the cache version, so old copies are replaced automatically.
- **App shortcuts** (right-click / long-press the app icon): Launch checklist, Hidden criteria,
  Performance scoring.

`manifest.webmanifest` and `sw.js` are generated by `build.py`; icons live in `icons/`.
The service worker registers after the `load` event, so it never competes with first paint.

## Design

Styled after Apple’s macOS Human Interface Guidelines (light appearance): unified toolbar,
collapsible source-list sidebar with an icon rail, grouped inset lists, segmented controls and
disclosure rows. Includes a print stylesheet (A4, page numbers, expanded disclosures).

## Disclaimer

Scoring details reflect Lighthouse 12–13 as used by PageSpeed Insights in late 2026. Google adjusts
weights, curves and audits between major versions. This project is not affiliated with Google,
Apple or WordPress.

## License

[MIT](LICENSE) © 2026 gitussr
