#!/usr/bin/env python3
"""Edit and publish the CV. Stdlib only, Python 3.9+; publishing needs LibreOffice.

  python3 scripts/cv.py dump [DOCX]
  python3 scripts/cv.py edit [DOCX] --old "exact paragraph text" --new "text with **bold**"
  python3 scripts/cv.py edit [DOCX] --after "anchor text" [--like "template text"] --new "..."
  python3 scripts/cv.py publish          export cv/mathis-weil-cv.docx, verify, install the PDF
  python3 scripts/cv.py export DOCX      private variants only: PDF next to the DOCX, never in this repo

DOCX defaults to cv/mathis-weil-cv.docx. Paragraph formatting (style, bullets, run
properties) is copied from the edited paragraph, or from --like. Paragraphs that
contain hyperlinks (the header line) are refused: their links would be lost.
LibreOffice drops docx links without a character style, so header links use the
neutral "HeaderLink" style already defined in the public CV.
"""
import argparse
import datetime
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DOCX = ROOT / "cv" / "mathis-weil-cv.docx"
BUILD_PDF = ROOT / "cv" / "build" / "mathis-weil-cv.pdf"
TARGETS = [ROOT / "docs" / "assets" / "mathis-weil-cv.pdf", ROOT.parent / "mathisweil" / "assets" / "mathis-weil-cv.pdf"]
SITEMAP = ROOT / "docs" / "sitemap.xml"
PHONE = [re.compile(r"\+\d{1,3}[\s.-]?\(?\d{1,4}\)?(?:[\s.-]?\d{2,4}){2,4}"), re.compile(r"\b0\d{4}\s?\d{6}\b")]
PAGES = 2
TITLE = "Mathis Weil, Curriculum Vitae"
PARA = re.compile(r"<w:p[ >].*?</w:p>|<w:p/>", re.S)
RUN = re.compile(r"<w:r[ >].*?</w:r>", re.S)


def fail(msg):
    sys.exit(f"cv.py: {msg}")


def read_doc(path):
    with zipfile.ZipFile(path) as z:
        return z.read("word/document.xml").decode("utf-8")


def write_doc(path, xml):
    fd, tmp = tempfile.mkstemp(suffix=".docx", dir=path.parent)
    os.close(fd)
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w") as zout:
        for item in zin.infolist():
            data = xml.encode("utf-8") if item.filename == "word/document.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    shutil.move(tmp, path)


def text_of(p):
    return "".join(html.unescape(t) for t in re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S))


def rpr_of(run):
    m = re.search(r"<w:rPr>.*?</w:rPr>|<w:rPr/>", run, re.S)
    return m.group(0) if m else ""


def is_bold(rpr):
    return "<w:b/>" in rpr


def make_run(text, rpr):
    return f'<w:r>{rpr}<w:t xml:space="preserve">{html.escape(text, quote=False)}</w:t></w:r>'


def rebuild(template, marked):
    """New paragraph XML with the template's pPr and run formatting; **x** marks bold."""
    runs = RUN.findall(template)
    plain = next((rpr_of(r) for r in runs if not is_bold(rpr_of(r))), "")
    bold = next((rpr_of(r) for r in runs if is_bold(rpr_of(r))), "")
    if not bold:
        bold = "<w:rPr><w:b/><w:bCs/></w:rPr>" if plain in ("", "<w:rPr/>") else plain.replace("<w:rPr>", "<w:rPr><w:b/><w:bCs/>", 1)
    head = template[: template.index(runs[0])] if runs else template[: template.index("</w:p>")]
    parts = re.split(r"\*\*", marked)
    return head + "".join(make_run(t, bold if i % 2 else plain) for i, t in enumerate(parts) if t) + "</w:p>"


def find(xml, text, what):
    hits = [p for p in PARA.findall(xml) if text_of(p) == text]
    if len(hits) != 1:
        fail(f"{what}: expected exactly one paragraph with that text, found {len(hits)} (use `dump` to copy it exactly)")
    return hits[0]


def cmd_dump(args):
    for i, p in enumerate(PARA.findall(read_doc(args.docx))):
        t = text_of(p)
        if not t.strip():
            continue
        marked = "".join(f"**{text_of(r)}**" if is_bold(rpr_of(r)) else text_of(r) for r in RUN.findall(p))
        bullet = "•" if "<w:numPr>" in p else " "
        link = " [links]" if "<w:hyperlink" in p else ""
        print(f"[{i:03d}] {bullet} {marked}{link}")


def cmd_edit(args):
    xml = read_doc(args.docx)
    if args.old:
        target = find(xml, args.old, "--old")
        if "<w:hyperlink" in target:
            fail("that paragraph contains hyperlinks (the header); editing it here would drop them")
        xml = xml.replace(target, rebuild(target, args.new), 1)
    else:
        anchor = find(xml, args.after, "--after")
        template = find(xml, args.like, "--like") if args.like else anchor
        if "<w:hyperlink" in template:
            fail("the template paragraph contains hyperlinks; pick another --like")
        xml = xml.replace(anchor, anchor + rebuild(template, args.new), 1)
    write_doc(args.docx, xml)
    print(f"cv.py: edited {args.docx}")


