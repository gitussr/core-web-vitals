#!/usr/bin/env python3
"""Build the multi-page handbook from _src/handbook.html.

One long page scored 83 on mobile Lighthouse (layout of ~4,000 elements is a
single long task), so every topic gets its own small, fast, indexable URL.

    python build.py        # writes index.html, <slug>/index.html, sitemap.xml
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "_src" / "handbook.html"
SITE = "https://gitussr.github.io/core-web-vitals/"
MODIFIED = "2026-11-26"

# id in source, slug, <title> (<= 60 chars), meta description (<= 155 chars), group
PAGES = [
    ("performance", "lighthouse-performance-score",
     "Lighthouse Performance Score: Weights, Curves & Thresholds",
     "How Lighthouse turns FCP, Speed Index, LCP, TBT and CLS into a 0–100 Performance score, with mobile and desktop thresholds for a perfect 100.",
     "Understand the score"),
    ("cwv", "core-web-vitals",
     "Core Web Vitals Explained: LCP, INP and CLS Thresholds",
     "What the Core Web Vitals assessment in PageSpeed Insights measures, the good/poor thresholds for LCP, INP and CLS, and why FID was retired.",
     "Understand the score"),
    ("accessibility", "accessibility-score",
     "Lighthouse Accessibility Score: How to Reach 100",
     "How the Lighthouse Accessibility score is weighted, and the axe-core audits that most often break WordPress sites — names, contrast, ARIA, structure.",
     "Understand the score"),
    ("best-practices", "best-practices-score",
     "Lighthouse Best Practices Score: Every Audit Explained",
     "Every scored Lighthouse Best Practices audit, how WordPress sites fail it — console errors, third-party cookies, image resolution — and how to fix it.",
     "Understand the score"),
    ("seo", "seo-score",
     "Lighthouse SEO Score: The Audits That Decide Your 100",
     "The technical checks behind the Lighthouse SEO score: indexability, titles, descriptions, link text, crawlable links, robots.txt, canonical and hreflang.",
     "Understand the score"),
    ("hidden", "hidden-criteria",
     "17 Hidden PageSpeed Insights Criteria That Cost Points",
     "The criteria that quietly cost PageSpeed points on sites that did everything right: mobile throttling, LCP discovery, embeds, noindex, long pages.",
     "Understand the score"),
    ("budgets", "performance-budgets",
     "Performance Budgets for a 100 PageSpeed Score",
     "Size and request budgets for HTML, CSS, JavaScript, images and fonts that make a mobile 100 achievable — and the design choices that make it impossible.",
     "Build it right"),
    ("html", "html-best-practices",
     "HTML Best Practices for Core Web Vitals and SEO",
     "The head order, LCP hero markup and semantic skeleton to write from the first line of HTML so the finished WordPress theme scores 100.",
     "Build it right"),
    ("css", "css-performance",
     "CSS Performance: Critical CSS, Fonts and Zero CLS",
     "Critical CSS, reserved space, compositor-only animations and metric-matched font fallbacks: CSS rules for fast LCP and zero layout shift.",
     "Build it right"),
    ("js", "javascript-performance",
     "JavaScript Performance: Reduce TBT and INP",
     "Keep Total Blocking Time and INP low: deferred scripts, delayed third parties, facades for embeds and the JavaScript patterns to avoid.",
     "Build it right"),
    ("media", "image-font-optimization",
     "Image and Font Optimization for LCP and CLS",
     "Formats, sizes, srcset and lazy-loading rules for images, plus self-hosted font setup, so media never costs you LCP or CLS points.",
     "Build it right"),
    ("wordpress", "wordpress-optimization",
     "Convert HTML to a Fast WordPress Theme (100/100)",
     "Turn a static HTML build into a WordPress theme without losing scores: enqueueing, removing core bloat, image functions and plugin discipline.",
     "Build it right"),
    ("hosting", "wordpress-hosting-caching",
     "WordPress Hosting, Caching and Headers for Fast TTFB",
     "Full-page caching, CDN, compression, cache lifetimes and security headers that keep WordPress TTFB under 200 ms and Best Practices at 100.",
     "Build it right"),
    ("testing", "testing-monitoring",
     "Lighthouse CI and Core Web Vitals Monitoring",
     "The tools to test and monitor Core Web Vitals continuously — DevTools, PageSpeed Insights, Lighthouse CI budgets, Search Console and RUM.",
     "Build it right"),
    ("checklist", "launch-checklist",
     "WordPress Core Web Vitals Launch Checklist",
     "A 33-item launch checklist for Performance, Accessibility, Best Practices and SEO to ship a WordPress site that scores 100 on PageSpeed Insights.",
     "Build it right"),
]

AUTHOR = {"@type": "Person", "name": "Chiranjit Karmakar", "url": "https://www.chiranjitkarmakar.com/"}

HOME_TITLE = "WordPress Core Web Vitals: Score 100 on PageSpeed Insights"
HOME_DESC = ("Learn how PageSpeed Insights scores Performance, Accessibility, Best Practices "
             "and SEO, the hidden criteria, and how to build a WordPress site that scores 100.")
HOME_H1 = "How to score 100 on PageSpeed Insights with WordPress"


def must(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags)
    if not m:
        raise SystemExit(f"pattern not found: {pattern[:60]}")
    return m


src = SRC.read_text(encoding="utf-8")

style = must(r"<style>.*?</style>", src).group(0)
favicon = must(r'<link rel="icon"[^>]*>', src).group(0)
sprite = must(r'<svg width="0" height="0".*?</svg>', src).group(0)
toolbar = must(r'<header class="toolbar">.*?</header>', src).group(0)
hero = must(r'<header class="hero">.*?</header>', src).group(0)
footer_p = must(r'<p class="footer">(.*?)</p>', src).group(1)
sections = {m.group(1): m.group(0) for m in re.finditer(
    r'<section class="doc" id="([a-z-]+)"[^>]*>.*?</section>', src, re.S)}
# the footer paragraph lives in the checklist section of the source; it is printed on every page instead
sections["checklist"] = re.sub(r'\s*<p class="footer">.*?</p>', "", sections["checklist"], flags=re.S)

# sidebar icons / labels from the source sidebar
side = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(
    r'<li><a href="#([a-z-]+)">(<span class="ico"[^>]*><svg.*?</svg></span>)<span class="side-text">(.*?)</span></a></li>',
    
    src, re.S)}
side_heads = re.findall(r'<p class="side-head">(.*?)</p>', src)


def text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def section_parts(sid):
    sec = sections[sid]
    head = must(r'<div class="sec-head">(<span class="ico lg"[^>]*>.*?</span>)<h2 id="([^"]+)">(.*?)</h2></div>', sec)
    sub = must(r'<p class="sec-sub">(.*?)</p>', sec)
    body = sec[sub.end():sec.rindex("</section>")]
    return head.group(1), head.group(2), head.group(3), sub.group(1), body


def demote(body):
    # On a topic page the section title becomes the h1, so every heading moves up one level
    # while keeping its original look.
    body = re.sub(r"<h3>", '<h2 class="t-h3">', body).replace("</h3>", "</h2>")
    body = re.sub(r"<h4>", '<h3 class="t-h4">', body).replace("</h4>", "</h3>")
    return body


ORDER = [("home", "", HOME_TITLE)] + [(p[0], p[1] + "/", p[2]) for p in PAGES]


def sidebar(prefix, current):
    out = ['<nav class="sidebar" id="sidebar" aria-label="Handbook pages">']
    groups = [("Understand the score", ["overview", "performance", "cwv", "accessibility", "best-practices", "seo", "hidden"]),
              ("Build it right", ["budgets", "html", "css", "js", "media", "wordpress", "hosting", "testing", "checklist"])]
    slugs = {p[0]: p[1] + "/" for p in PAGES}
    slugs["overview"] = ""
    for gi, (gname, ids) in enumerate(groups):
        out.append(f'  <div class="side-group">\n    <p class="side-head">{side_heads[gi]}</p>\n    <ul class="side-list">')
        for i in ids:
            ico, label = side[i]
            href = prefix + slugs[i] if (prefix + slugs[i]) else "./"
            cur = ' aria-current="page"' if (i == current or (i == "overview" and current == "home")) else ""
            out.append(f'      <li><a href="{href}"{cur}>{ico}<span class="side-text">{label}</span></a></li>')
        out.append("    </ul>\n  </div>")
    out.append("</nav>")
    return "\n".join(out)


HEAD_SCRIPT = ('<script>try{if(localStorage.getItem("wv100-sidebar")==="closed")'
               'document.documentElement.classList.add("sb-collapsed")}catch(e){}</script>')

JS_BASE = r"""
(function(){
  var d=document,root=d.documentElement,sb=d.getElementById('sidebar'),tg=d.getElementById('sidebarToggle'),
      scrim=d.getElementById('scrim'),tip=d.getElementById('railTip'),narrow=matchMedia('(max-width:860px)'),
      links=[].slice.call(d.querySelectorAll('.side-list a'));
  function sbVisible(){return narrow.matches?sb.classList.contains('open'):!root.classList.contains('sb-collapsed')}
  function syncTg(){var v=sbVisible();tg.setAttribute('aria-expanded',v);tg.title=narrow.matches?(v?'Hide sidebar':'Show sidebar'):(v?'Collapse sidebar':'Expand sidebar')}
  function setSb(open){sb.classList.toggle('open',open);scrim.classList.toggle('show',open);syncTg()}
  function setCollapsed(c){root.classList.toggle('sb-collapsed',c);try{localStorage.setItem('wv100-sidebar',c?'closed':'open')}catch(e){}syncTg()}
  tg.addEventListener('click',function(){hideTip();if(narrow.matches)setSb(!sb.classList.contains('open'));else setCollapsed(!root.classList.contains('sb-collapsed'))});
  scrim.addEventListener('click',function(){setSb(false)});
  if(narrow.addEventListener)narrow.addEventListener('change',function(){setSb(false)});
  d.addEventListener('keydown',function(e){
    if(e.ctrlKey&&e.metaKey&&(e.key==='s'||e.key==='S')){e.preventDefault();tg.click()}
    if(e.key==='Escape'&&sb.classList.contains('open')){setSb(false);tg.focus()}
  });
  syncTg();
  /* Icon-rail tooltips (labels stay in the DOM for screen readers) */
  function showTip(a){
    if(narrow.matches||!root.classList.contains('sb-collapsed'))return;
    var r=a.getBoundingClientRect();tip.textContent=a.textContent.trim();
    tip.style.left=(r.right+10)+'px';tip.style.top=(r.top+r.height/2)+'px';tip.classList.add('show');
  }
  function hideTip(){tip.classList.remove('show')}
  links.forEach(function(a){
    a.addEventListener('mouseenter',function(){showTip(a)});a.addEventListener('focus',function(){showTip(a)});
    a.addEventListener('mouseleave',hideTip);a.addEventListener('blur',hideTip);
  });
  sb.addEventListener('scroll',hideTip,{passive:true});
  /* Print: expand disclosures, stamp URL + date, then restore */
  d.getElementById('printBtn').addEventListener('click',function(){window.print()});
  var closed=[];
  addEventListener('beforeprint',function(){
    closed=[].filter.call(d.querySelectorAll('details'),function(x){return !x.open});
    closed.forEach(function(x){x.open=true});
    var m=d.getElementById('printMeta');
    if(m)m.textContent=location.href.split('#')[0]+' · printed '+new Date().toLocaleDateString(undefined,{year:'numeric',month:'long',day:'numeric'});
  });
  addEventListener('afterprint',function(){closed.forEach(function(x){x.open=false});closed=[]});
})();
"""

JS_TABS = r"""
(function(){
  var d=document,tabs=[].slice.call(d.querySelectorAll('[role="tab"]'));
  function sel(t){tabs.forEach(function(x){var on=x===t;x.setAttribute('aria-selected',on);x.tabIndex=on?0:-1;d.getElementById(x.getAttribute('aria-controls')).hidden=!on})}
  tabs.forEach(function(t,i){
    t.addEventListener('click',function(){sel(t)});
    t.addEventListener('keydown',function(e){var n=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0;
      if(n){var nt=tabs[(i+n+tabs.length)%tabs.length];sel(nt);nt.focus();e.preventDefault()}});
  });
})();
"""

JS_CHECKLIST = r"""
(function(){
  var d=document,KEY='wv100-checklist',boxes=[].slice.call(d.querySelectorAll('#checklist-form input')),saved={};
  try{saved=JSON.parse(localStorage.getItem(KEY))||{}}catch(e){}
  var fill=d.getElementById('progressFill'),txt=d.getElementById('progressText');
  function update(){var n=boxes.filter(function(b){return b.checked}).length;fill.style.width=(n/boxes.length*100)+'%';txt.textContent=n+' of '+boxes.length+' done'}
  boxes.forEach(function(b){b.checked=!!saved[b.name];
    b.addEventListener('change',function(){saved[b.name]=b.checked;try{localStorage.setItem(KEY,JSON.stringify(saved))}catch(e){}update()})});
  d.getElementById('resetChecks').addEventListener('click',function(){saved={};boxes.forEach(function(b){b.checked=false});try{localStorage.removeItem(KEY)}catch(e){}update()});
  update();
})();
"""

# Old single-page anchors (…/#performance) keep working
OLD_HASHES = {p[0]: p[1] + "/" for p in PAGES}
HASH_REDIRECT = ("<script>(function(){var m=" + json.dumps(OLD_HASHES, separators=(",", ":")) +
                 ",h=location.hash.slice(1);if(m[h])location.replace(m[h])})()</script>")


def page(prefix, current, title, desc, url, main_html, extra_js="", ld=None, head_extra=""):
    tb = toolbar.replace('<a class="logo" href="./">', f'<a class="logo" href="{prefix or "./"}">')
    ld_json = json.dumps(ld, ensure_ascii=False, separators=(",", ":")) if ld else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="CWV — Core Web Vitals">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#f6f6f6">
{favicon}
<script type="application/ld+json">{ld_json}</script>
{head_extra}{style}
</head>
<body>
{HEAD_SCRIPT}
<a class="skip" href="#main">Skip to content</a>

{sprite}

{tb}

{sidebar(prefix, current)}
<div class="scrim" id="scrim" aria-hidden="true"></div>
<div class="rail-tip" id="railTip" aria-hidden="true"></div>

<main class="content" id="main" tabindex="-1">
<div class="page">
{main_html}
<footer class="footer"><p>{footer_p}</p>
<p class="credit">&copy; 2027 All Rights Reserved. Developed by <a href="https://www.chiranjitkarmakar.com/">Chiranjit Karmakar</a></p></footer>
</div>
</main>

<script>{JS_BASE}{extra_js}</script>
</body>
</html>
"""


