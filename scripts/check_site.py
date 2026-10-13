#!/usr/bin/env python3
"""Checks for mathisweil.github.io. Stdlib only, Python 3.9+. Exit 1 on any error.

Run from anywhere: python3 scripts/check_site.py
"""
import json
import re
import shutil
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SIBLING = ROOT.parent / "mathisweil"
CV_DOCX = ROOT / "cv" / "mathis-weil-cv.docx"
CV_PDF = DOCS / "assets" / "mathis-weil-cv.pdf"
SITE = "https://mathisweil.github.io/"
ALLOWED_DOCS = {"cv/mathis-weil-cv.docx", "docs/assets/mathis-weil-cv.pdf"}
PUBLISHED_EXT = {".html", ".htm", ".css", ".js", ".png", ".jpg", ".jpeg", ".gif",
                 ".svg", ".ico", ".webp", ".woff2", ".pdf"}
OUTSIDE_DOCS_OK = (".claude/", ".github/", "scripts/", "cv/")
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# Superseded figures and wording from earlier drafts: do not reintroduce them.
# Ask Mathis before changing or narrowing any pattern.
SUPERSEDED = [
    (r"MiniHack[^.]{0,80}\b70(\.0)?\s?%|\b70(\.0)?\s?%[^.]{0,80}\b(MiniHack|win)", "superseded MiniHack win rate"),
    (r"\b9\.3\s?%[^.]{0,60}baseline", "superseded baseline comparison"),
    (r"\b8\.2\s?%[^.]{0,80}(OOD|out-of-distribution|win)|(OOD|out-of-distribution)[^.]{0,80}\b8\.2\s?%", "superseded OOD figure"),
    (r"(highest|best)[^.]{0,30}(OOD|out-of-distribution) transfer", "superseded OOD claim"),
    (r"order of magnitude[^.]{0,40}PPO", "superseded PPO comparison"),
    (r"sole developer of (both|the MiniHack|the Craftax|the planner)", "planner codebases: lead developer"),
    (r"histogram sums", "superseded thesis wording"),
    (r"(TF-IDF|BM25)[^.]{0,60}every (retrieval )?metric", "superseded SkillFindr comparison"),
    (r"Double Intractability", "old paper title"),
    (r"Powering Your Agentic Future", "old white-paper title"),
    (r"Pruned KV Cache Inference", "old evo-memory title"),
    (r"currently[^.]{0,40}\bat Ki\b", "Ki role is past (Jun-Sep 2026)"),
    (r"Graduate visa from September 2026", "old visa wording"),
]
PHONE = [re.compile(r"\+\d{1,3}[\s.-]?\(?\d{1,4}\)?(?:[\s.-]?\d{2,4}){2,4}"),
         re.compile(r"\b0\d{4}\s?\d{6}\b")]


