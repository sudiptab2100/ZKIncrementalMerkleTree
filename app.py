import os
import random
import argparse
import json
from web3 import Web3


def generate_commitment():
    nullifier = int.from_bytes(random.randbytes(32), 'big')
    commitment = int.from_bytes(random.randbytes(32), 'big')
    data = {
        "nullifier": nullifier,
        "secret": commitment
    }
    with open('files/secrets.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    os.system('node CommitmentHasher_js/generate_witness.js CommitmentHasher_js/CommitmentHasher.wasm files/secrets.json files/witness.wtns') # Generate witness
    os.system('snarkjs wtns export json files/witness.wtns files/witness.json') # Export witness to json
    
    with open('files/witness.json') as f:
        commitment = json.load(f)[1]
    
    return commitment

def getContract():
    address = "0xf559617fdEF8889968b722375f1E2797467280C7"
    abi = json.load(open('contracts/ABIs/IMT.json'))
    rpc_url = "https://rpc.sepolia.org"
    chain_id = 11155111
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    
    return contract

def insert_commitment(commitment):
    pass

if __name__ == '__main__':
    if not os.path.exists('files'): os.makedirs('files') 
    
    parser = argparse.ArgumentParser(description="ZK Incremental Merkle Tree (IMT) Operations.")
    parser.add_argument('--task', type=str, required=True, help='"insert": Generate and Insert Commitment in IMT\n"verify": Verify Commitment in IMT')
    args = parser.parse_args()
    validate = ['insert', 'verify']
    if args.task not in validate:
        raise ValueError(f"Invalid task argument. Expected one of: {validate}")
    
    if args.task == 'insert':
        commitment = generate_commitment()
        print(f"Generated commitment: {commitment}")