def pager(prefix, idx):
    parts = ['<nav class="pager" aria-label="Previous and next pages">']
    if idx > 0:
        pid, pslug, _ = ORDER[idx - 1]
        ptitle = "Handbook home" if pid == "home" else text(side[pid][1])
        parts.append(f'  <a class="prev" href="{prefix + pslug or "./"}"><small>Previous</small><b>‹ {html.escape(ptitle)}</b></a>')
    if idx + 1 < len(ORDER):
        nid, nslug, _ = ORDER[idx + 1]
        parts.append(f'  <a class="next" href="{prefix + nslug}"><small>Next</small><b>{html.escape(text(side[nid][1]))} ›</b></a>')
    parts.append("</nav>")
    return "\n".join(parts)


def article_ld(title, desc, url, crumbs):
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "TechArticle", "headline": title, "description": desc, "url": url, "inLanguage": "en",
         "dateModified": MODIFIED, "author": AUTHOR, "isPartOf": {"@type": "WebSite", "name": "CWV — Core Web Vitals", "url": SITE},
         "about": ["Core Web Vitals", "WordPress", "Lighthouse", "PageSpeed Insights"]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]},
    ]}


written = []

# ---------------------------------------------------------------- home page
overview = sections["overview"]
toc = ['<section class="doc" id="contents" aria-labelledby="h-contents">',
       '  <div class="sec-head"><span class="ico lg" style="--c:var(--blue-fill)"><svg aria-hidden="true"><use href="#i-list"/></svg></span><h2 id="h-contents">Contents</h2></div>',
       '  <p class="sec-sub">Fifteen short chapters. Read the first half to understand how the score works, then follow the build phases in order.</p>']
