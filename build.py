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
    <div class="journal-wrap">
      <div class="journal-banner">
        <div class="j-banner-text">
          <h1 class="j-title">{TITLE}</h1>
          <div class="j-rule" aria-hidden="true"></div>
          <p class="j-sub">{SUB}</p>
          <p class="j-tag">{TAG}</p>
        </div>
        <figure class="j-art">
          <img src="assets/journal/diaries-art.jpg" alt="Illustration of a man thinking in an armchair under a hanging lamp" loading="lazy" />
        </figure>
      </div>
      <p class="j-editions-label">{EDITIONS}</p>
      <article class="edition-card">
        <figure class="edition-photo">
          <img src="assets/journal/taxi.jpg" alt="A taxi seen from the street" loading="lazy" />
        </figure>
        <div class="edition-panel">
          <p class="edition-label">{EDITION_LABEL}</p>
          <h2 class="edition-title">{THEME_TITLE}</h2>
          <p class="edition-pill"><span class="pill-dot" aria-hidden="true"></span>{DEADLINE}</p>
          <p class="edition-desc">{DESC}</p>
          <button class="curator-chip" data-curator type="button" aria-haspopup="dialog">
            <img class="curator-avatar" src="assets/journal/baraa.jpg" alt="" />
            <span class="curator-chip-text">
              <span class="curator-chip-label">{CURATOR_LABEL}</span>
              <span class="curator-chip-name">{CURATOR_NAME}</span>
            </span>
          </button>
          <a class="edition-btn" href="edition-01.html">{BUTTON_LABEL}<span class="btn-arrow" aria-hidden="true">→</span></a>
        </div>
      </article>
      <div class="j-intro">
{INTRO}      </div>
      <div class="info-cards">
{CARDS}      </div>
      <div class="band">
        <p class="band-text">{BAND}</p>
        <a class="band-btn" href="https://www.instagram.com/the.image.club" target="_blank" rel="noopener">@THE.IMAGE.CLUB</a>
      </div>
    </div>
  </section>
{POPUP}'''

EDITION_MAIN = '''  <div class="subnav-wrap">
    <nav class="subnav" aria-label="Breadcrumb and sections">
      <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="journal.html">{BC_HOME}</a><span class="bc-sep" aria-hidden="true">/</span><span class="bc-current">{BC_CURRENT}</span>
      </nav>
      <nav class="anchor-links" aria-label="Page sections">
        <a href="#about">{A_THEME}</a>
        <a href="#curator">{A_CURATOR}</a>
        <a href="#open-call">{A_OPEN}</a>
        <a class="submit-link" href="{TALLY}" target="_blank" rel="noopener">{A_SUBMIT}</a>
      </nav>
    </nav>
  </div>

  <section class="ed-hero">
    <p class="ed-kicker">{HERO_KICKER}</p>
    <h1 class="ed-title">{HERO_TITLE}</h1>
    <div class="ed-mosaic">
      <figure class="ed-m-taxi"><img src="assets/journal/taxi.jpg" alt="A taxi seen from the street" loading="lazy" /></figure>
      <figure class="ed-m-mosaic"><img src="assets/journal/mosaic.jpg" alt="A dark street mosaic" loading="lazy" /></figure>
      <figure class="ed-m-street"><img src="assets/journal/street.jpg" alt="A quiet street" loading="lazy" /></figure>
    </div>
    <p class="ed-caption">{HERO_CAPTION}</p>
  </section>

  <section class="ed-section" id="about">
    <p class="ed-label"><span class="ed-label-num">{ABOUT_NUM}</span>{ABOUT_LABEL}</p>
    <p class="ed-para">{ABOUT_P1}</p>
    <p class="ed-para">{ABOUT_P2}</p>
    <p class="ed-para">{ABOUT_P3}</p>
    <div class="ed-photo-row">
      <figure><img src="assets/journal/crosswalk.jpg" alt="Crosswalk" loading="lazy" /></figure>
      <figure><img src="assets/journal/protest.jpg" alt="Protest" loading="lazy" /></figure>
      <figure><img src="assets/journal/hate.jpg" alt="Protest poster" loading="lazy" /></figure>
      <figure><img src="assets/journal/arch.jpg" alt="Archway" loading="lazy" /></figure>
    </div>
  </section>

  <section class="ed-section" id="curator">
    <p class="ed-label"><span class="ed-label-num">{CURATOR_NUM}</span>{CURATOR_SECTION_LABEL}</p>
    <div class="ed-curator-card">
      <figure class="ed-portrait"><img src="assets/journal/baraa.jpg" alt="Portrait of Baraa Salih" loading="lazy" /></figure>
      <div class="ed-curator-text">
        <h2 class="ed-curator-name">{CURATOR_NAME}</h2>
        <p class="ed-curator-role">{CURATOR_ROLE}</p>
        <p class="ed-curator-bio">{CURATOR_BIO}</p>
        <div class="ed-gallery">
          <figure><img src="assets/journal/woman.jpg" alt="Woman waving" loading="lazy" /></figure>
          <figure><img src="assets/journal/swimmer.jpg" alt="Swimmer with arms outstretched" loading="lazy" /></figure>
          <figure><img src="assets/journal/kids.jpg" alt="Children in a street" loading="lazy" /></figure>
          <figure><img src="assets/journal/rubble.jpg" alt="Rubble and a motorcycle" loading="lazy" /></figure>
        </div>
        <p class="ed-caption">{GALLERY_CAPTION}</p>
        <button class="ed-outline-btn" data-curator type="button" aria-haspopup="dialog">{MORE_BTN}</button>
      </div>
    </div>
  </section>

  <section class="ed-section" id="open-call">
    <p class="ed-label"><span class="ed-label-num">{OPEN_NUM}</span>{OPEN_LABEL}</p>
    <div class="ed-opencall-grid">
      <div class="ed-details">
        <h3 class="ed-sub-title">{DETAILS_HEADING}</h3>
        <ol class="ed-detail-list">
          <li><span class="ed-detail-num">{D1_NUM}</span><span class="ed-detail-text">{D1}</span></li>
          <li><span class="ed-detail-num">{D2_NUM}</span><span class="ed-detail-text">{D2}</span></li>
          <li><span class="ed-detail-num">{D3_NUM}</span><span class="ed-detail-text">{D3}</span></li>
          <li><span class="ed-detail-num">{D4_NUM}</span><span class="ed-detail-text">{D4}</span></li>
          <li><span class="ed-detail-num">{D5_NUM}</span><span class="ed-detail-text">{D5}</span></li>
        </ol>
        <div class="ed-howto">
          <h4 class="ed-howto-title">{HOWTO_HEAD}</h4>
          <p class="ed-howto-body">{HOWTO_BODY}</p>
        </div>
      </div>
      <aside class="ed-keydates">
        <h3 class="ed-kd-title">{KD_TITLE}</h3>
        <div class="ed-kd-row"><span class="ed-kd-label">{KD1_LABEL}</span><span class="ed-kd-value">{KD1_VALUE}</span></div>
        <div class="ed-kd-row"><span class="ed-kd-label">{KD2_LABEL}</span><span class="ed-kd-value">{KD2_VALUE}</span></div>
        <div class="ed-kd-row"><span class="ed-kd-label">{KD3_LABEL}</span><span class="ed-kd-value">{KD3_VALUE}</span></div>
        <a class="ed-submit" href="{TALLY}" target="_blank" rel="noopener">{SUBMIT_LABEL}</a>
      </aside>
    </div>
  </section>

  <section class="ed-section">
    <p class="ed-label">{GUIDES_LABEL}</p>
    <div class="ed-guide-row ed-guide-row-3">
      <article class="ed-guide">
        <h3>{G1_TITLE}</h3>
        <ul>
          <li>{G1_B1}</li>
          <li>{G1_B2}</li>
          <li>{G1_B3}</li>
          <li>{G1_B4}</li>
        </ul>
      </article>
      <article class="ed-guide">
        <h3>{G2_TITLE}</h3>
        <ul>
          <li>{G2_B1}</li>
          <li>{G2_B2}</li>
          <li>{G2_B3}</li>
          <li>{G2_B4}</li>
          <li>{G2_B5}</li>
        </ul>
      </article>
      <article class="ed-guide">
        <h3>{G3_TITLE}</h3>
        <ul>
          <li>{G3_B1}</li>
          <li>{G3_B2}</li>
          <li>{G3_B3}</li>
        </ul>
      </article>
    </div>
    <div class="ed-guide-row ed-guide-row-2">
      <article class="ed-guide">
        <h3>{G4_TITLE}</h3>
        <ul>
          <li>{G4_B1}</li>
          <li>{G4_B2}</li>
          <li>{G4_B3}</li>
          <li>{G4_B4}</li>
        </ul>
      </article>
      <article class="ed-guide">
        <h3>{G5_TITLE}</h3>
        <ul>
          <li>{G5_B1}</li>
          <li>{G5_B2}</li>
          <li>{G5_B3}</li>
        </ul>
      </article>
    </div>
  </section>

  <section class="ed-cta">
    <div class="ed-cta-text">
      <h2 class="ed-cta-title">{CTA_TITLE}</h2>
      <p class="ed-cta-sub">{CTA_SUB}</p>
    </div>
    <a class="ed-submit" href="{TALLY}" target="_blank" rel="noopener">{CTA_BTN}</a>
  </section>
{POPUP}'''

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


def popup_markup():
    """Shared Baraa Salih popup modal, included in both journal pages."""
    return (
        '  <div class="popup-overlay" id="curatorPopup" role="dialog" aria-modal="true" '
        'aria-labelledby="popupName" hidden>\n'
        '    <button class="popup-close" type="button" aria-label="Close">×</button>\n'
        '    <div class="popup-panel">\n'
        '      <figure class="popup-portrait"><img src="assets/journal/baraa.jpg" alt="Portrait of Baraa Salih" loading="lazy" /></figure>\n'
        '      <div class="popup-text">\n'
        '        <p class="popup-kicker">%s</p>\n'
        '        <h2 class="popup-name" id="popupName">%s</h2>\n'
        '        <p class="popup-lead">%s</p>\n'
        '        <p class="popup-bio">%s</p>\n'
        '        <p class="popup-bio">%s</p>\n'
        '        <a class="popup-ig" href="https://www.instagram.com/braa_salih1/" target="_blank" rel="noopener">%s</a>\n'
        '      </div>\n'
        '      <div class="popup-gallery">\n'
        '        <figure><img src="assets/journal/woman.jpg" alt="Woman waving" loading="lazy" /></figure>\n'
        '        <figure><img src="assets/journal/swimmer.jpg" alt="Swimmer with arms outstretched" loading="lazy" /></figure>\n'
        '        <figure><img src="assets/journal/kids.jpg" alt="Children in a street" loading="lazy" /></figure>\n'
        '        <figure><img src="assets/journal/rubble.jpg" alt="Rubble and a motorcycle" loading="lazy" /></figure>\n'
        '      </div>\n'
        '      <p class="popup-caption">%s</p>\n'
        '    </div>\n'
        '  </div>\n'
    ) % (
        pair("Guest curator · Edition 01", "القيّم الفني الضيف · العدد الأول"),
        pair("Baraa Salih", "براء صالح"),
        pair("An independent photographer working across documentary photography and personal visual storytelling.",
             "مصوّر مستقل يعمل بين التصوير الوثائقي والسرد البصري الشخصي."),
        pair("Moving between Syria, Turkey and France, my practice has ranged from following the news to observing everyday life. Street photography has opened up a new space for my work — not simply as a means of expression, but as a way to rediscover places, people's relationships with them, and the relationship between the individual and the collective.",
             "بين سوريا وتركيا وفرنسا، تنوّعت تجربتي بين متابعة الخبر ومراقبة الحياة اليومية. ومنحني تصوير الشارع مساحة جديدة للممارسة، ليس كوسيلة للتعبير فقط، بل كطريقة لإعادة اكتشاف المكان وعلاقة الناس به، وعلاقة الفرد بالجماعة."),
        pair("To me, the street is an open stage without a director, a place from which to observe the world and see it in different ways.",
             "فالشارع، في نظري، مسرح مفتوح بلا مخرج، يمكن من خلاله ملاحظة العالم ورؤيته بطرق مختلفة."),
        pair("Instagram · @braa_salih1 ↗", "إنستغرام · braa_salih1 ↗"),
        pair("Photographs: Baraa Salih", "الصور: براء صالح"),
    )


def ar_num(n):
    """Arabic-Indic digits, no punctuation: 1 -> ٠١."""
    return "".join("٠١٢٣٤٥٦٧٨٩"[int(d)] for d in str(n))


def edition_values():
    """Hardcoded bilingual values for the Edition 01 page (spec section B)."""
    TALLY = "https://tally.so/r/4ar4Ao"
    return {
        "TALLY": TALLY,
        "POPUP": popup_markup(),
        "BC_HOME": pair("Diaries", "يوميات"),
        "BC_CURRENT": pair("Edition 01 · From the Streets", "العدد الأول · من الشارع"),
        "A_THEME": pair("The theme", "الموضوع"),
        "A_CURATOR": pair("Guest curator", "القيّم الفني الضيف"),
        "A_OPEN": pair("Open call", "الدعوة المفتوحة"),
        "A_SUBMIT": pair("Submit your work ↗", "قدّم مشاركتك ↗"),
        "HERO_KICKER": pair("First Edition · Open Call", "العدد الأول · دعوة مفتوحة للمشاركة"),
        "HERO_TITLE": pair("From the Streets", "من الشارع"),
        "HERO_CAPTION": pair("Photographs: Luma Darwish", "الصور: لوما درويش"),
        "ABOUT_NUM": pair("01", "٠١"),
        "ABOUT_LABEL": pair("About the theme", "عن الموضوع"),
        "ABOUT_P1": pair("The street is an open space where everyday life unfolds. It is where faces, stories and fleeting encounters intersect, and where our relationships with places and one another take shape.",
                         "الشارع مساحة مفتوحة للحياة اليومية، مكان تتقاطع فيه الوجوه والقصص واللقطات العابرة، وتشكّل فيه علاقتنا بالمكان وبالآخرين."),
        "ABOUT_P2": pair("For the first edition of Diaries, we invite photographers to explore the street through their lenses and share photographs that capture what draws their attention: faces, movement, light, shadows, details, unexpected moments and everyday scenes.",
                         "في العدد الأول من يوميات، ندعو المصوّرين إلى استكشاف الشارع من خلال عدساتهم، ومشاركة صور تلتقط ما يلتفتون إليه: الوجوه، الحركة، الضوء، الظلال، التفاصيل، اللقطات غير المتوقعة والمشاهد اليومية."),
        "ABOUT_P3": pair("We are not looking for a fixed definition of street photography. We welcome different experiences and perspectives, and photographs that reflect how each photographer sees the world around them.",
                         "لا نبحث عن تعريف محدد للتصوير الشارع، بل نرحّب بتجارب ورؤى مختلفة، وكل صورة تعكس طريقة صاحبها في رؤية العالم من حوله."),
        "CURATOR_NUM": pair("02", "٠٢"),
        "CURATOR_SECTION_LABEL": pair("Guest curator", "القيّم الفني الضيف"),
        "CURATOR_NAME": pair("Baraa Salih", "براء صالح"),
        "CURATOR_ROLE": pair("Independent photographer", "مصوّر مستقل"),
        "CURATOR_BIO": pair("An independent photographer working across documentary photography and personal visual storytelling. His practice has taken him between Syria, Turkey and France, and he approaches street photography as a way to rediscover places and people's relationships with them.",
                            "مصوّر مستقل يعمل بين التصوير الوثائقي والسرد البصري الشخصي. تنوّعت تجربته بين سوريا وتركيا وفرنسا، ويمنحه تصوير الشارع بوصفه مساحة لإعادة اكتشاف المكان وعلاقة الناس به."),
        "GALLERY_CAPTION": pair("Photographs: Baraa Salih", "الصور: براء صالح"),
        "MORE_BTN": pair("More about Baraa →", "تعرّف أكثر على براء ←"),
        "OPEN_NUM": pair("03", "٠٣"),
        "OPEN_LABEL": pair("Open call", "الدعوة المفتوحة"),
        "DETAILS_HEADING": pair("Submission details", "تفاصيل المشاركة"),
        "D1_NUM": pair("01", "٠١"),
        "D1": pair("Open to photographers of all experience levels.",
                   "الدعوة مفتوحة للمصوّرين من جميع مستويات الخبرة."),
        "D2_NUM": pair("02", "٠٢"),
        "D2": pair("Digital and analogue photography are welcome.",
                   "التصوير الرقمي والأنالوغ مرحّب بهما."),
        "D3_NUM": pair("03", "٠٣"),
        "D3": pair("Submit between one and three photographs.",
                   "يمكن تقديم صورة واحدة إلى ثلاث صور."),
        "D4_NUM": pair("04", "٠٤"),
        "D4": pair("Submission deadline: December 10, 2026.",
                   "آخر موعد للتقديم: 10 ديسمبر 2026."),
        "D5_NUM": pair("05", "٠٥"),
        "D5": pair("Approximately 10 photographers will be selected for this edition.",
                   "سيتم اختيار نحو 10 مصوّرين للمشاركة في هذا العدد."),
        "HOWTO_HEAD": pair("How to participate", "كيف تشارك؟"),
        "HOWTO_BODY": pair("Please read the submission guidelines below, then submit your information and photographs through the application form.",
                           "اقرأ إرشادات المشاركة أدناه، ثم أرسل معلوماتك وصورك من خلال استمارة التقديم."),
        "KD_TITLE": pair("Key dates", "مواعيد هامة"),
        "KD1_LABEL": pair("Submission deadline", "آخر موعد للتقديم"),
        "KD1_VALUE": pair("December 10, 2026", "10 ديسمبر 2026"),
        "KD2_LABEL": pair("Photographers selected", "عدد المصوّرين المختارين"),
        "KD2_VALUE": pair("≈ 10", "نحو 10"),
        "KD3_LABEL": pair("Selected photographers contacted", "التواصل مع المختارين"),
        "KD3_VALUE": pair("After the call closes", "بعد انتهاء فترة التقديم"),
        "SUBMIT_LABEL": pair("Submit your work ↗", "قدّم مشاركتك ↗"),
        "GUIDES_LABEL": pair("Submission guidelines", "إرشادات المشاركة"),
        "G1_TITLE": pair("Photographs", "الصور"),
        "G1_B1": pair("Submit between one and three photographs.", "يمكن تقديم صورة واحدة إلى ثلاث صور."),
        "G1_B2": pair("All photographs must be your own work, and you must hold the rights to them.", "يجب أن تكون الصور من تصويرك وأن تملك حقوق استخدامها."),
        "G1_B3": pair("Both digital and analogue photography are welcome.", "نرحّب بالتصوير الرقمي والأنالوغ والمعالجة الفوتوغرافية التي تقدّم رؤيتك."),
        "G1_B4": pair("No watermarks or added logos.", "لا تُقبَل الصور التي تتضمن علامات مائية أو شعارات مضافة."),
        "G2_TITLE": pair("Image specifications", "مواصفات الصور"),
        "G2_B1": pair("Format: JPEG.", "الصيغة: JPEG."),
        "G2_B2": pair("Colour profile: sRGB.", "مساحة الألوان: sRGB."),
        "G2_B3": pair("Maximum file size: 2 MB per photograph.", "ألا يتجاوز حجم الصورة 2 ميغابايت."),
        "G2_B4": pair("Maximum dimensions: 2,000 pixels on the longest edge.", "ألا يتجاوز الضلع الأطول 2000 بكسل."),
        "G2_B5": pair("Name files using your name and image number (e.g. Name_01.jpg).", "تسمية الملفات باسم المصوّر ورقم الصورة (مثال: Name_01.jpg)."),
        "G3_TITLE": pair("Text and information", "النصوص والمعلومات"),
        "G3_B1": pair("Include a title for each photograph, if applicable.", "أرفق عنواناً لكل صورة إن وجد."),
        "G3_B2": pair("You may include a short description or reflection about the image or the idea behind it. This is optional.", "يمكنك إضافة وصف قصير أو نص يشرح سياق الصورة أو الفكرة ورائها، هذا اختياري."),
        "G3_B3": pair("Include a short biography introducing yourself and your photographic practice.", "أضف نبذة قصيرة عنك وعن تجربتك الفوتوغرافية."),
        "G4_TITLE": pair("Image rights and publication", "حقوق الصور والنشر"),
        "G4_B1": pair("Photographers retain full ownership and copyright of their work.", "يحتفظ المصوّر بكامل حقوق ملكية صوره."),
        "G4_B2": pair("By submitting, you grant The Image Club permission to review your photographs for selection purposes only.", "يمنح تقديم الصور نادي يوميات الإذن بنشرها لأغراض الاختيار فقط."),
        "G4_B3": pair("If selected, you will be asked to confirm permission for publication in this edition of Diaries, with photographer credit.", "في حال اختيار الصور، سيُطلب تأكيد موافقة المصوّر على نشرها ضمن هذا العدد من يوميات، مع ذكر اسمه."),
        "G4_B4": pair("Any additional use beyond this edition requires separate permission.", "أي استخدام إضافي لصور خارج نطاق هذا العدد يتطلب موافقة منفصلة من المصوّر."),
        "G5_TITLE": pair("Please note", "ملاحظات"),
        "G5_B1": pair("Submission does not guarantee selection.", "تقديم الصور لا يضمن اختيارها."),
        "G5_B2": pair("Selected photographers will be contacted after the submission period closes.", "سيتم التواصل مع المصوّرين المختارين بعد انتهاء فترة التقديم."),
        "G5_B3": pair("Unselected photographs will not be published or used for other purposes.", "لن تُنشر الصور غير المختارة أو تُستخدم لأغراض أخرى."),
        "CTA_TITLE": pair("Ready to take part?", "جاهز للمشاركة؟"),
        "CTA_SUB": pair("Submission deadline: December 10, 2026", "آخر موعد للتقديم: 10 ديسمبر 2026"),
        "CTA_BTN": pair("Submit your work ↗", "قدّم مشاركتك ↗"),
    }


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

    # Journal: paragraphs 1-3 are the banner (title, subtitle, tagline);
    # paragraph 4 is the editions label; paragraphs 5-9 are the edition card
    # (theme title, description, curator label, curator name, button label);
    # remaining paragraphs before the first ### heading are the intro; each
    # ### section is an info card (title + body); the > lines become the
    # Instagram band (button label hardcoded). Pairing is by position
    # (like about_sections); missing/extra sections warn, never crash.
    def journal_split(paras):
        banner = list(paras[:3])
        if len(banner) < 3:
            banner += [""] * (3 - len(banner))
        editions_label = paras[3] if len(paras) > 3 else ""
        card = list(paras[4:9])
        if len(card) < 5:
            card += [""] * (5 - len(card))
        rest = paras[9:]
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
        return banner, editions_label, card, intro, sections, closers

    j_banner_en, j_label_en, j_card_en, j_intro_en, j_sec_en, j_close_en = journal_split(paragraphs(journal[0]))
    j_banner_ar, j_label_ar, j_card_ar, j_intro_ar, j_sec_ar, j_close_ar = journal_split(paragraphs(journal[1]))
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
        '      <p class="prose j-intro-para">%s</p>\n' % pair(en, ar)
        for en, ar in zip_longest(j_intro_en, j_intro_ar, fillvalue=""))

    section_parts = []
    for i, ((h_en, b_en), (h_ar, b_ar)) in enumerate(
            zip_longest(j_sec_en, j_sec_ar, fillvalue=("", [])), start=1):
        body_en = " ".join(b for b in b_en if b)
        body_ar = " ".join(b for b in b_ar if b)
        section_parts.append('      <article class="info-card">\n'
                             '        <span class="info-num">%s</span>\n'
                             '        <h3 class="info-title">%s</h3>\n'
                             '        <p class="info-body">%s</p>\n'
                             '      </article>\n'
                             % (pair("%02d" % i, ar_num(i)),
                                pair(h_en, h_ar),
                                pair(body_en, body_ar)))
    journal_sections = "".join(section_parts)

    band_text_en = " ".join(c for c in j_close_en if c)
    band_text_ar = " ".join(c for c in j_close_ar if c)
    if not band_text_en and not band_text_ar:
        print("warning: journal.md has no Instagram band line (>)")

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
             "EDITIONS": pair(j_label_en, j_label_ar),
             "EDITION_LABEL": pair("Edition 01", "العدد الأول"),
             "THEME_TITLE": pair(j_card_en[0], j_card_ar[0]),
             "DEADLINE": pair("Open call — Deadline December 10, 2026",
                              "دعوة مفتوحة — آخر موعد ١٠ ديسمبر ٢٠٢٦"),
             "DESC": pair(j_card_en[1], j_card_ar[1]),
             "CURATOR_LABEL": pair(j_card_en[2], j_card_ar[2]),
             "CURATOR_NAME": pair(j_card_en[3], j_card_ar[3]),
             "BUTTON_LABEL": pair(j_card_en[4], j_card_ar[4]),
             "INTRO": intro_paras,
             "CARDS": journal_sections,
             "BAND": pair(band_text_en, band_text_ar),
             "POPUP": popup_markup()},
        ),
        "edition-01.html": (
            "From the Streets — Diaries Edition 01 — The Image Club",
            EDITION_MAIN,
            edition_values(),
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
