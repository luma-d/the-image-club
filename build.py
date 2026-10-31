#!/usr/bin/env python3
"""Build docs/ from the plain-markdown files in content/.

Pure Python 3 standard library, no pip dependencies.

Each content file has two blocks, `## en` and `## ar`. This script
wraps every line/paragraph in the site's span structure
(<span class="en"> / <span class="ar" lang="ar" dir="rtl">),
escapes the text for HTML, and regenerates docs/index.html from a
template. It also copies css/, js/, favicon.svg and assets/ into docs/.
Idempotent: every run rebuilds docs/ from scratch.
"""

import html
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
DOCS = ROOT / "docs"

NAV_ANCHORS = ["#about", "#workshops", "#membership", "#contact"]

PAGE = '''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="description" content="The Image Club — a new home for photography coming to Damascus. Film developing, cyanotype and hands-on workshops; founded by Luma Darwish." />
<title>The Image Club — نادي الصورة | Damascus</title>
<meta name="theme-color" content="#141413" />
<link rel="icon" type="image/svg+xml" href="favicon.svg" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:wght@400;500;600&family=Inter:wght@300;400;500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="css/style.css" />
</head>
<body>
<a class="skip-link" href="#main"><span class="en">Skip to content</span><span class="ar" lang="ar" dir="rtl">تخطَّ إلى المحتوى</span></a>
<div id="grain" aria-hidden="true"></div>

<header class="site-nav">
  <div class="nav-inner">
    <a class="brand" href="#top" aria-label="The Image Club — نادي الصورة">
      <svg class="logo-mark" viewBox="0 0 240 160" role="img" aria-label="The Image Club logo mark">
        <path d="M8 36 C 60 46, 180 46, 232 30" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>
        <rect x="50" y="46" width="62" height="106" fill="none" stroke="currentColor" stroke-width="4"/>
        <rect x="124" y="46" width="64" height="102" fill="currentColor"/>
        <rect x="73" y="16" width="16" height="44" rx="2" class="pin"/>
        <rect x="148" y="16" width="16" height="44" rx="2" class="pin"/>
      </svg>
      <span class="brand-text">
        <span class="wordmark">The Image Club</span>
        <span class="wordmark-ar arabic" lang="ar" dir="rtl">نادي الصورة</span>
      </span>
    </a>
    <button class="hamburger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    <nav class="nav-links">
{NAV_LINKS}      <button class="lang-btn" id="langBtn" aria-label="Switch language — تبديل اللغة"><span class="en">العربية</span><span class="ar" lang="ar" dir="rtl">English</span></button>
      <a class="ig-link" href="https://www.instagram.com/theimageclub" aria-label="Instagram" target="_blank" rel="noopener">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.5" cy="6.5" r="1.1" fill="currentColor"/></svg>
      </a>
    </nav>
  </div>
</header>

<main id="main">
  <section class="hero" id="top">
    <svg class="logo-mark hero-mark" viewBox="0 0 240 160" role="img" aria-label="The Image Club logo mark">
      <path d="M8 36 C 60 46, 180 46, 232 30" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>
      <rect x="50" y="46" width="62" height="106" fill="none" stroke="currentColor" stroke-width="4"/>
      <rect x="124" y="46" width="64" height="102" fill="currentColor"/>
      <rect x="73" y="16" width="16" height="44" rx="2" class="pin"/>
      <rect x="148" y="16" width="16" height="44" rx="2" class="pin"/>
    </svg>
    <h1>The Image Club</h1>
    <p class="arabic arabic-lg" lang="ar" dir="rtl">نادي الصورة</p>
    <p class="tagline">{TAGLINE}</p>
    <span class="soon-pill">{PILL}</span>
  </section>

  <div class="filmstrip" aria-hidden="true"></div>

  <section class="block invert" data-reveal id="about">
    <p class="section-label"><span class="en">01 — About</span><span class="ar" lang="ar" dir="rtl">٠١ — حول</span></p>
{ABOUT_PARAS}  </section>

  <div class="filmstrip" aria-hidden="true"></div>

  <section class="block" data-reveal id="workshops">
    <p class="section-label"><span class="en">02 — Workshops</span><span class="ar" lang="ar" dir="rtl">٠٢ — الورش</span></p>
    <p class="prose muted-prose">{WORKSHOPS_INTRO}</p>
    <div class="cards">
{CARDS}    </div>
    <div class="carousel" aria-label="Photos from our first workshops">
      <div class="car-track">
        <figure><img src="assets/gallery/01.jpg" alt="Cyanotype workshop participant preparing plants and negatives, Damascus, September 2026" loading="lazy" decoding="async" /></figure>
        <figure><img src="assets/gallery/02.jpg" alt="Cyanotype exposures on a rooftop in Damascus, September 2026" loading="lazy" decoding="async" /></figure>
        <figure><img src="assets/gallery/03.jpg" alt="Participants coating paper at the cyanotype workshop table, Damascus, September 2026" loading="lazy" decoding="async" /></figure>
        <figure><img src="assets/gallery/04.jpg" alt="Cyanotype prints and negatives drying under the sun, Damascus, September 2026" loading="lazy" decoding="async" /></figure>
        <figure><img src="assets/gallery/05.jpg" alt="Workshop session in a Damascene courtyard house, September 2026" loading="lazy" decoding="async" /></figure>
        <figure><img src="assets/gallery/06.jpg" alt="Participant preparing objects for a cyanotype exposure, Damascus, September 2026" loading="lazy" decoding="async" /></figure>
        <figure><img src="assets/gallery/07.jpg" alt="Film developing workshop around the workshop tables, Damascus, September 2026" loading="lazy" decoding="async" /></figure>
        <figure><img src="assets/gallery/08.jpg" alt="Black and white film developing session with tanks and chemistry, Damascus, September 2026" loading="lazy" decoding="async" /></figure>
        <figure><img src="assets/gallery/09.jpg" alt="Participants pouring chemistry during a film developing workshop, Damascus, September 2026" loading="lazy" decoding="async" /></figure>
        <figure><img src="assets/gallery/10.jpg" alt="C-41 colour developing explained at the whiteboard, Damascus, September 2026" loading="lazy" decoding="async" /></figure>
        <figure><img src="assets/gallery/11.jpg" alt="Film developing workshop discussion around the table, Damascus, September 2026" loading="lazy" decoding="async" /></figure>
        <figure><img src="assets/gallery/12.jpg" alt="Cyanotype plate with flowers and blue clips on the workshop table, Damascus, September 2026" loading="lazy" decoding="async" /></figure>
      </div>
      <div class="car-controls">
        <button class="car-btn car-prev" aria-label="Previous photos">←</button>
        <button class="car-btn car-next" aria-label="Next photos">→</button>
      </div>
    </div>
  </section>

  <div class="filmstrip" aria-hidden="true"></div>

  <section class="block invert" id="membership">
    <p class="section-label"><span class="en">03 — Membership</span><span class="ar" lang="ar" dir="rtl">٠٣ — العضوية</span></p>
    <h2>{MEMBERSHIP_H2}</h2>
    <a class="btn btn-outline" href="https://www.instagram.com/theimageclub" target="_blank" rel="noopener">{MEMBERSHIP_BTN}</a>
  </section>

  <div class="filmstrip" aria-hidden="true"></div>

  <section class="block" data-reveal id="contact">
    <p class="section-label"><span class="en">04 — Contact</span><span class="ar" lang="ar" dir="rtl">٠٤ — تواصل</span></p>
    <p class="prose"><strong>{LOCATION}</strong></p>
    <p class="prose"><span class="ig-handle">@theimageclub</span> &nbsp;·&nbsp; <a class="mail" href="mailto:hello@theimageclub.com">hello@theimageclub.com</a></p>
  </section>
</main>

<div class="filmstrip" aria-hidden="true"></div>

<footer class="site-footer invert">
  <svg class="logo-badge" viewBox="-30 -66 300 300" role="img" aria-label="The Image Club logo badge">
    <circle cx="120" cy="84" r="145" fill="none" stroke="currentColor" stroke-width="2"/>
    <path d="M8 36 C 60 46, 180 46, 232 30" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>
    <rect x="50" y="46" width="62" height="106" fill="none" stroke="currentColor" stroke-width="4"/>
    <rect x="124" y="46" width="64" height="102" fill="currentColor"/>
    <rect x="73" y="16" width="16" height="44" rx="2" class="pin"/>
    <rect x="148" y="16" width="16" height="44" rx="2" class="pin"/>
  </svg>
  <div class="footer-copy">
    <span class="en">{FOOTER_EN}</span>
    <span class="ar" lang="ar" dir="rtl">{FOOTER_AR}</span>
  </div>
</footer>

<script src="js/main.js"></script>
</body>
</html>
'''


