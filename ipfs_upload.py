#!/usr/bin/env python3
"""
Upload a JSON record to Pinata (pinning) and return the IPFS hash.
Requires: requests
Set env variables PINATA_API_KEY and PINATA_SECRET, or edit the variables below.
Usage: python3 ipfs_upload.py record.json
"""
import os, sys, json, requests

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET = os.getenv("PINATA_SECRET")
PINATA_PIN_JSON_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"


def pin_json(obj):
    if not PINATA_API_KEY or not PINATA_SECRET:
        raise RuntimeError("Set PINATA_API_KEY and PINATA_SECRET in environment")
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET,
        "Content-Type": "application/json"
    }
    payload = {"pinataContent": obj}
    r = requests.post(PINATA_PIN_JSON_URL, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["IpfsHash"]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ipfs_upload.py record.json")
        sys.exit(2)
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        obj = json.load(f)
    h = pin_json(obj)
    print("Pinned to IPFS:", h)

if __name__ == "__main__":
    main()
