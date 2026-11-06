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
from itertools import zip_longest
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
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:wght@500;600&display=swap" rel="stylesheet" />
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
      <a class="ig-link" href="https://www.instagram.com/the.image.club" aria-label="Instagram" target="_blank" rel="noopener">
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


  <section class="block invert" data-reveal id="about">
    <p class="section-label">{SEC1}</p>
{ABOUT_PARAS}  </section>


  <section class="block" data-reveal id="workshops">
    <p class="section-label">{SEC2}</p>
    <p class="prose muted-prose">{WORKSHOPS_INTRO}</p>
    <div class="cards">
{CARDS}    </div>
    <div class="carousel" aria-label="Photos from our first workshops">
      <div class="car-track">
{CAROUSEL}      </div>
      <div class="car-controls">
        <button class="car-btn car-prev" aria-label="Previous photos">←</button>
        <button class="car-btn car-next" aria-label="Next photos">→</button>
      </div>
    </div>
  </section>


  <section class="block invert" id="membership">
    <p class="section-label">{SEC3}</p>
    <h2>{MEMBERSHIP_H2}</h2>
    <a class="btn btn-outline" href="https://www.instagram.com/the.image.club" target="_blank" rel="noopener">{MEMBERSHIP_BTN}</a>
  </section>


  <section class="block" data-reveal id="contact">
    <p class="section-label">{SEC4}</p>
    <p class="prose"><strong>{LOCATION}</strong></p>
    <p class="prose"><span class="ig-handle">@the.image.club</span> &nbsp;·&nbsp; <a class="mail" href="mailto:hi@theimageclub.org">hi@theimageclub.org</a></p>
  </section>
</main>


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


LANG_HEADINGS = {
    "en": {"en", "english", "english (en)", "english(en)"},
    "ar": {"ar", "arabic", "عربي", "عربية", "العربية", "عربى"},
}


