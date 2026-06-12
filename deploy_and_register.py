#!/usr/bin/env python3
"""
Deploy the DataRegistry contract and register a sample IPFS hash on Goerli.
Requires: web3, eth-account, py-solc-x (solcx)
Set environment:
  PROVIDER_URL - RPC endpoint (e.g., Infura/Alchemy/localhost)
  PRIVATE_KEY - private key of deployer (testnet key)
Usage:
  python3 deploy_and_register.py ipfs_hash "Title" "source_url"
"""
import os, sys, json
from web3 import Web3
from solcx import compile_standard, install_solc

PROVIDER = os.getenv("PROVIDER_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PROVIDER or not PRIVATE_KEY:
    raise SystemExit("Set PROVIDER_URL and PRIVATE_KEY in environment")

w3 = Web3(Web3.HTTPProvider(PROVIDER))
acct = w3.eth.account.from_key(PRIVATE_KEY)
# chain_id will be obtained from provider; for Goerli this is 5
try:
    chain_id = w3.eth.chain_id
except Exception:
    chain_id = 5

CONTRACT_SOURCE_PATH = "contracts/DataRegistry.sol"

def compile_contract():
    # ensure a compatible solc is installed
    install_solc('0.8.17')
    with open(CONTRACT_SOURCE_PATH, "r", encoding="utf-8") as f:
        src = f.read()
    compiled = compile_standard({
        "language":"Solidity",
        "sources": {"DataRegistry.sol": {"content": src}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
    }, allow_paths=".")
    abi = compiled["contracts"]["DataRegistry.sol"]["DataRegistry"]["abi"]
    bytecode = compiled["contracts"]["DataRegistry.sol"]["DataRegistry"]["evm"]["bytecode"]["object"]
    return abi, bytecode


def deploy(abi, bytecode):
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(acct.address)
    tx = contract.constructor().build_transaction({
        "from": acct.address,
        "nonce": nonce,
        "gas": 8000000,
        "gasPrice": w3.to_wei("20", "gwei"),
        "chainId": chain_id
    })
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print("Deploy tx:", tx_hash.hex())
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Deployed at:", receipt.contractAddress)
    return receipt.contractAddress


def register(contract_address, abi, ipfs_hash, title, source):
    contract = w3.eth.contract(address=contract_address, abi=abi)
    nonce = w3.eth.get_transaction_count(acct.address)
    tx = contract.functions.register(ipfs_hash, title, source).build_transaction({
        "from": acct.address,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("20", "gwei"),
        "chainId": chain_id
    })
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print("Register tx:", tx_hash.hex())
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 deploy_and_register.py ipfs_hash \"Title\" \"source\"")
        sys.exit(2)
    ipfs_hash, title, source = sys.argv[1], sys.argv[2], sys.argv[3]
    abi, bytecode = compile_contract()
    contract_addr = deploy(abi, bytecode)
    rec = register(contract_addr, abi, ipfs_hash, title, source)
    print("Registered. Receipt:", rec.transactionHash.hex())
    print("Contract at:", contract_addr)

if __name__ == "__main__":
    main()
