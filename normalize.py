#!/usr/bin/env python3
"""
Normalize JSONL scraped records. Deduplicate by URL and optionally filter those
that mention the target name. Preserves tags and occurrence counts.
Usage: python3 normalize.py input.jsonl output_normalized.jsonl
"""
import sys, json

TARGET_NAMES = ["Felicia Ann Kelley", "Felicia A. Kelley", "Felicia Kelley"]


def mentions_target(text):
    if not text: return False
    t = text.lower()
    return any(name.lower() in t for name in TARGET_NAMES)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 normalize.py input.jsonl output_normalized.jsonl")
        sys.exit(2)
    inp, outp = sys.argv[1], sys.argv[2]
    seen = set()
    kept = 0
    with open(inp, encoding="utf-8") as inf, open(outp, "w", encoding="utf-8") as outf:
        for line in inf:
            try:
                rec = json.loads(line)
            except:
                continue
            url = rec.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            text = "".join([rec.get("text_snippet",""), rec.get("title",""), rec.get("meta_description","")])
            if mentions_target(text):
                # ensure tags and occurrences exist
                rec.setdefault("tags", [])
                rec.setdefault("occurrences", {})
                outf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                kept += 1
    print("Normalized. Found", kept, "records mentioning the target (unique urls: ", len(seen), ").")

if __name__ == "__main__":
    main()
