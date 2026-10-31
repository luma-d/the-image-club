# The Image Club — editing & build

The website is generated from plain-markdown files in `content/`. Edit those
files, then run `python3 build.py` — it rewrites `docs/index.html` and
refreshes the copied `css/`, `js/`, `favicon.svg` and `assets/` inside
`docs/`. **`docs/` is what GitHub Pages serves** (from the `main` branch).

## Content files

| File | What it holds |
|---|---|
| `content/hero.md` | paragraph 1 = hero tagline, paragraph 2 = pill text |
| `content/about.md` | about paragraphs; a line starting `> ` becomes the italic closer |
| `content/workshops.md` | paragraph 1 = intro; then one `### Card title` + paragraph per workshop card (exactly 3; numbered 01–03 automatically) |
| `content/membership.md` | paragraph 1 = heading, paragraph 2 = button label |
| `content/contact.md` | paragraph 1 = bold location line (the email and Instagram handle are fixed in `build.py`) |
| `content/footer.md` | footer lines, one per line; joined with `<br>` in the output |
| `content/nav.md` | nav link labels, one per line, in order: About, Workshops, Membership, Contact |

## Markdown format

Every content file has exactly two blocks:

```
## en
(English text)

## ar
(Arabic text)
```

Rules:

- Paragraphs are separated by a blank line.
- `build.py` escapes everything for HTML and wraps each line/paragraph in
  `<span class="en">…</span><span class="ar" lang="ar" dir="rtl">…</span>` —
  you never need to write HTML or `<span>` tags yourself.
- The language toggle, section labels (`01 — About` …), logo SVGs, film
  strips, photo carousel and the Instagram link are fixed in `build.py`;
  they are not part of the content files.
- In `footer.md` and `nav.md` each line is one item — no blank lines inside
  the block.

## Build & preview

```
python3 build.py     # rebuild docs/ from content/ (prints every file written)
./start.sh           # rebuild, then serve docs/ on http://127.0.0.1:8000 + cloudflared demo URL
```

`build.py` is pure Python 3 stdlib, idempotent, and takes no arguments.

## ملاحظة بالعربية

تحرير النصوص يتم داخل ملفات `content/` كنصٍّ عادي، ثم يُشغَّل
`python3 build.py` لإعادة بناء الصفحة النهائية داخل مجلد `docs/` — وهو
المجلّد الذي ينشره GitHub Pages من فرع `main`.
