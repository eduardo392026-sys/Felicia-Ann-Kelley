#!/usr/bin/env python3
"""
Simple scraper: given a text file with one URL per line, fetches each page,
extracts title, meta description, visible text, and saves JSON lines of records.
Detects the target name and a set of keywords: "little endian", "big O"/"big-O",
"f/k/a" and "blockchain" and records tags and occurrence counts.
Requires: requests, beautifulsoup4
Usage: python3 scraper.py urls.txt output.jsonl
"""
import sys
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urlparse

HEADERS = {"User-Agent": "FeliciaDataBot/1.0 (+https://yourdomain.example)"}

KEYWORDS = [
    ("little endian", ["little endian"]),
    ("big o", ["big o", "big-o", "bigO", "big-o notation", "big o notation"]),
    ("f/k/a", ["f/k/a", "fka", "formerly known as", "aka"]),
    ("blockchain", ["blockchain"]),
]
TARGET_NAMES = ["Felicia Ann Kelley", "Felicia A. Kelley", "Felicia Kelley"]


def extract_visible_text(soup):
    for s in soup(["script","style","noscript"]):
        s.extract()
    text = soup.get_text(separator="\n")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return "\n".join(lines)


def occurrences_of_terms(text):
    t = text.lower() if text else ""
    tags = []
    counts = {}
    for tag, forms in KEYWORDS:
        c = 0
        for f in forms:
            c += t.count(f)
        if c > 0:
            tags.append(tag)
            counts[tag] = c
    # check target names
    found_name = False
    for name in TARGET_NAMES:
        if name.lower() in t:
            found_name = True
            counts.setdefault("name_matches", 0)
            counts["name_matches"] += t.count(name.lower())
    return tags, counts, found_name


def scrape_url(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        return {"url": url, "error": str(e), "timestamp": time.time()}

    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta_desc = ""
    md = soup.find("meta", attrs={"name":"description"}) or soup.find("meta", attrs={"property":"og:description"})
    if md and md.get("content"):
        meta_desc = md["content"].strip()

    visible_text = extract_visible_text(soup)
    combined = "\n".join([title, meta_desc, visible_text])
    tags, counts, found_name = occurrences_of_terms(combined)

    return {
        "url": url,
        "domain": urlparse(url).netloc,
        "title": title,
        "meta_description": meta_desc,
        "text_snippet": visible_text[:8000],
        "found_name": bool(found_name),
        "tags": tags,
        "occurrences": counts,
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scraper.py urls.txt output.jsonl")
        sys.exit(2)
    urls_file, out_file = sys.argv[1], sys.argv[2]
    with open(urls_file) as f:
        urls = [l.strip() for l in f if l.strip()]
    with open(out_file, "w", encoding="utf-8") as out:
        for url in urls:
            rec = scrape_url(url)
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print("Scraped:", url, "found_name=", rec.get("found_name", False), "tags=", rec.get("tags", []))
            time.sleep(1)

if __name__ == "__main__":
    main()
