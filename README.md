# mathisweil.github.io

Personal site of Mathis Weil, live at https://mathisweil.github.io. Plain HTML, CSS and one small script with no build step. GitHub Pages serves the `docs/` folder only, so nothing else in this repo is published.

- **Edit**: page copy lives in `docs/index.html`; images, GIFs and the CV PDF in `docs/assets/`. Uploading through GitHub's web UI? Put files in `docs/assets/`, never at the root.
- **Check**: `python3 scripts/check_site.py` (Python 3.9+, no dependencies). It also runs before every commit and push in Claude Code and on every push in GitHub Actions.
- **CV**: the public CV source is `cv/mathis-weil-cv.docx`; `python3 scripts/cv.py publish` exports it with LibreOffice and installs the PDF.
- **With Claude Code**: open a session in this repo (or on claude.ai/code with only this repo attached) and ask for the change, e.g. "add my new job to the website". `CLAUDE.md` holds the rules and the `update-site` skill the procedure. A fresh clone asks once to trust the folder; accept it so the checks run.
- **Search Console**: `docs/google9877d2b0db4033da.html` and the `google-site-verification` meta tag verify the property (and Bing through it). Keep both.
- **Fonts**: `docs/assets/fonts/` holds self-hosted STIX Two Text and Source Code Pro under the SIL Open Font License.
- Lighthouse flags the 1.4 MB Craftax GIF as a video opportunity; accepted, since the GIFs stay byte-identical to the profile README's.
