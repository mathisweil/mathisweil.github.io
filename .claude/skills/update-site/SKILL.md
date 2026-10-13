---
name: update-site
description: Update Mathis Weil's website mathisweil.github.io (his portfolio / personal page). Use for any request to add, change or remove content on the site, such as availability or job status, a new job or role, a paper's status or arXiv link, a new project, an award or news item, skills, profile links, the CV PDF, the portrait photo or a GIF, and to keep the GitHub profile README and the public CV in sync with the site. Covers finding every place a fact lives, asking only for missing facts, editing, checking, committing with Mathis's confirmation, deploying and verifying the live site.
argument-hint: "[what to change]"
---

# Update the website

Read `CLAUDE.md` first if it is not in context. `where-facts-live.md` (next to this file) lists every place each fact lives, the format used in each, and which text is byte-identical across places.

## 0. Start clean
- `git status` and `git pull --ff-only` here, and in `../mathisweil` (the profile README repo) if that clone exists. Stop and ask if either has changes you did not make.
- Cloud mode if `CLAUDE_CODE_REMOTE=true` (claude.ai/code): only this repo is reachable and LibreOffice, ImageMagick and Chrome are absent. Edit `docs/` only: never `cv/` (`cv.py edit` refuses without LibreOffice) and never other repos. Read the profile README with `curl -s https://raw.githubusercontent.com/mathisweil/mathisweil/main/README.md` so your hand-over gives its exact new text. See section 7.
- Before the first commit in a new environment, `git config user.email` must be `mathis.weil@outlook.com` or Mathis's GitHub noreply address; otherwise stop and ask.

## 1. Collect the facts, asking once for only what is missing
- **New job or role**: exact title; may the employer be named; start month; location or remote; what happens to the status line ("Open to ... roles") and to the visa sentence (never reword it: keep, change or drop, as Mathis says); a News entry on the profile README; add it to the CV?
- **Paper**: the new link or ID (verify it, section 2); does "Paper" keep pointing at OpenReview?
- **Project**: name; dates; role and team size; one sentence with numbers and where each number comes from; code link; a GIF file path if any; Research band (with a figure) or Other projects (no figure) and its position in the list.
- **Award**: exact name; issuer; month and year; any qualifier ("one of 14"); add it to the CV?
- **Photo or GIF**: a file path or URL. An image pasted into chat cannot be saved byte for byte. In claude.ai/code Mathis uploads the file into `docs/assets/` on the session branch, then `git pull`.
- Word a future-dated fact so it stays true after the date ("ML Engineer at Acme from November 2026") and list the date in your report as something to revisit.
- Numbers come only from Mathis or a source document; quote the source in your report.

## 2. Verify external links and IDs before publishing them
- arXiv: the ID matches `^\d{4}\.\d{4,5}(v\d+)?$` with a YYMM that is not in the future; `curl -s "https://export.arxiv.org/api/query?id_list=<id>"` returns exactly one `<entry>` whose title is the paper's title and whose authors are, in order, Khan, Weil, Güzel, Parker-Holder, Bogunovic. Anything else: stop and ask. If arXiv is unreachable (claude.ai/code), add the link only on Mathis's explicit OK and report it as unverified.
- Other URLs: `curl -sI` returns 200 (openreview.net answers 403 to scripts; that is expected).

## 3. Edit
**Site (`docs/index.html`)**: copy the nearest existing entry of the same kind as the template and reuse its classes. Keep these pairs identical (the check enforces them):
- `<title>` = `og:title`; meta description = `og:description` (≤ 160 characters);
- the tagline text = JSON-LD Person `description`;
- the hero profile links = JSON-LD `sameAs` (same order); the portrait `src` = JSON-LD `image`.

Also:
- Any change to visible text, links or images sets the footer "updated <Month YYYY>" and the sitemap `lastmod` for `/` to today (`docs/sitemap.xml`).
- Kickers (`span.kicker`) stay at 36 characters or fewer; they never wrap.
- Background rows are reverse-chronological. Ranges use a spaced hyphen (`Jun 2026 - Sep 2026`, `2025 - 2026`, `75 to 85%`); Mathis wants no en or em dashes anywhere (the check enforces it).
- Never change `og.png`, `og:image:alt` or the plan panel (64 cells, `script.js` depends on them) unless asked.

**Profile README (`../mathisweil/README.md`)**: same facts in its own format (see `where-facts-live.md`); its News list has no counterpart on the site.

