#!/usr/bin/env python3
"""Build docs/ from the plain-markdown files in content/.

Pure Python 3 standard library, no pip dependencies.

Each content file has two blocks, `## en` and `## ar`. This script
wraps every line/paragraph in the site's span structure
(<span class="en"> / <span class="ar" lang="ar" dir="rtl">),
escapes the text for HTML, and regenerates one page per section in
docs/ (index.html, about.html, workshops.html, journal.html,
membership.html, contact.html) from a shared base template. It also
copies css/, js/, favicon.svg and assets/ into docs/.
Idempotent: every run rebuilds docs/ from scratch.
"""

import html
import shutil
from itertools import zip_longest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
DOCS = ROOT / "docs"

NAV_LINKS = ["about.html", "workshops.html", "journal.html", "membership.html", "contact.html"]

BASE = '''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="description" content="The Image Club — a new home for photography coming to Damascus. Film developing, cyanotype and hands-on workshops; founded by Luma Darwish." />
<title>{TITLE}</title>
<meta name="theme-color" content="#141413" />
<link rel="icon" type="image/svg+xml" href="favicon.svg" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:wght@500;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="css/style.css" />
</head>
<body>
<a class="skip-link" href="#main"><span class="en">Skip to content</span><span class="ar" lang="ar" dir="rtl">تخطَّ إلى المحتوى</span></a>
<div id="grain" aria-hidden="true"></div>

<header class="site-nav">
  <div class="nav-inner">
    <a class="brand" href="index.html" aria-label="The Image Club — نادي الصورة">
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
{MAIN}
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

INDEX_MAIN = '''  <section class="hero" id="top">
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
    <a class="soon-pill" href="membership.html">{PILL}</a>
  </section>
'''

ABOUT_MAIN = '''  <section class="block invert" data-reveal id="about">
    <p class="section-label">{SEC1}</p>
{ABOUT_PARAS}  </section>
'''

WORKSHOPS_MAIN = '''  <section class="block" data-reveal id="workshops">
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
'''

JOURNAL_MAIN = '''  <section class="block invert" id="journal">
    <div class="diaries-banner">
      <div class="diaries-text">
        <h1 class="diaries-title">{TITLE}</h1>
        <p class="diaries-sub">{SUB}</p>
        <p class="diaries-tag">{TAG}</p>
        <p class="diaries-edition">{EDITION}</p>
      </div>
      <img class="diaries-art" src="assets/journal/diaries-art.jpg" alt="Illustration of a man thinking in an armchair under a hanging lamp" />
    </div>
    <div class="diaries-intro">
{INTRO}    </div>
{SECTIONS}  </section>
  <section class="diaries-band">
    <p class="band-lead">{BAND_LEAD}</p>
    <p class="band-note">{BAND_NOTE}</p>
  </section>
'''

MEMBERSHIP_MAIN = '''  <section class="block invert" id="membership">
    <p class="section-label">{SEC4}</p>
{MEMBERSHIP_BODY}    <a class="btn btn-outline" href="https://www.instagram.com/the.image.club" target="_blank" rel="noopener">{MEMBERSHIP_BTN}</a>
  </section>
'''

CONTACT_MAIN = '''  <section class="block" data-reveal id="contact">
    <p class="section-label">{SEC5}</p>
{CONTACT_BODY}    <p class="prose"><strong>{LOCATION}</strong></p>
    <p class="prose"><span class="ig-handle">@the.image.club</span> &nbsp;·&nbsp; <a class="mail" href="mailto:hi@theimageclub.org">hi@theimageclub.org</a></p>
  </section>
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
    """Blank-line-separated paragraphs, each a single string.

    A `### ` heading line is always its own paragraph even without a blank
    line around it, and a `> ` line always starts a new paragraph — the
    GitHub web editor makes it easy to delete those blank lines by accident.
    """
    paras, cur = [], []
    for line in lines:
        s = line.strip()
        if s.startswith("### "):
            if cur:
                paras.append("\n".join(cur))
                cur = []
            paras.append(s)
        elif s.startswith("> ") and cur:
            paras.append("\n".join(cur))
            cur = [line]
        elif s == "":
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


def sub(template, **values):
    """Replace {KEY} placeholders without a format pass (content may contain braces)."""
    for key, value in values.items():
        template = template.replace("{" + key + "}", value)
    return template