def parse_md(path: Path):
    """Return (en_lines, ar_lines): raw lines of the two blocks."""
    en, ar = [], []
    mode = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "## en":
            mode = "en"
        elif line.strip() == "## ar":
            mode = "ar"
        elif mode:
            (en if mode == "en" else ar).append(line)
    return en, ar


def paragraphs(lines):
    """Blank-line-separated paragraphs, each a single string."""
    paras, cur = [], []
    for line in lines:
        if line.strip() == "":
            if cur:
                paras.append("\n".join(cur))
                cur = []
        else:
            cur.append(line)
    if cur:
        paras.append("\n".join(cur))
    return paras


def pair(en, ar):
    """The site's bilingual span structure; text escaped for HTML."""
    return ('<span class="en">%s</span>'
            '<span class="ar" lang="ar" dir="rtl">%s</span>'
            % (html.escape(en), html.escape(ar)))


def main():
    nav = parse_md(CONTENT / "nav.md")
    hero = parse_md(CONTENT / "hero.md")
    about = parse_md(CONTENT / "about.md")
    workshops = parse_md(CONTENT / "workshops.md")
    membership = parse_md(CONTENT / "membership.md")
    contact = parse_md(CONTENT / "contact.md")
    footer = parse_md(CONTENT / "footer.md")

    # Nav: one label per line, fixed anchors in order.
    if len(nav[0]) != len(nav[1]) != len(NAV_ANCHORS):
        raise SystemExit("nav.md: expected 4 link labels per language")
    nav_links = "".join(
        '      <a href="%s">%s</a>\n' % (anchor, pair(en, ar))
        for anchor, en, ar in zip(NAV_ANCHORS, nav[0], nav[1])
    )

    # Hero: paragraph 1 = tagline, paragraph 2 = pill.
    hero_en, hero_ar = paragraphs(hero[0]), paragraphs(hero[1])
    if len(hero_en) < 2 or len(hero_ar) < 2:
        raise SystemExit("hero.md: needs a tagline and a pill line")

    # About: paragraphs; a `> ` line renders as the italic closer.
    about_en, about_ar = paragraphs(about[0]), paragraphs(about[1])
    if len(about_en) != len(about_ar):
        raise SystemExit("about.md: en/ar paragraph counts differ")
    about_paras = []
    for en, ar in zip(about_en, about_ar):
        closer = en.startswith("> ")
        if closer:
            en, ar = en[2:], ar[2:]
        about_paras.append('    <p class="%s">%s</p>\n'
                          % ("prose about-close" if closer else "prose", pair(en, ar)))

    # Workshops: intro paragraph, then exactly 3 `### Title` + body pairs.
    w_en, w_ar = paragraphs(workshops[0]), paragraphs(workshops[1])
    titles_en = [p[4:] for p in w_en[1:] if p.startswith("### ")]
    titles_ar = [p[4:] for p in w_ar[1:] if p.startswith("### ")]
    bodies_en = [p for p in w_en[1:] if not p.startswith("### ")]
    bodies_ar = [p for p in w_ar[1:] if not p.startswith("### ")]
    if not (len(titles_en) == len(titles_ar) == len(bodies_en) == len(bodies_ar)):
        raise SystemExit("workshops.md: expected 3 `### Title` + body pairs per language")
    cards = []
    for i, ((t_en, t_ar), (b_en, b_ar)) in enumerate(
            zip(zip(titles_en, titles_ar), zip(bodies_en, bodies_ar)), start=1):
        cards.append(
            '      <article class="card" data-reveal>\n'
            '        <span class="card-num">%02d</span>\n'
            '        <h3>%s</h3>\n'
            '        <p>%s</p>\n'
            '      </article>\n' % (i, pair(t_en, t_ar), pair(b_en, b_ar)))

    # Membership: paragraph 1 = heading, paragraph 2 = button label.
    m_en, m_ar = paragraphs(membership[0]), paragraphs(membership[1])
    if len(m_en) < 2 or len(m_ar) < 2:
        raise SystemExit("membership.md: needs a heading and a button label")

    # Contact: paragraph 1 = bold location (email/Instagram are hardcoded).
    c_en, c_ar = paragraphs(contact[0]), paragraphs(contact[1])
    if not c_en or not c_ar:
        raise SystemExit("contact.md: needs a location line")

    # Footer: one line per item, joined with <br>.
    footer_en = "<br />".join(html.escape(l) for l in footer[0] if l.strip())
    footer_ar = "<br />".join(html.escape(l) for l in footer[1] if l.strip())

    page = PAGE.format(
        NAV_LINKS=nav_links,
        TAGLINE=pair(hero_en[0], hero_ar[0]),
        PILL=pair(hero_en[1], hero_ar[1]),
        ABOUT_PARAS="".join(about_paras),
        WORKSHOPS_INTRO=pair(w_en[0], w_ar[0]),
        CARDS="".join(cards),
        MEMBERSHIP_H2=pair(m_en[0], m_ar[0]),
        MEMBERSHIP_BTN=pair(m_en[1], m_ar[1]),
        LOCATION=pair(c_en[0], c_ar[0]),
        FOOTER_EN=footer_en,
        FOOTER_AR=footer_ar,
    )

    # Rebuild docs/ from scratch (idempotent).
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)
    (DOCS / "index.html").write_text(page, encoding="utf-8")

    written = [DOCS / "index.html"]

    def copy_tree(src: Path, dst: Path):
        for p in sorted(src.rglob("*")):
            if not p.is_file():
                continue
            if "originals" in p.parts:
                continue  # keep optimizer originals out of the site output
            d = dst / p.relative_to(src)
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, d)
            written.append(d)

    copy_tree(ROOT / "css", DOCS / "css")
    copy_tree(ROOT / "js", DOCS / "js")
    shutil.copy2(ROOT / "favicon.svg", DOCS / "favicon.svg")
    written.append(DOCS / "favicon.svg")
    copy_tree(ROOT / "assets", DOCS / "assets")

    for d in sorted(written):
        print("wrote", d.relative_to(ROOT))


if __name__ == "__main__":
    main()
