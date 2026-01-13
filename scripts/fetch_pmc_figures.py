#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


def _http_get(url: str, retries: int = 4) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "cole-digital-science-sandbox (scripts/fetch_pmc_figures.py)",
            "Accept": "*/*",
        },
    )

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request) as response:  # nosec - URLs built from trusted PMC IDs
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == retries - 1:
                raise
            retry_after = error.headers.get("Retry-After")
            delay = float(retry_after) if retry_after and retry_after.isdigit() else 1.5 * (attempt + 1)
            time.sleep(delay)

    raise RuntimeError("Unreachable: retries exhausted")


def _text(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    return value or None


def _element_text(node: ET.Element | None) -> str | None:
    if node is None:
        return None
    value = "".join(node.itertext()).strip()
    return value or None


def _find_cc_license(xml_root: ET.Element) -> tuple[str | None, str | None]:
    license_el = None
    for el in xml_root.iter():
        if el.tag.split("}")[-1] == "license":
            license_el = el
            break
    if license_el is None:
        return None, None

    license_url = None
    for key, val in license_el.attrib.items():
        if key.split("}")[-1] == "href":
            license_url = val
            break

    license_text = _element_text(license_el)
    if license_url and "creativecommons.org/licenses/" in license_url:
        return license_url, license_text
    if license_text and "Creative Commons" in license_text:
        return license_url, license_text
    return None, license_text


def _find_first_figure(xml_root: ET.Element) -> tuple[str | None, str | None]:
    for fig in xml_root.iter():
        if fig.tag.split("}")[-1] != "fig":
            continue

        caption = None
        caption_el = None
        for el in fig.iter():
            if el.tag.split("}")[-1] == "caption":
                caption_el = el
                break
        if caption_el is not None:
            caption = _element_text(caption_el)

        href = None
        for el in fig.iter():
            if el.tag.split("}")[-1] != "graphic":
                continue
            for key, val in el.attrib.items():
                if key.split("}")[-1] == "href":
                    href = val
                    break
            if href:
                break

        if href:
            return href, caption

    return None, None


def _safe_filename(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-")
    return value or "figure"


def fetch_figures(pubmed_path: Path, figures_path: Path, out_dir: Path, only_cc: bool) -> int:
    pubmed = json.loads(pubmed_path.read_text(encoding="utf-8"))
    items = pubmed.get("items", [])

    figures_data = {"figures": []}
    if figures_path.exists():
        figures_data = json.loads(figures_path.read_text(encoding="utf-8"))

    figures = list(figures_data.get("figures", []))
    already = {fig.get("src") for fig in figures if isinstance(fig, dict)}

    out_dir.mkdir(parents=True, exist_ok=True)

    added = 0
    for item in items:
        pmc = item.get("pmc")
        pmid = item.get("pmid")
        if not pmc or not pmid:
            continue

        efetch_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
            + urllib.parse.urlencode({"db": "pmc", "id": pmc, "retmode": "xml"})
        )
        xml_root = ET.fromstring(_http_get(efetch_url))
        license_url, license_text = _find_cc_license(xml_root)
        if only_cc and not license_url:
            continue

        href, caption = _find_first_figure(xml_root)
        if not href:
            continue

        article_url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmc}/"
        article_html = _http_get(article_url).decode("utf-8", errors="ignore")
        cdn_match = re.search(r'src="([^"]*%s)"' % re.escape(href), article_html)

        basename = _safe_filename(f"{pmid}-{Path(href).name}")
        if "." not in basename:
            basename = f"{basename}.jpg"
        out_path = out_dir / basename
        src = f"assets/figures/{basename}"

        if src in already:
            continue

        if not out_path.exists():
            image_url = cdn_match.group(1).replace("&amp;", "&") if cdn_match else f"{article_url}bin/{href}"
            out_path.write_bytes(_http_get(image_url))

        year = item.get("year")
        title = item.get("title") or "Publication figure"
        credit_bits = []
        if license_url:
            credit_bits.append(f"License: {license_url}")
        elif license_text:
            credit_bits.append("License: see article")
        credit = " · ".join(credit_bits) if credit_bits else None

        figures.append(
            {
                "src": src,
                "alt": f"Figure from: {title}",
                "caption": _text(caption) or f"{title} ({year})" if year else title,
                "link": item.get("pmc_url") or item.get("pubmed_url"),
                "credit": credit,
            }
        )
        already.add(src)
        added += 1

    figures_data["figures"] = figures
    figures_path.write_text(json.dumps(figures_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return added


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Download the first figure from CC-licensed PMC articles listed in assets/pubmed.json."
    )
    parser.add_argument("--pubmed", default="assets/pubmed.json", help="Path to PubMed JSON (default: assets/pubmed.json).")
    parser.add_argument(
        "--figures",
        default="assets/figures/figures.json",
        help="Figure gallery JSON to update (default: assets/figures/figures.json).",
    )
    parser.add_argument("--out-dir", default="assets/figures", help="Where to write image files (default: assets/figures).")
    parser.add_argument(
        "--only-cc",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Only download figures when a Creative Commons license is detected (default: true).",
    )
    args = parser.parse_args(argv)

    added = fetch_figures(
        pubmed_path=Path(args.pubmed),
        figures_path=Path(args.figures),
        out_dir=Path(args.out_dir),
        only_cc=bool(args.only_cc),
    )
    print(f"Added {added} figure(s) to {args.figures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