def main():
    nav = parse_md(CONTENT / "nav.md")
    hero = parse_md(CONTENT / "hero.md")
    about = parse_md(CONTENT / "about.md")
    workshops = parse_md(CONTENT / "workshops.md")
    journal = parse_md(CONTENT / "journal.md")
    membership = parse_md(CONTENT / "membership.md")
    contact = parse_md(CONTENT / "contact.md")
    footer = parse_md(CONTENT / "footer.md")

    # Nav: one label per line, fixed page hrefs in order. Blank lines ignored.
    nav = [[l for l in block if l.strip()] for block in nav]
    if len(nav[0]) != len(nav[1]) or len(nav[0]) != len(NAV_LINKS):
        print("warning: nav.md should have %d labels per language; publishing with what is there"
              % len(NAV_LINKS))
    nav_links = "".join(
        '      <a href="%s">%s</a>\n' % (href, pair(en, ar))
        for href, en, ar in zip_longest(NAV_LINKS, nav[0], nav[1], fillvalue="")
    )

    # Section labels reuse the nav.md labels, so editing a
    # label in nav.md updates both the top bar and the section heading.
    sec_labels = {
        i: ('<span class="en">%s</span>'
            '<span class="ar" lang="ar" dir="rtl">%s</span>'
            % (html.escape(en), html.escape(ar)))
        for i, (en, ar) in enumerate(zip_longest(nav[0], nav[1], fillvalue=""), 1)
    }

    # Hero: paragraph 1 = tagline, paragraph 2 = pill.
    hero_en, hero_ar = paragraphs(hero[0]), paragraphs(hero[1])
    if len(hero_en) < 2 or len(hero_ar) < 2:
        print("warning: hero.md should have a tagline and a pill line per language")
    hero_en += [""] * (2 - len(hero_en)) if len(hero_en) < 2 else []
    hero_ar += [""] * (2 - len(hero_ar)) if len(hero_ar) < 2 else []

    # About: `### ` headings split the text into sections; `> ` is the italic
    # closer. Sections pair by order (heading with heading) and paragraphs
    # pair within their section — merging or deleting paragraphs in one
    # language never shifts text in the other.
    def about_sections(paras):
        sections, head, body, closer = [], "", [], ""
        for p in paras:
            if p.startswith("### "):
                sections.append((head, body))
                head, body = p[4:], []
            elif p.startswith("> "):
                closer = p[2:]
            else:
                body.append(p)
        sections.append((head, body))
        return sections, closer

    a_sec_en, a_close_en = about_sections(paragraphs(about[0]))
    a_sec_ar, a_close_ar = about_sections(paragraphs(about[1]))
    if len(a_sec_en) != len(a_sec_ar):
        print("warning: about.md has %d en sections but %d ar sections — "
              "pairing what matches; extras show in one language only"
              % (len(a_sec_en), len(a_sec_ar)))

    def side(en, ar):
        """Class that hides a paragraph in the language it has no text for."""
        if en and not ar:
            return " en-only"
        if ar and not en:
            return " ar-only"
        return ""

    about_paras = []
    for (h_en, b_en), (h_ar, b_ar) in zip_longest(a_sec_en, a_sec_ar, fillvalue=("", [])):
        if h_en or h_ar:
            about_paras.append('    <h3 class="about-heading%s">%s</h3>\n'
                               % (side(h_en, h_ar), pair(h_en, h_ar)))
        for en, ar in zip_longest(b_en, b_ar, fillvalue=""):
            about_paras.append('    <p class="prose%s">%s</p>\n'
                               % (side(en, ar), pair(en, ar)))
    if a_close_en or a_close_ar:
        about_paras.append('    <p class="prose about-close%s">%s</p>\n'
                           % (side(a_close_en, a_close_ar), pair(a_close_en, a_close_ar)))

    # Founder photo right after the first About prose paragraph (if any).
    figure = ('    <figure class="about-figure">\n'
              '      <img src="assets/about/founder.png" alt="Luma Darwish, founder of The Image Club" loading="lazy" />\n'
              '    </figure>\n')
    for i, para in enumerate(about_paras):
        if para.startswith('    <p class="prose'):
            about_paras.insert(i + 1, figure)
            break

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

    # Journal: paragraphs 1-4 are the banner (title, subtitle, tagline,
    # edition line); paragraphs before the first ### heading are the intro;
    # each ### section is numbered (01/02/03 in English, ١./٢./٣. in Arabic)
    # with paragraphs beneath it; the > lines become the closing red band.
    # Pairing is by position (like about_sections); missing/extra sections
    # warn, never crash.
    AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"

    def ar_number(n):
        return "".join(AR_DIGITS[int(d)] for d in str(n)) + "."

    def journal_split(paras):
        banner = list(paras[:4])
        if len(banner) < 4:
            banner += [""] * (4 - len(banner))
        rest = paras[4:]
        intro, sections, closers = [], [], []
        head, body, seen = None, [], False
        for para in rest:
            if para.startswith("### "):
                if seen:
                    sections.append((head, body))
                head, body = para[4:], []
                seen = True
            elif para.startswith("> "):
                closers.append(para[2:])
            elif not seen:
                intro.append(para)
            else:
                body.append(para)
        if seen:
            sections.append((head, body))
        return banner, intro, sections, closers

    j_banner_en, j_intro_en, j_sec_en, j_close_en = journal_split(paragraphs(journal[0]))
    j_banner_ar, j_intro_ar, j_sec_ar, j_close_ar = journal_split(paragraphs(journal[1]))
    if len(j_sec_en) != len(j_sec_ar):
        print("warning: journal.md has %d en sections but %d ar sections — "
              "pairing what matches; extras show in one language only"
              % (len(j_sec_en), len(j_sec_ar)))

    def body_of(block_en, block_ar, name):
        if not block_en and not block_ar:
            print("warning: %s.md has no text" % name)
        return "".join(
            '    <p class="prose">%s</p>\n' % pair(en, ar)
            for en, ar in zip_longest(block_en, block_ar, fillvalue=""))

    intro_paras = "".join(
        '      <p class="prose%s">%s</p>\n' % (side(en, ar), pair(en, ar))
        for en, ar in zip_longest(j_intro_en, j_intro_ar, fillvalue=""))

    section_parts = []
    for i, ((h_en, b_en), (h_ar, b_ar)) in enumerate(
            zip_longest(j_sec_en, j_sec_ar, fillvalue=("", [])), start=1):
        num = pair("%02d" % i, ar_number(i))
        section_parts.append('    <h3 class="diaries-heading%s"><span class="diaries-num">%s</span> %s</h3>\n'
                             % (side(h_en, h_ar), num, pair(h_en, h_ar)))
        for en, ar in zip_longest(b_en, b_ar, fillvalue=""):
            section_parts.append('    <p class="prose%s">%s</p>\n'
                                 % (side(en, ar), pair(en, ar)))
    journal_sections = "".join(section_parts)

    j_close_en = (j_close_en + ["", ""])[:2]
    j_close_ar = (j_close_ar + ["", ""])[:2]
    band_lead = pair(j_close_en[0], j_close_ar[0])
    band_note = pair(j_close_en[1], j_close_ar[1])

    m_en, m_ar = paragraphs(membership[0]), paragraphs(membership[1])
    membership_body = body_of(m_en, m_ar, "membership")

    c_en, c_ar = paragraphs(contact[0]), paragraphs(contact[1])
    contact_body = body_of(c_en, c_ar, "contact")

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

    pages = {
        "index.html": (
            "The Image Club — نادي الصورة",
            INDEX_MAIN,
            {"TAGLINE": pair(hero_en[0], hero_ar[0]),
             "PILL": pair(hero_en[1], hero_ar[1])},
        ),
        "about.html": (
            "About — The Image Club",
            ABOUT_MAIN,
            {"SEC1": sec_labels.get(1, ""),
             "ABOUT_PARAS": "".join(about_paras)},
        ),
        "workshops.html": (
            "Workshops — The Image Club",
            WORKSHOPS_MAIN,
            {"SEC2": sec_labels.get(2, ""),
             "WORKSHOPS_INTRO": pair(w_en[0] if w_en else "", w_ar[0] if w_ar else ""),
             "CARDS": "".join(cards),
             "CAROUSEL": carousel},
        ),
        "journal.html": (
            "Journal — The Image Club",
            JOURNAL_MAIN,
            {"TITLE": pair(j_banner_en[0], j_banner_ar[0]),
             "SUB": pair(j_banner_en[1], j_banner_ar[1]),
             "TAG": pair(j_banner_en[2], j_banner_ar[2]),
             "EDITION": pair(j_banner_en[3], j_banner_ar[3]),
             "INTRO": intro_paras,
             "SECTIONS": journal_sections,
             "BAND_LEAD": band_lead,
             "BAND_NOTE": band_note},
        ),
        "membership.html": (
            "Membership — The Image Club",
            MEMBERSHIP_MAIN,
            {"SEC4": sec_labels.get(4, ""),
             "MEMBERSHIP_BODY": membership_body,
             "MEMBERSHIP_BTN": pair("Follow us on Instagram", "تابعونا على إنستغرام")},
        ),
        "contact.html": (
            "Contact — The Image Club",
            CONTACT_MAIN,
            {"SEC5": sec_labels.get(5, ""),
             "CONTACT_BODY": contact_body,
             "LOCATION": pair("Damascus, Syria", "دمشق، سوريا")},
        ),
    }

    # Rebuild docs/ from scratch (idempotent).
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)

    written = []
    for name, (title, fragment, values) in pages.items():
        doc = sub(BASE, TITLE=title, NAV_LINKS=nav_links,
                  MAIN=sub(fragment, **values),
                  FOOTER_EN=footer_en, FOOTER_AR=footer_ar)
        (DOCS / name).write_text(doc, encoding="utf-8")
        written.append(DOCS / name)

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
    written.append(DOCS / "CNAME")

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