class Page(HTMLParser):
    """Collects what the checks need from docs/index.html in one pass."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
            "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.text, self.attr_text = [], [], []
        self.refs, self.ids, self.imgs, self.gifs, self.cells = [], [], [], [], []
        self.meta, self.jsonld_raw, self.kickers = {}, [], []
        self.h1, self.canonical, self.title = 0, None, ""
        self.tagline, self.footer, self.portrait = "", "", None
        self.hero_links = []

    def _inside(self, tag=None, cls=None, **attrs):
        for t, a in self.stack:
            if tag and t != tag:
                continue
            if cls and cls not in (a.get("class") or "").split():
                continue
            if all(a.get(k) == v for k, v in attrs.items()):
                return True
        return False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        for key in ("alt", "title", "aria-label"):
            if a.get(key):
                self.attr_text.append(a[key])
        for key in ("href", "src"):
            if a.get(key):
                self.refs.append(a[key])
        if a.get("srcset"):
            self.refs += [c.strip().split()[0] for c in a["srcset"].split(",") if c.strip()]
        if tag == "h1":
            self.h1 += 1
        elif tag == "meta" and a.get("content"):
            self.meta[a.get("name") or a.get("property")] = a["content"]
            self.attr_text.append(a["content"])
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "img":
            self.imgs.append(a)
            if self._inside("span", cls="portrait"):
                self.portrait = a.get("src")
        elif tag == "source" and (a.get("srcset") or "").endswith(".gif"):
            self.gifs.append(a["srcset"])
        elif tag == "i" and self._inside("div", cls="plan"):
            self.cells.append(a.get("data-d"))
        elif tag == "a" and self._inside("nav", **{"aria-label": "Contact and profiles"}):
            if (a.get("href") or "").startswith("https://"):
                self.hero_links.append(a["href"])
        elif tag == "span" and "kicker" in (a.get("class") or "").split():
            self.kickers.append("")
        if tag not in self.VOID:
            self.stack.append((tag, a))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID and self.stack:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self._inside("script", type="application/ld+json"):
            self.jsonld_raw.append(data)
            return
        if self._inside("script") or self._inside("style"):
            return
        if self._inside("title"):
            self.title += data
            return
        self.text.append(data)
        if self._inside("p", cls="tagline"):
            self.tagline += data
        if self._inside("footer"):
            self.footer += data
        if self._inside("span", cls="kicker") and self.kickers:
            self.kickers[-1] += data


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def jsonld_strings(node):
    if isinstance(node, dict):
        return [s for v in node.values() for s in jsonld_strings(v)]
    if isinstance(node, list):
        return [s for v in node for s in jsonld_strings(v)]
    return [node] if isinstance(node, str) else []


def docx_text(path):
    out = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.endswith(".xml"):
                xml = z.read(name).decode("utf-8", "replace")
                xml = re.sub(r"</w:p>", "\n", xml)
                out.append(re.sub(r"<[^>]+>", "", xml))
    return "\n".join(out)


def pdf_text(path):
    if not shutil.which("pdftotext"):
        return None
    run = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True)
    return run.stdout if run.returncode == 0 else None


def repo_files():
    """Tracked plus untracked, non-ignored files, relative to ROOT."""
    if shutil.which("git") and (ROOT / ".git").exists():
        run = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--cached", "--others",
                              "--exclude-standard"], capture_output=True, text=True)
        if run.returncode == 0:
            return [f for f in run.stdout.splitlines() if (ROOT / f).exists()]
    return [str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
            if p.is_file() and ".git" not in p.parts]


def check_structure(page, files):
    errors = []
    if page.h1 != 1:
        errors.append(f"index.html: expected one <h1>, found {page.h1}")
    dupes = sorted({i for i in page.ids if page.ids.count(i) > 1})
    if dupes:
        errors.append(f"index.html: duplicate ids {dupes}")
    for ref in page.refs:
        if re.match(r"^(https?:|mailto:|#|data:)", ref):
            continue
        if not (DOCS / ref.split("#")[0].split("?")[0]).is_file():
            errors.append(f"index.html: local file not found: {ref}")
    for img in page.imgs:
        missing = [k for k in ("alt", "width", "height") if not img.get(k)]
        if missing:
            errors.append(f"index.html: <img src={img.get('src')}> lacks {missing}")
    srcs = {img.get("src") for img in page.imgs}
    for gif in page.gifs:
        poster = gif[:-4] + "-poster.png"
        if poster not in srcs or not (DOCS / poster).is_file():
            errors.append(f"index.html: {gif} needs its poster {poster} as the <img> fallback")
    if not (DOCS / ".nojekyll").is_file():
        errors.append("docs/.nojekyll is missing (Jekyll would rewrite the site)")
    for f in files:
        parts = Path(f).parts
        if f.startswith("docs/") and any(p.startswith(".") for p in parts) and f != "docs/.nojekyll":
            errors.append(f"{f}: dotfiles under docs/ are published; remove it")
        if f.startswith("docs/") or f.startswith(OUTSIDE_DOCS_OK):
            continue
        if Path(f).suffix.lower() in PUBLISHED_EXT or "assets" in parts:
            errors.append(f"{f}: published files belong in docs/ (only docs/ is served)")
    errors += check_sitemap(page)
    robots = (DOCS / "robots.txt").read_text() if (DOCS / "robots.txt").is_file() else ""
    if f"Sitemap: {SITE}sitemap.xml" not in robots:
        errors.append("docs/robots.txt: missing the Sitemap: line")
    return errors


def check_sitemap(page):
    path = DOCS / "sitemap.xml"
    try:
        tree = ElementTree.parse(path)
    except (OSError, ElementTree.ParseError) as exc:
        return [f"docs/sitemap.xml: {exc}"]
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    errors, home_lastmod = [], None
    for url in tree.getroot().findall("s:url", ns):
        loc = url.findtext("s:loc", "", ns)
        rel = loc[len(SITE):] if loc.startswith(SITE) else None
        if rel is None or not (DOCS / (rel or "index.html")).is_file():
            errors.append(f"docs/sitemap.xml: <loc> {loc} does not map to a file in docs/")
        if rel == "":
            home_lastmod = url.findtext("s:lastmod", "", ns)
    m = re.search(r"updated (\w+) (\d{4})", norm(page.footer))
    if not m or m.group(1) not in MONTHS:
        errors.append("index.html: footer must read 'updated <Month YYYY>'")
    elif home_lastmod and home_lastmod[:7] != f"{m.group(2)}-{MONTHS.index(m.group(1)) + 1:02d}":
        errors.append(f"footer says '{m.group(0)}' but sitemap lastmod for / is {home_lastmod}; "
                      "set both to today when visible content changes")
    return errors


def check_pairs(page):
    errors, m = [], page.meta
    pairs = [("<title>", norm(page.title), "og:title", m.get("og:title")),
             ("meta description", m.get("description"), "og:description", m.get("og:description"))]
    for a_name, a, b_name, b in pairs:
        if norm(a) != norm(b):
            errors.append(f"index.html: {a_name} and {b_name} must be identical")
    try:
        graph = json.loads("".join(page.jsonld_raw))["@graph"]
        website = next(n for n in graph if n.get("@type") == "WebSite")
        profile = next(n for n in graph if n.get("@type") == "ProfilePage")
        person = profile["mainEntity"]
    except (ValueError, KeyError, StopIteration) as exc:
        return errors + [f"index.html: JSON-LD missing or malformed ({exc})"]
    urls = {"canonical": page.canonical, "og:url": m.get("og:url"), "WebSite.url": website.get("url"),
            "ProfilePage.url": profile.get("url"), "Person.url": person.get("url")}
    for name, value in urls.items():
        if value != SITE:
            errors.append(f"index.html: {name} must be {SITE} (is {value})")
    if website.get("name") != m.get("og:site_name"):
        errors.append("index.html: JSON-LD WebSite name must equal og:site_name")
    if person.get("sameAs") != page.hero_links:
        errors.append("index.html: JSON-LD sameAs must list the hero https links in the same order")
    if norm(person.get("description")) != norm(page.tagline):
        errors.append("index.html: JSON-LD Person description must equal the tagline text")
    if person.get("image") != SITE + (page.portrait or ""):
        errors.append("index.html: JSON-LD Person image must be the portrait <img> src")
    return errors


def check_plan(page):
    if len(page.cells) != 64 or not all(c in list("01234567") for c in page.cells):
        return [f"index.html: the plan panel needs exactly 64 <i data-d=0-7> cells (found {len(page.cells)}); "
                "script.js depends on it"]
    return []


def check_text(sources):
    errors = []
    for name, text in sources.items():
        flat = norm(text)
        for pattern, label in SUPERSEDED:
            hit = re.search(pattern, flat, re.I)
            if hit:
                errors.append(f"{name}: {label}: '{hit.group(0)[:90]}'. Ask Mathis; never edit the pattern list "
                              "without his OK")
        for pattern in PHONE:
            if pattern.search(flat):
                errors.append(f"{name}: looks like a phone number; phone numbers are never published")
    return errors


def check_cv(files):
    errors = []
    extra = sorted(f for f in files if Path(f).suffix.lower() in (".docx", ".pdf") and f not in ALLOWED_DOCS)
    if extra:
        errors.append(f"only the public CV may be in this repo; remove {extra}")
    texts = {"cv docx": docx_text(CV_DOCX) if CV_DOCX.is_file() else None, "cv pdf": pdf_text(CV_PDF)}
    for name, text in texts.items():
        if text and not re.search(r"REFERENCES\s*Available on request\.", text):
            errors.append(f"{name}: the REFERENCES section must read 'Available on request.'")
    return errors, texts


def exif_segments(path):
    data = path.read_bytes()
    found = []
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 4 <= len(data) and data[i] == 0xFF:
            marker, length = data[i + 1], int.from_bytes(data[i + 2:i + 4], "big")
            if marker == 0xDA:
                break
            payload = data[i + 4:i + 2 + length]
            if marker == 0xE1 and payload.startswith(b"Exif\x00\x00"):
                found.append("EXIF")
            if marker == 0xE1 and b"GPS" in payload:
                found.append("GPS")
            i += 2 + length
    elif data[:8] == b"\x89PNG\r\n\x1a\n":
        i = 8
        while i + 8 <= len(data):
            length, kind = int.from_bytes(data[i:i + 4], "big"), data[i + 4:i + 8]
            if kind == b"eXIf":
                found.append("EXIF")
            i += 12 + length
    return found


def check_images():
    errors = []
    for path in sorted(DOCS.rglob("*")):
        if path.suffix.lower() in (".jpg", ".jpeg", ".png"):
            found = exif_segments(path)
            if found:
                errors.append(f"{path.relative_to(ROOT)}: contains {sorted(set(found))} metadata; strip it "
                              "(see the update-site skill, portrait recipe)")
    return errors


def warnings(page):
    out = []
    shared = SIBLING / "assets"
    if shared.is_dir():
        for theirs in shared.iterdir():
            ours = DOCS / "assets" / theirs.name
            if ours.is_file() and ours.read_bytes() != theirs.read_bytes():
                out.append(f"docs/assets/{theirs.name} differs from ../mathisweil/assets/ "
                           "(sibling clone may be stale: pull it; never copy the stale file over)")
    for k in page.kickers:
        if len(norm(k)) > 36:
            out.append(f"kicker over 36 characters may overflow on phones: '{norm(k)}'")
    if len(page.meta.get("description", "")) > 160:
        out.append("meta description is over 160 characters; search results may truncate it")
    if shutil.which("tidy"):
        version = subprocess.run(["tidy", "-v"], capture_output=True, text=True).stdout
        if re.search(r"version [5-9]", version):
            run = subprocess.run(["tidy", "-q", "-e", str(DOCS / "index.html")], capture_output=True, text=True)
            notes = [l for l in run.stderr.splitlines() if l.strip() and "trimming empty <i>" not in l]
            out += [f"tidy: {l}" for l in notes]
    return out


def main():
    html_path = DOCS / "index.html"
    if not html_path.is_file():
        print("check_site: docs/index.html not found", file=sys.stderr)
        return 1
    page = Page()
    page.feed(html_path.read_text(encoding="utf-8"))
    files = repo_files()
    errors = check_structure(page, files) + check_pairs(page) + check_plan(page)
    cv_errors, cv_texts = check_cv(files)
    try:
        ld = jsonld_strings(json.loads("".join(page.jsonld_raw)))
    except ValueError:
        ld = []
    sources = {"index.html": "\n".join(page.text + page.attr_text + ld)}
    sources.update({k: v for k, v in cv_texts.items() if v})
    for rel in ["README.md", "CLAUDE.md"] + [str(p.relative_to(ROOT)) for p in (ROOT / ".claude").rglob("*")
                                             if p.suffix in (".md", ".json")]:
        if (ROOT / rel).is_file():
            sources[rel] = (ROOT / rel).read_text(encoding="utf-8")
    if (SIBLING / "README.md").is_file():
        sources["../mathisweil/README.md"] = (SIBLING / "README.md").read_text(encoding="utf-8")
    errors += cv_errors + check_text(sources) + check_images()
    warns = warnings(page)
    skipped = [] if cv_texts["cv pdf"] is not None else ["CV PDF text (pdftotext not installed)"]
    for w in warns:
        print(f"warning: {w}")
    for s in skipped:
        print(f"skipped: {s}")
    for e in errors:
        print(f"error: {e}")
    print(f"check_site: {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