for gname in ("Understand the score", "Build it right"):
    toc.append(f"  <h3>{gname}</h3>\n  <div class=\"toc\">")
    for sid, slug, title, desc, grp in PAGES:
        if grp != gname:
            continue
        ico = side[sid][0].replace('class="ico"', 'class="ico lg"')
        _, _, h2, _, _ = section_parts(sid)
        toc.append(f'    <a href="{slug}/">{ico}<span><b>{h2}</b><small>{html.escape(desc)}</small></span></a>')
    toc.append("  </div>")
toc.append("</section>")
home_hero = hero.replace(must(r"<h1>.*?</h1>", hero).group(0), f"<h1>{HOME_H1}</h1>")
home_main = f"{home_hero}\n\n{overview}\n\n" + "\n".join(toc) + "\n" + pager("", 0)
home_ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebSite", "name": "CWV — Core Web Vitals", "url": SITE, "inLanguage": "en"},
    {"@type": "TechArticle", "headline": HOME_H1, "description": HOME_DESC, "url": SITE, "inLanguage": "en",
     "author": AUTHOR,
     "dateModified": MODIFIED, "about": ["Core Web Vitals", "WordPress", "Lighthouse", "PageSpeed Insights"],
     "hasPart": [{"@type": "TechArticle", "headline": p[2], "url": SITE + p[1] + "/"} for p in PAGES]},
]}
(ROOT / "index.html").write_text(
    page("", "home", HOME_TITLE, HOME_DESC, SITE, home_main, ld=home_ld, head_extra=HASH_REDIRECT + "\n"),
    encoding="utf-8")