def soffice():
    for exe in ("soffice", "libreoffice"):
        if shutil.which(exe):
            return shutil.which(exe)
    mac = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if os.path.exists(mac):
        return mac
    fail("LibreOffice not found; the CV cannot be exported here. Hand the `cv.py edit` commands to a local session")


def convert(docx, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        run = subprocess.run([soffice(), "--headless", f"-env:UserInstallation=file://{profile}",
                              "--convert-to", "pdf", "--outdir", str(outdir), str(docx)],
                             capture_output=True, text=True)
    pdf = outdir / (docx.stem + ".pdf")
    if run.returncode != 0 or not pdf.is_file():
        fail(f"LibreOffice export failed: {run.stderr.strip()[:300]}")
    return pdf


def pdf_string(raw):
    if raw.startswith(b"<"):
        data = bytes.fromhex(raw[1:-1].decode())
    else:
        data = re.sub(rb"\\(.)", rb"\1", raw[1:-1])
    return data[2:].decode("utf-16-be") if data.startswith(b"\xfe\xff") else data.decode("latin-1")


def pdf_title(data):
    """The document title lives in the Info dictionary (the object with /Producer), not the outline."""
    for obj in re.finditer(rb"\sobj(.*?)endobj", data, re.S):
        body = obj.group(1)
        if b"/Producer" in body:
            m = re.search(rb"/Title\s*(<[0-9A-Fa-f]*>|\((?:\\.|[^\\)])*\))", body)
            return pdf_string(m.group(1)) if m else ""
    return ""


def pdf_facts(pdf):
    data = pdf.read_bytes()
    return {"pages": len(re.findall(rb"/Type\s*/Page(?!s)", data)),
            "title": pdf_title(data),
            "links": len(set(re.findall(rb"/URI\s*\(([^)]*)\)", data))),
            "font": bool(re.search(rb"/BaseFont\s*/[A-Z]{6}\+(Carlito|Calibri)", data))}


def docx_text(path):
    return "\n".join(text_of(p) for p in PARA.findall(read_doc(path)))


def cmd_publish(_args):
    text = docx_text(PUBLIC_DOCX)
    if any(p.search(text) for p in PHONE):
        fail("the public CV contains a phone number")
    if not re.search(r"REFERENCES\s*Available on request\.", text):
        fail("the public CV must say 'REFERENCES / Available on request.'")
    if BUILD_PDF.exists():
        BUILD_PDF.unlink()
    pdf = convert(PUBLIC_DOCX, BUILD_PDF.parent)
    pdf.rename(BUILD_PDF)
    facts = pdf_facts(BUILD_PDF)
    problems = []
    if facts["pages"] != PAGES:
        problems.append(f"{facts['pages']} pages (must be {PAGES}: propose a cut to Mathis; never change fonts, margins or spacing)")
    if facts["title"] != TITLE:
        problems.append(f"PDF title is '{facts['title']}' (docProps/core.xml dc:title must be '{TITLE}')")
    if facts["links"] < 4:
        problems.append(f"only {facts['links']} links (header links need the HeaderLink character style)")
    if not facts["font"]:
        problems.append("Carlito/Calibri not embedded (fonts substituted: layout is not trustworthy on this machine)")
    if problems:
        fail("export rejected: " + "; ".join(problems) + f". Inspect {BUILD_PDF}")
    installed = []
    for target in TARGETS:
        if target.parent.is_dir():
            shutil.copyfile(BUILD_PDF, target)
            installed.append(target)
    if any(t.read_bytes() != BUILD_PDF.read_bytes() for t in installed):
        fail("installed copies differ from the build")
    today = datetime.date.today().isoformat()
    sitemap = SITEMAP.read_text()
    new = re.sub(r"(<loc>[^<]*mathis-weil-cv\.pdf</loc><lastmod>)[^<]*(</lastmod>)", rf"\g<1>{today}\g<2>", sitemap)
    SITEMAP.write_text(new)
    print(f"cv.py: published {facts['pages']} pages, {facts['links']} links, title '{facts['title']}'")
    for t in installed:
        print(f"  -> {t}")
    if len(installed) < len(TARGETS):
        print("  note: ../mathisweil not present; copy the PDF there from a session that has it")
    print(f"  sitemap CV lastmod -> {today}")


def cmd_export(args):
    docx = args.docx.resolve()
    if docx == PUBLIC_DOCX.resolve():
        fail("use `publish` for the public CV")
    if ROOT in docx.parents:
        fail("private CV variants never live in this repo")
    pdf = convert(docx, docx.parent)
    facts = pdf_facts(pdf)
    print(f"cv.py: exported {pdf} ({facts['pages']} pages, {facts['links']} links, title '{facts['title']}')")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dump")
    d.add_argument("docx", nargs="?", type=Path, default=PUBLIC_DOCX)
    e = sub.add_parser("edit")
    e.add_argument("docx", nargs="?", type=Path, default=PUBLIC_DOCX)
    g = e.add_mutually_exclusive_group(required=True)
    g.add_argument("--old")
    g.add_argument("--after")
    e.add_argument("--like")
    e.add_argument("--new", required=True)
    sub.add_parser("publish")
    x = sub.add_parser("export")
    x.add_argument("docx", type=Path)
    args = ap.parse_args()
    {"dump": cmd_dump, "edit": cmd_edit, "publish": cmd_publish, "export": cmd_export}[args.cmd](args)


if __name__ == "__main__":
    main()
