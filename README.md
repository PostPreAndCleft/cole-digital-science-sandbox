# cole-digital-science-sandbox

Temporary lab-style personal academic website, designed to be lightweight and easy to remove later.

## Pages
- `index.html` (Home)
- `about.html`
- `publications.html`
- `projects.html`
- `seminars.html`
- `cv.html`
- `contact.html`

Note: A `members.html` page is planned but not included yet.

## Archives
To capture static snapshots (and keep a Git tag), use:

```bash
python3 scripts/archive_pages.py --pages linkedin.html --label job
git tag -a job-2026-02-07 -m "Job-specific snapshot"
```

Snapshots are saved under `archives/` with link rewrites so they work from that folder.

## Local preview
Open `index.html` directly in a browser, or use a simple local server:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

If port `8000` is unavailable (common in restricted environments), pick another port, for example:

```bash
python3 -m http.server 8085
```

## GitHub Pages deployment
1. Push this repo to GitHub.
2. In the repo, go to **Settings → Pages**.
3. Under **Build and deployment**, choose:
   - Source: **Deploy from a branch**
   - Branch: **main** (or `master`), folder **/ (root)**
4. Click **Save**.
5. Wait a minute for GitHub Pages to build. The site will be available at:
   `https://<your-username>.github.io/<repo-name>/`

## Customize
- Update the placeholder text in each HTML file.
- Replace placeholder DOIs, ORCID, and PDF links in `publications.html` and `cv.html`.
- Edit the color palette in `assets/styles.css` (CSS variables at the top).

## PubMed-synced publications
This site can render a publications list from `assets/pubmed.json`.

1. Run (requires network access):
   ```bash
   python3 scripts/fetch_pubmed.py --query 'Cole AA[Author]'
   ```
2. Refresh `publications.html` and the "PubMed list" section updates.

Tip: If PubMed mixes in other “Cole” authors, use a more specific query (author initials, affiliations, keywords, or ORCID if you have one).
In restricted environments (like this Codex session), you may need to approve network access before the script can contact NCBI.

## Publication figure gallery
Drop images you have permission to re-use into `assets/figures/` and list them in `assets/figures/figures.json`.

If a paper is in PubMed Central under a Creative Commons license, you can also try `python3 scripts/fetch_pmc_figures.py --only-cc`.

## Project status (return here)
- Current state: full static site scaffold is live with a homepage publication carousel, seminar playlist randomizer, and a publication figure gallery.
- Content workflow:
  - Figures: update `assets/figures/figures.json` and add/remove images in `assets/figures/`.
  - Carousel: edit featured paper takeaways in `assets/featured_publications_data.js`.
  - Seminars: update `assets/fars_playlist_data.js` (generated from CSVs) and `assets/seminars.js` for UI.
  - Publications: update `assets/pubmed.json` (optionally via `scripts/fetch_pubmed.py`).
- Publishing checklist: keep `references/` private (it is ignored by `.gitignore`).

## License
Content and code are provided under the CC0 license unless replaced with your own.