written.append(SITE)

# ---------------------------------------------------------------- topic pages
for idx, (sid, slug, title, desc, grp) in enumerate(PAGES, start=1):
    ico, hid, h2, sub, body = section_parts(sid)
    url = SITE + slug + "/"
    crumbs_html = (f'<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="../">Handbook</a></li>'
                   f'<li>{grp}</li><li><span aria-current="page">{text(side[sid][1])}</span></li></ol></nav>')
    main_html = f"""<article class="doc-page" id="{sid}" aria-labelledby="{hid}">
<header class="page-head">
  {crumbs_html}
  <div class="sec-head">{ico}<h1 class="page-title" id="{hid}">{h2}</h1></div>
  <p class="print-meta" id="printMeta">{url}</p>
  <p class="sec-sub">{sub}</p>
</header>
{demote(body).strip()}
</article>
{pager("../", idx)}"""
    js = (JS_TABS if 'role="tab"' in body else "") + (JS_CHECKLIST if "checklist-form" in body else "")
    ld = article_ld(title, desc, url, [("Handbook", SITE), (text(side[sid][1]), url)])
    out = ROOT / slug / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page("../", sid, title, desc, url, main_html, js, ld), encoding="utf-8")
    written.append(url)

# ---------------------------------------------------------------- sitemap
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{u}</loc><lastmod>{MODIFIED}</lastmod></url>\n" for u in written) +
    "</urlset>\n", encoding="utf-8")

for p in PAGES:
    assert len(p[2]) <= 60, (p[2], len(p[2]))
    assert len(p[3]) <= 160, (p[3], len(p[3]))
print(f"built {len(written)} pages")
