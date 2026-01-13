(() => {
  const pubList = document.getElementById("pubmed-list");
  const pubStatus = document.getElementById("pubmed-status");
  if (!pubList) return;

  const escapeHtml = (value) =>
    String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const renderPublication = (item) => {
    const title = item.title ?? "Untitled";
    const year = item.year ?? "";
    const journal = item.journal ?? "";
    const authors = Array.isArray(item.authors) ? item.authors.join(", ") : "";
    const doi = item.doi ? escapeHtml(item.doi) : null;
    const pmid = item.pmid;
    const pubmedUrl = item.pubmed_url || (pmid ? `https://pubmed.ncbi.nlm.nih.gov/${pmid}/` : null);
    const pmcUrl = item.pmc_url || null;

    const links = [
      pubmedUrl ? `<a href="${escapeHtml(pubmedUrl)}">PubMed</a>` : null,
      doi ? `<a href="https://doi.org/${doi}">DOI</a>` : null,
      pmcUrl ? `<a href="${escapeHtml(pmcUrl)}">PMC</a>` : null,
    ]
      .filter(Boolean)
      .join(" · ");

    return `
      <article class="list-item">
        <h3>${escapeHtml(title)}</h3>
        <p>${escapeHtml(authors)}${authors ? ". " : ""}${year ? `${escapeHtml(year)}. ` : ""}${escapeHtml(journal)}</p>
        <p class="pub-links">${links}</p>
      </article>
    `;
  };

  const loadJson = async (path) => {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  };

  const loadFigures = async () => {
    const grid = document.getElementById("figure-grid");
    const status = document.getElementById("figure-status");
    if (!grid) return;

    try {
      const figuresData = await loadJson("assets/figures/figures.json");
      const figures = Array.isArray(figuresData.figures) ? figuresData.figures : [];
      if (!figures.length) {
        status.textContent = "Add figure images in assets/figures/ and list them in assets/figures/figures.json.";
        return;
      }

      status.textContent = "";
      grid.innerHTML = figures
        .map((fig) => {
          const src = fig.src;
          const alt = fig.alt || fig.caption || "Publication figure";
          const caption = fig.caption || "";
          const link = fig.link || null;
          const credit = fig.credit || null;
          const footer = [credit ? `<span class="muted">${escapeHtml(credit)}</span>` : null, link ? `<a href="${escapeHtml(link)}">Source</a>` : null]
            .filter(Boolean)
            .join(" · ");

          const img = `<img class="figure-img" src="${escapeHtml(src)}" alt="${escapeHtml(alt)}" loading="lazy" />`;
          return `
            <figure class="figure-card">
              ${link ? `<a href="${escapeHtml(link)}">${img}</a>` : img}
              <figcaption>
                <div class="figure-caption">${escapeHtml(caption)}</div>
                ${footer ? `<div class="figure-meta">${footer}</div>` : ""}
              </figcaption>
            </figure>
          `;
        })
        .join("");
    } catch (error) {
      status.textContent = "Figure gallery not configured yet (missing assets/figures/figures.json).";
    }
  };

  const loadPublications = async () => {
    try {
      const data = await loadJson("assets/pubmed.json");
      const items = Array.isArray(data.items) ? data.items : [];
      items.sort((a, b) => (b.year ?? 0) - (a.year ?? 0));

      pubList.innerHTML = items.map(renderPublication).join("");
      pubStatus.textContent = items.length
        ? `Loaded ${items.length} publications from PubMed.`
        : "No PubMed results yet. Update assets/pubmed.json.";
    } catch (error) {
      pubStatus.textContent =
        "PubMed list not generated yet. Run scripts/fetch_pubmed.py to create assets/pubmed.json.";
    }
  };

  loadFigures();
  loadPublications();
})();

