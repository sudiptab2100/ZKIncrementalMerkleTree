import os
import random
import argparse
import json


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