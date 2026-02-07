#!/usr/bin/env python3
"""Create dated HTML snapshots in archives/ with link rewrites.

Usage examples:
  python3 scripts/archive_pages.py --pages linkedin.html
  python3 scripts/archive_pages.py --pages linkedin.html cv.html --label job
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import sys


RELATIVE_ATTR_RE = re.compile(r"\b(?P<attr>href|src)=(?P<quote>[\"'])(?P<url>[^\"']+)(?P=quote)")


def _rewrite_url(url: str) -> str:
    if url.startswith(("http://", "https://", "mailto:", "tel:", "#", "/", "../")):
        return url
    if url.startswith("./"):
        url = url[2:]
    return f"../{url}"


def rewrite_links(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        attr = match.group("attr")
        quote = match.group("quote")
        url = match.group("url")
        new_url = _rewrite_url(url)
        return f"{attr}={quote}{new_url}{quote}"

    return RELATIVE_ATTR_RE.sub(repl, html)


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive HTML pages into archives/.")
    parser.add_argument(
        "--pages",
        nargs="+",
        required=True,
        help="HTML files to archive (e.g., linkedin.html).",
    )
    parser.add_argument(
        "--out-dir",
        default="archives",
        help="Output directory for archived pages (default: archives).",
    )
    parser.add_argument(
        "--label",
        default="",
        help="Optional label to include in the archived filename (e.g., job).",
    )
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Override date for the archive filename (YYYY-MM-DD).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    label = args.label.strip()
    date_str = args.date.strip()

    for page in args.pages:
        src = Path(page)
        if not src.exists():
            print(f"Missing file: {src}", file=sys.stderr)
            return 1
        if src.suffix.lower() != ".html":
            print(f"Skipping non-HTML file: {src}", file=sys.stderr)
            continue

        html = src.read_text()
        html = rewrite_links(html)

        parts = [src.stem]
        if label:
            parts.append(label)
        if date_str:
            parts.append(date_str)
        filename = "-".join(parts) + src.suffix

        dest = unique_path(out_dir / filename)
        dest.write_text(html)
        print(f"Archived {src} -> {dest}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
