# Publication figure gallery

This folder is for images you have permission to re-use on your website.

Suggested workflow:

1. Export a figure panel (or a simplified version) as `webp`/`png` from your own source files.
2. Put the image in `assets/figures/`.
3. Add an entry to `assets/figures/figures.json`:

```json
{
  "src": "assets/figures/my-figure.webp",
  "alt": "Electron tomogram showing synaptic architecture",
  "caption": "Transsynaptic elements revealed by electron tomography.",
  "link": "https://pubmed.ncbi.nlm.nih.gov/PMID_HERE/",
  "credit": "Figure adapted from Cole et al."
}
```

Notes:
- Many journal figures are copyrighted even if you are an author. Prefer images you control (author manuscript figures, CC-licensed open access figures, or redrawn/adapted schematics).
- If you want, we can add a per-image license field and display it in the UI.

Optional automation:
- If a paper is available in PubMed Central under a Creative Commons license, you can try:
  ```bash
  python3 scripts/fetch_pmc_figures.py --only-cc
  ```
  This downloads the first figure from each CC-licensed PMC paper listed in `assets/pubmed.json` and updates `assets/figures/figures.json`.