**CV (`cv/mathis-weil-cv.docx`)**: only through `scripts/cv.py`.
- `python3 scripts/cv.py dump` to see paragraphs; `edit --old "<exact text>" --new "<text with **bold**>"` to change one; `edit --after "<anchor>" --like "<template>" --new "..."` to insert one (an award: after and like the last award; a job: three inserts like "Software Engineer, Groupe Prunay | Jul 2024 - Aug 2024", "Louveciennes, France" and its bullet). Ask before moving a section.
- `python3 scripts/cv.py publish` exports, verifies (exactly 2 pages, title, links, fonts, no phone, references "Available on request.") and installs the PDF in `docs/assets/` and `../mathisweil/assets/`, and bumps the CV `lastmod`. Commit the docx and PDF together.
- Over 2 pages: propose a cut to Mathis; never change fonts, margins or spacing. No LibreOffice (claude.ai/code): do not edit the CV; hand over the exact `cv.py` commands.
- The header line holds the links and cannot be edited with `cv.py edit`; ask Mathis.
- The private CV variants live outside this repo (`../cvs/` on the lab machine only): ask before touching them; `cv.py export <path>` writes their PDF next to them; never copy them here.

## 4. Assets
- **Portrait**: keep the path `docs/assets/portrait.jpg`. Strip all metadata and fix rotation in one step:
  `uv run --no-project --with pillow python -c "import sys;from PIL import Image,ImageOps;s=Image.open(sys.argv[1]);i=ImageOps.fit(ImageOps.exif_transpose(s).convert('RGB'),(390,390),centering=(0.5,0.4));i.save(sys.argv[2],quality=88,optimize=True,icc_profile=s.info.get('icc_profile'))" SRC docs/assets/portrait.jpg`
  Read the result to confirm it is upright and well framed. Ask for JPEG or PNG if given HEIC. Off-site photos only Mathis can change: GitHub avatar, LinkedIn, Scholar, OpenReview.
- **GIF**: 840x480, at most 2 MB, the first frame is the poster: `convert "docs/assets/<name>.gif[0]" -strip docs/assets/<name>-poster.png` (or Pillow `Image.open(gif).convert("RGB").save(png)`). Use the `<picture>` figure pattern of an existing figure. Alt text: extract frames (`convert x.gif -coalesce <scratch>/f-%03d.png`), Read a few, describe only what is visible, take numbers only from Mathis, and get the alt text approved. If the GIF also goes on the profile README, copy it byte for byte to `../mathisweil/assets/`.
- Write screenshots and temporary files outside the repo.

## 5. Check
- `python3 scripts/check_site.py` must report 0 errors. Read every warning.
- For layout changes (a new figure, row type or long text), preview at 375 and 1440 px: `python3 -m http.server -d docs 8000 &` then `google-chrome --headless=new --hide-scrollbars --window-size=375,2400 --screenshot=<scratch>/m.png http://localhost:8000/` (macOS: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`), and read the screenshots.

## 6. Commit, deploy, verify
- Show Mathis a short diff summary, then commit (he confirms each commit and push). Stage files by name; one commit per repo.
- Local: `git push origin main`; wait for `gh api repos/mathisweil/mathisweil.github.io/pages/builds/latest --jq '.status,.commit'` to show `built` and the new commit; then `curl -s "https://mathisweil.github.io/?v=$(date +%s)" | grep -F "<new text>"` (the CDN may take up to 10 minutes). For a replaced asset, compare its sha256 with the live file.
- If the push is rejected, `git pull --rebase`, re-run the check, push again. Never force-push.

## 7. claude.ai/code
- Only this repo: edit `docs/` (and text you can verify), run the check, commit, push a branch, open the PR (CLAUDE.md, Deploy). After Mathis merges, verify through the Pages build API; the live site is not reachable from the cloud, so tell Mathis what to look at.
- Do not edit the CV, regenerate images or touch other repos here. End with a hand-over: the exact profile README text, the `cv.py` commands and any other changes owed to a local session.

## 8. Same fact elsewhere (second step, local only)
The paper's BibTeX, links and status also live in the code READMEs, two `CITATION.cff` files and two Hugging Face model cards (`where-facts-live.md`). Show the exact diffs and apply them only after Mathis approves each destination: code repos are pushed with `git -C ../<repo> push https://github.com/mathisweil/<repo>.git main`; Hugging Face needs `hf auth whoami` to print `mathisweil`, then `hf download` / edit / `hf upload`.

## 9. Report
What changed (with sources), what is still owed (hand-overs, dates to revisit), and what only Mathis can update himself: LinkedIn, Google Scholar, OpenReview, ORCID, the GitHub bio and avatar.