def parse_md(path: Path):
    """Return (en_lines, ar_lines): raw lines of the two language blocks.

    Tolerant of non-technical edits: a missing file, headings renamed to
    "## English" / "## Arabic" / "## عربي", a BOM, or text left outside
    any heading — all still publish, with a warning naming what to fix.
    """
    if not path.exists():
        print("warning: content/%s is missing; publishing without it" % path.name)
        return [], []
    text = path.read_text(encoding="utf-8-sig")
    en, ar = [], []
    blocks = {"en": en, "ar": ar}
    mode, seen_heading, pre = None, False, []
    for line in text.splitlines():
        s = line.strip().rstrip(":：").strip().lower()
        if s.startswith("## "):
            name = s[3:].strip()
            seen_heading = True
            mode = next((lang for lang, names in LANG_HEADINGS.items()
                         if name in names), None)
            if mode is None:
                print("warning: content/%s has an unknown heading %r — text "
                      "under it is skipped (use ## en and ## ar)"
                      % (path.name, line.strip()))
            continue
        if mode:
            blocks[mode].append(line)
        elif not seen_heading:
            pre.append(line)
    if pre and not en:
        print("warning: content/%s has text before the first heading — "
              "treating it as English" % path.name)
        en[:0] = pre
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

    # Nav: one label per line, fixed anchors in order. Blank lines ignored.
    nav = [[l for l in block if l.strip()] for block in nav]
    if len(nav[0]) != len(nav[1]) or len(nav[0]) != len(NAV_ANCHORS):
        print("warning: nav.md should have %d labels per language; publishing with what is there"
              % len(NAV_ANCHORS))
    nav_links = "".join(
        '      <a href="%s">%s</a>\n' % (anchor, pair(en, ar))
        for anchor, en, ar in zip_longest(NAV_ANCHORS, nav[0], nav[1], fillvalue="")
    )

    # Section labels ("01 — About") reuse the nav.md labels, so editing a
    # label in nav.md updates both the top bar and the section heading.
    AR_NUMS = ("٠١", "٠٢", "٠٣", "٠٤")
    sec_labels = {
        i: ('<span class="en">%02d — %s</span>'
            '<span class="ar" lang="ar" dir="rtl">%s — %s</span>'
            % (i, html.escape(en), AR_NUMS[i - 1], html.escape(ar)))
        for i, (en, ar) in enumerate(zip_longest(nav[0], nav[1], fillvalue=""), 1)
    }

    # Hero: paragraph 1 = tagline, paragraph 2 = pill.
    hero_en, hero_ar = paragraphs(hero[0]), paragraphs(hero[1])
    if len(hero_en) < 2 or len(hero_ar) < 2:
        print("warning: hero.md should have a tagline and a pill line per language")
    hero_en += [""] * (2 - len(hero_en)) if len(hero_en) < 2 else []
    hero_ar += [""] * (2 - len(hero_ar)) if len(hero_ar) < 2 else []

    # About: paragraphs; `> ` renders as the italic closer; `### ` as a heading.
    about_en, about_ar = paragraphs(about[0]), paragraphs(about[1])
    if len(about_en) != len(about_ar):
        print("warning: about.md has %d en paragraphs but %d ar — pairing what "
              "matches; extras will show in one language only"
              % (len(about_en), len(about_ar)))
    about_paras = []
    for en, ar in zip_longest(about_en, about_ar, fillvalue=""):
        if en.startswith("### ") or ar.startswith("### "):
            about_paras.append('    <h3 class="about-heading">%s</h3>\n'
                               % pair(en[4:] if en.startswith("### ") else en,
                                      ar[4:] if ar.startswith("### ") else ar))
            continue
        closer = en.startswith("> ") or ar.startswith("> ")
        if closer:
            en, ar = en[2:], ar[2:]
        about_paras.append('    <p class="%s">%s</p>\n'
                          % ("prose about-close" if closer else "prose", pair(en, ar)))

    # Workshops: intro paragraph, then `### Title` cards. A card body is
    # optional; titles and bodies are matched by position in the file, so
    # deleting a description never shifts text onto the wrong card.
    w_en, w_ar = paragraphs(workshops[0]), paragraphs(workshops[1])
    def cards_of(block):
        out, cur = [], None
        for p in block:
            if p.startswith("### "):
                cur = {"title": p[4:], "body": ""}
                out.append(cur)
            elif cur is not None and not cur["body"]:
                cur["body"] = p
        return out
    w_cards_en, w_cards_ar = cards_of(w_en), cards_of(w_ar)
    if len(w_cards_en) != len(w_cards_ar):
        print("warning: workshops.md has %d en cards but %d ar cards — pairing what matches"
              % (len(w_cards_en), len(w_cards_ar)))
    cards = []
    blank = {"title": "", "body": ""}
    for i, (c_en, c_ar) in enumerate(
            zip_longest(w_cards_en, w_cards_ar, fillvalue=blank), start=1):
        body = ('        <p>%s</p>\n' % pair(c_en["body"], c_ar["body"])
                if (c_en["body"] or c_ar["body"]) else "")
        cards.append(
            '      <article class="card" data-reveal>\n'
            '        <span class="card-num">%02d</span>\n'
            '        <h3>%s</h3>\n%s'
            '      </article>\n' % (i, pair(c_en["title"], c_ar["title"]), body))

    # Membership: paragraph 1 = heading, paragraph 2 = button label.
    m_en, m_ar = paragraphs(membership[0]), paragraphs(membership[1])
    if len(m_en) < 2 or len(m_ar) < 2:
        print("warning: membership.md should have a heading and a button label per language")
    m_en += [""] * max(0, 2 - len(m_en))
    m_ar += [""] * max(0, 2 - len(m_ar))

    # Contact: paragraph 1 = bold location (email/Instagram are hardcoded).
    c_en, c_ar = paragraphs(contact[0]), paragraphs(contact[1])
    if not c_en or not c_ar:
        print("warning: contact.md should have a location line per language")
    c_en += [""] if not c_en else []
    c_ar += [""] if not c_ar else []

    # Carousel: one slide per image in assets/gallery/, sorted by filename.
    # Optional content/gallery.md: one alt-text line per image, same order.
    gallery_dir = ROOT / "assets" / "gallery"
    imgs = sorted(p.name for p in gallery_dir.iterdir()
                  if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
    alts = []
    gpath = CONTENT / "gallery.md"
    if gpath.exists():
        alts = [l.strip() for l in gpath.read_text(encoding="utf-8").splitlines()
                if l.strip() and not l.startswith("#")]
    carousel = "".join(
        '        <figure><img src="assets/gallery/%s" alt="%s" loading="lazy" decoding="async" /></figure>\n'
        % (name, html.escape(alts[i] if i < len(alts)
             else "From the club's workshops in Damascus, September 2026"))
        for i, name in enumerate(imgs))

    # Footer: one line per item, joined with <br>.
    footer_en = "<br />".join(html.escape(l) for l in footer[0] if l.strip())
    footer_ar = "<br />".join(html.escape(l) for l in footer[1] if l.strip())

    page = PAGE.format(
        NAV_LINKS=nav_links,
        SEC1=sec_labels.get(1, ""), SEC2=sec_labels.get(2, ""),
        SEC3=sec_labels.get(3, ""), SEC4=sec_labels.get(4, ""),
        TAGLINE=pair(hero_en[0], hero_ar[0]),
        PILL=pair(hero_en[1], hero_ar[1]),
        ABOUT_PARAS="".join(about_paras),
        WORKSHOPS_INTRO=pair(w_en[0], w_ar[0]),
        CARDS="".join(cards),
        CAROUSEL=carousel,
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
    (DOCS / "CNAME").write_text("theimageclub.org\n", encoding="utf-8")

    for d in sorted(written):
        print("wrote", d.relative_to(ROOT))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # never take the live site down over a build bug
        print("build failed: %s — the previous site stays published" % exc)
        raise SystemExit(1)
