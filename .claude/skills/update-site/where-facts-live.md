# Where each fact lives

Locations and formats only. Site = `docs/index.html`; Profile = `../mathisweil/README.md` (repo mathisweil/mathisweil); CV = `cv/mathis-weil-cv.docx` (published as `docs/assets/mathis-weil-cv.pdf` and `../mathisweil/assets/mathis-weil-cv.pdf`, byte-identical). "Manual" places need Mathis's own login.

## Status, availability, visa
- Site: `p.status` in the hero ("**Open to ... in London.** Eligible for the UK Graduate visa, no sponsorship needed."); the meta description and `og:description` (identical, ≤ 160 characters); the lede `p.lede` ("I have just finished ...") goes stale with a new job.
- Profile: the status paragraph under the link row (same sentences); the opening paragraph; a News bullet `- **Mon YYYY** · ...` at the top of `## News`.
- CV: header line 2 "Curriculum Vitae | Eligible for the UK Graduate visa, no sponsorship needed".
- Wording is fixed: "Eligible for" (not "holding") the visa. Ask before changing it.
- Manual: LinkedIn headline and Open-to-work.

## Roles and dates
- Site: first `dl.dated` in `#background`, newest first: `<dt>Jun–Sep 2026</dt><dd><strong>Title</strong>, Org · one line<small>optional sub-line</small></dd>`.
- Profile: `## Background` bullets `- **Title**, Org, Jun–Sep 2026 · one line`.
- CV: `Title, Org | Jun 2026 - Sep 2026` (bold title run), an italic location or context line, then bullets, under RESEARCH EXPERIENCE, TEACHING EXPERIENCE or EXPERIENCE.
- Current roles: Machine Learning Researcher, Ki (Jun–Sep 2026, past tense; MSc thesis research embedded in the underwriting team); Postgraduate Teaching Assistant, UCL (Sep 2025 – Jun 2026, four modules, 280+ students); Lab demonstrator, QMUL (Sep 2024 – May 2025, 400+ undergraduates).
- Manual: LinkedIn Experience, OpenReview career history, ORCID employment, GitHub `company` field.

## Education and thesis status
- Site: `#background` rows for the MSc (thesis submitted September 2026, result pending; module marks) and BSc (First Class Honours, 83%); the thesis entry `article#thesis` in `#research`.
- Profile: `## Background`; the thesis section under `## Research`; News.
- CV: EDUCATION (thesis line, module marks); never state an MSc classification until Mathis gives it.

## The paper
- Site `article#paper`: title, kicker "NeurIPS 2026 · BeNTo", authors (`<strong>Mathis Weil</strong>`, `*` for equal contribution), venue line, links row (Paper, Code, Checkpoints), findings, Role line, two figures, BibTeX.
- Author order is fixed: Muhammad Ali Khan*, Mathis Weil*, Ahmet H. Güzel, Jack Parker-Holder, Ilija Bogunovic (`*` equal contribution), even though the local camera-ready PDF prints Weil first.
- Profile: `## Research` section, News; CV: PUBLICATIONS and the "Discrete Diffusion Planners on Craftax & MiniHack | Jan 2026 - Sep 2026" entry.
- Byte-identical BibTeX in six places: Site (`<details>` in `#paper`), Profile, `../craftax-ReMDM-planner/README.md`, `../minihack-ReMDM-planner/README.md`, and the Hugging Face cards `mathisweil/remdm-craftax-checkpoints` and `mathisweil/remdm-minihack-checkpoints`. Also `CITATION.cff` in both code repos. Canonical entry:

```bibtex
@inproceedings{khan2026returnweighted,
  title     = {Return-Weighted {ELBO} Fine-Tuning Degrades Masked Diffusion Planners},
  author    = {Muhammad Ali Khan and Mathis Weil and Ahmet H. G{\"u}zel and Jack Parker-Holder and Ilija Bogunovic},
  booktitle = {Beyond Next Token Prediction: Diffusion and Flow Models for Next-Generation Decoding},
  year      = {2026},
  url       = {https://openreview.net/forum?id=VGyjG8Gy29}
}
```
- With an arXiv ID add `eprint = {<id>}`, `archivePrefix = {arXiv}` and `primaryClass = {<from the listing>}` to every copy; `url` stays OpenReview unless Mathis says otherwise.
- GitHub: descriptions and homepage fields of the two code repos; the GitHub bio mentions the paper.
- Manual: Google Scholar (the co-author shows as "AH Gözel" there; Mathis can fix it), OpenReview, LinkedIn Publications, ORCID works.

## The thesis
- Site `article#thesis`; Profile thesis section; CV EDUCATION and the Ki entry.
- Results use public freMTPL data only; no Ki-book data, schema or figures; no code link ("private to Ki; access on request through Ki").

## Projects
- Site: `ul.projects` rows `li.entry` in `#projects` (evo-memory, SkillFindr, BidBird); order is Mathis's choice. A project with a GIF goes in `#research` as an `article.entry` with a figure, or in Other projects without one: ask.
- Profile: `## Other projects` one-line bullets `- **[Name](url)** · text`.
- CV: RESEARCH PROJECTS or PROJECTS.
- Repo descriptions and homepage fields on GitHub (`gh repo edit`, after Mathis approves the text).
- Intentional differences: the site keeps more metrics than the profile (e.g. SkillFindr MAP@20 and latency); keep them.

## Awards
- Site: the "Awards" row of the second `dl.dated` (items joined by " · "); BidBird's 1st place also appears in its project row.
- Profile: no awards section; awards appear inline in Background and projects.
- CV: AWARDS bullets (bold name, plain rest).

## Skills, interests, languages
- Site: the Skills, Interests and Languages rows; CV: SKILLS and RESEARCH INTERESTS. The profile has none.

## Links and identity
- Site: hero `nav[aria-label="Contact and profiles"]` (Email and CV use `a.primary`), JSON-LD `sameAs` (same https links, same order), footer, canonical and `og:url`.
- Profile: the link row at the top (Website, Email, LinkedIn, Google Scholar, OpenReview, Hugging Face, CV).
- CV header line 1: email, mathisweil.github.io, LinkedIn, GitHub (hyperlinks; edit by hand only).
- Tagline: Site `p.tagline` = JSON-LD `description`; Profile line under the title; GitHub bio; the `mathisweil` repo description.
- Location "London": title and `og:title`, status, footer, Profile, CV header, GitHub location.
- Manual: LinkedIn website, Scholar homepage, OpenReview homepage, Hugging Face homepage, ORCID websites.

## Images
- Portrait `docs/assets/portrait.jpg` (390x390, no metadata) = JSON-LD `image`.
- GIFs and posters: `docs/assets/<name>.gif` and `<name>-poster.png`; the three paper and thesis GIFs are byte-identical with `../mathisweil/assets/`. Alt texts and captions: Site and Profile versions differ slightly on purpose; keep each as it is unless the GIF changes.
- `docs/assets/og.png` is the MiniHack poster at 200 % (point filter) and is described by `og:image:alt`; change only if asked.
