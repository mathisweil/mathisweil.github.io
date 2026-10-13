# mathisweil.github.io

Personal site, live at https://mathisweil.github.io. Plain HTML, CSS and one small script, no build step; GitHub Pages serves the repository root (`.nojekyll` keeps Jekyll out of the way).

- All copy lives in `index.html`. The profile README at github.com/mathisweil/mathisweil is the source of truth: copy a changed sentence from there into the page, never the other way round, and keep each fact in one place.
- The GIFs and the CV in `assets/` are byte copies of `mathisweil/assets/`. After replacing a GIF, re-export its poster with `convert "assets/<name>.gif[0]" -strip assets/<name>-poster.png`; `og.png` is the MiniHack poster at 200% with a point filter.
- Portrait: `assets/portrait.jpg` (390x390, no EXIF or GPS). Before any upload, strip metadata with `exiftool -all= -tagsfromfile @ -icc_profile -overwrite_original <file>`.
- Search Console: `google9877d2b0db4033da.html` and the `google-site-verification` meta tag verify the property, and Bing through it. Keep both.
- Structured data: the JSON-LD in `<head>` repeats the tagline, the portrait path and the hero profile links. Update it when those change.
- Sitemap: bump a URL's `lastmod` in `sitemap.xml` only when that page or the CV changes in substance.
- Fonts in `assets/fonts/` are self-hosted STIX Two Text and Source Code Pro under the SIL Open Font License (licence files alongside).
- Lighthouse flags the 1.4 MB Craftax GIF as a video opportunity. Accepted: the GIFs are the visual backbone and stay byte-identical to the profile.
