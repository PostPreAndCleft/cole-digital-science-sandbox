#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


def _http_get(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:  # nosec - user supplies query only
        return response.read()


def _text(node: ET.Element | None) -> str | None:
    if node is None:
        return None
    value = "".join(node.itertext()).strip()
    return value or None


def _first(*values: str | None) -> str | None:
    for value in values:
        if value:
            return value
    return None


def _parse_year(pub_date: ET.Element | None) -> int | None:
    if pub_date is None:
        return None
    year_text = _text(pub_date.find("Year"))
    if year_text and year_text.isdigit():
        return int(year_text)

    medline_date = _text(pub_date.find("MedlineDate"))
    if medline_date:
        for token in medline_date.split():
            if token.isdigit() and len(token) == 4:
                return int(token)
    return None


def _chunk(items: list[str], size: int) -> list[list[str]]:
    if not items:
        return []
    count = int(math.ceil(len(items) / size))
    return [items[i * size : (i + 1) * size] for i in range(count)]


def fetch_pubmed(query: str, retmax: int, email: str | None, tool: str | None) -> dict:
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": str(retmax),
        "sort": "pub+date",
    }
    if email:
        params["email"] = email
    if tool:
        params["tool"] = tool

    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(params)
    esearch_data = json.loads(_http_get(esearch_url).decode("utf-8"))
    pmids = esearch_data.get("esearchresult", {}).get("idlist", [])

    items: list[dict] = []
    for batch in _chunk(pmids, 150):
        fetch_params = {"db": "pubmed", "id": ",".join(batch), "retmode": "xml"}
        if email:
            fetch_params["email"] = email
        if tool:
            fetch_params["tool"] = tool
        efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(fetch_params)
        xml_bytes = _http_get(efetch_url)
        root = ET.fromstring(xml_bytes)

        for article in root.findall("./PubmedArticle"):
            citation = article.find("./MedlineCitation")
            if citation is None:
                continue

            pmid = _text(citation.find("./PMID"))
            article_node = citation.find("./Article")
            if not pmid or article_node is None:
                continue

            title = _text(article_node.find("./ArticleTitle"))
            journal = _text(article_node.find("./Journal/Title"))
            pub_date = article_node.find("./Journal/JournalIssue/PubDate")
            year = _parse_year(pub_date)

            authors: list[str] = []
            for author in article_node.findall("./AuthorList/Author"):
                last = _text(author.find("./LastName"))
                initials = _text(author.find("./Initials"))
                collective = _text(author.find("./CollectiveName"))
                if collective:
                    authors.append(collective)
                elif last and initials:
                    authors.append(f"{last} {initials}")
                elif last:
                    authors.append(last)

            doi = None
            pmc = None
            for id_node in article.findall("./PubmedData/ArticleIdList/ArticleId"):
                id_type = id_node.attrib.get("IdType")
                value = _text(id_node)
                if id_type == "doi" and value:
                    doi = value
                if id_type == "pmc" and value:
                    pmc = value

            items.append(
                {
                    "pmid": pmid,
                    "title": title,
                    "journal": journal,
                    "year": year,
                    "authors": authors,
                    "doi": doi,
                    "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "pmc": pmc,
                    "pmc_url": f"https://pmc.ncbi.nlm.nih.gov/articles/{pmc}/" if pmc else None,
                }
            )

    now = dt.datetime.now(dt.timezone.utc).isoformat()
    return {"generated_at": now, "query": query, "count": len(items), "items": items}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch PubMed metadata for an author query and write assets/pubmed.json for the site."
    )
    parser.add_argument(
        "--query",
        required=True,
        help='PubMed search query, e.g. \'Cole AA[Author] AND ("electron tomography"[Title/Abstract] OR synapse)\'',
    )
    parser.add_argument("--retmax", type=int, default=200, help="Max PubMed results to fetch (default: 200).")
    parser.add_argument("--email", default=None, help="Optional: email to include for NCBI E-utilities etiquette.")
    parser.add_argument("--tool", default="cole-digital-science-sandbox", help="Optional: tool name for NCBI requests.")
    parser.add_argument(
        "--out",
        default="assets/pubmed.json",
        help="Output path relative to repo root (default: assets/pubmed.json).",
    )
    args = parser.parse_args(argv)

    data = fetch_pubmed(query=args.query, retmax=args.retmax, email=args.email, tool=args.tool)
    out_path = args.out
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"Wrote {out_path} with {data['count']} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

