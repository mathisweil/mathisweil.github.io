# mathisweil.github.io

Mathis Weil's personal site, https://mathisweil.github.io. GitHub Pages serves `docs/` only: plain HTML, CSS and one small script; no build step, no frameworks, no npm. For any content change (status, job, paper, project, award, CV, photo, GIF) use the `update-site` skill.

## Facts
- Facts come only from the profile README (github.com/mathisweil/mathisweil), the public CV (`cv/mathis-weil-cv.docx`), or Mathis in the session. Never invent, round or extrapolate a number.
- The site and the profile README must agree on shared facts: change both when both are reachable, otherwise change one and hand over the exact text for the other.
- Text marked byte-identical in `.claude/skills/update-site/where-facts-live.md` is copied verbatim; any other difference between site and profile README is intentional, so do not align it.
- Never publish: phone numbers, referees, Ki-side advisor names (the UCL supervisor, Prof Philip Treleaven, is public), Ki-book data or a link to Ki code (thesis results use public freMTPL data only), the private CV variants. `scripts/check_site.py` blocks superseded claims; ask Mathis before changing any of its patterns.

## Page
- The hero summarises; the sections hold detail. A fact may appear once in each, never twice within a section. Do not remove an existing repeat unless asked.
- Reuse the existing components (copy the nearest existing entry). No new sections, cards, navigation or pages unless Mathis asks.

## Commands
- Check: `python3 scripts/check_site.py` (also runs before every commit and push, and in CI).
- Preview: `python3 -m http.server -d docs 8000`.
- CV: `python3 scripts/cv.py --help` (dump, edit, publish).

## Deploy
- Mathis confirms every commit and push. Stage files by name, never `git add -A`; never force-push.
- Local: `git push origin main`, then confirm the Pages build (`gh api repos/mathisweil/mathisweil.github.io/pages/builds/latest --jq '.status,.commit'`) and the live page.
- claude.ai/code (`CLAUDE_CODE_REMOTE=true`): attach only this repo, push a branch, open the PR with the claude.ai button or `gh api -X POST repos/mathisweil/mathisweil.github.io/pulls -f head=<branch> -f base=main -f title=...` (`gh pr` fails there). Mathis merges.
- Files under `.github/workflows/` are pushed over SSH from a local machine, never from claude.ai/code (the gh token lacks the `workflow` scope).
