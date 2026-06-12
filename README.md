# Felicia-Ann-Kelley

This repository contains a starter pipeline to scrape web pages for references to "Felicia Ann Kelley",
normalize results, upload records to IPFS (Pinata), and anchor IPFS hashes on-chain using an Ethereum
testnet (Goerli) registry contract.

Important notes
- You confirmed using Goerli for anchoring. Use a testnet private key and testnet RPC provider (Infura/Alchemy).
- This pipeline looks for the name and the keywords: "little endian", "big O" (and variants), "f/k/a" (and variants), and "blockchain". These are stored as tags/occurrence counts in each record.
- Do NOT publish or store sensitive personal data on-chain. The contract stores only IPFS hashes, a title and a source URL.

Files added
- scraper.py — fetch pages, extract title/meta/text, detect name and keywords, emits JSONL
- normalize.py — dedupe and filter for records that mention the target name
- ipfs_upload.py — example Pinata uploader (requires PINATA_API_KEY, PINATA_SECRET env vars)
- contracts/DataRegistry.sol — simple Solidity contract to register IPFS hashes
- deploy_and_register.py — compile, deploy the contract and register an IPFS hash (requires PROVIDER_URL and PRIVATE_KEY env vars)

Quick start (local)
1. Prepare a list of URLs in a file `urls.txt` (one per line).
2. Run the scraper:
   python3 scraper.py urls.txt scraped.jsonl
3. Normalize and filter:
   python3 normalize.py scraped.jsonl normalized.jsonl
4. For each record you want to anchor, upload to IPFS (using Pinata):
   export PINATA_API_KEY=your_key
   export PINATA_SECRET=your_secret
   python3 ipfs_upload.py record.json
   This prints an IPFS hash (e.g., Qm... or bafy...)
5. Deploy and register on Goerli (testnet):
   export PROVIDER_URL=https://goerli.infura.io/v3/YOUR-PROJECT-ID
   export PRIVATE_KEY=0xYOUR_PRIVATE_KEY
   python3 deploy_and_register.py <ipfs_hash> "Page Title" "https://source.url"

Security and legal
- Respect robots.txt and site Terms of Service. Do not scrape sites you are not allowed to.
- Keep private keys and API keys secure; do not commit them to the repository.
- Consider hashing or redacting sensitive content before pinning or publishing.

If you want next
- I can also add a GitHub Action to run the pipeline on a schedule, or change the registry to accept extra tags on-chain (more gas).
- I can optionally switch IPFS provider to Infura, or implement automatic discovery using the Bing Search API.
