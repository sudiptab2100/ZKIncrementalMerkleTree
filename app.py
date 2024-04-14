import os
import random
import argparse
import json
from web3 import Web3


def generateCommitment():
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
    rpc_url = "https://rpc2.sepolia.org"
    chain_id = 11155111
    private_key = os.getenv("ETH_PRIVATE_KEY")
    
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    sender_address = w3.eth.account.from_key(private_key).address
    contract = w3.eth.contract(address=address, abi=abi)
    
    metadata = {
        'chainid': chain_id,
        'private': private_key,
        'sender': sender_address,
        'w3': w3,
        'contract': contract
    }
    return metadata

def insertCommitment(commitment):
    metadata = getContract()
    chain_id = metadata['chainid']
    private_key = metadata['private']
    sender_address = metadata['sender']
    w3 = metadata['w3']
    contract = metadata['contract']
    
    leaf_index = contract.functions.currentLeafIndex().call()
    insret_commitment_tx = contract.functions.insertLeaf(int(commitment)).build_transaction(
        {
            "nonce": w3.eth.get_transaction_count(sender_address),
            "gasPrice": w3.eth.gas_price,
            "gas": 3000000,  # Adjust gas limit accordingly
            "chainId": chain_id,
        }
    )
    signed_tx = w3.eth.account.sign_transaction(insret_commitment_tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
    return leaf_index, tx_hash

def getPath(leaf_index):
    metadata = getContract()
    chain_id = metadata['chainid']
    private_key = metadata['private']
    sender_address = metadata['sender']
    w3 = metadata['w3']
    contract = metadata['contract']
    
    path = contract.functions.getPath(leaf_index).call()
    return path

def isTreeMember(leaf_index, pathElements, side):
    metadata = getContract()
    chain_id = metadata['chainid']
    private_key = metadata['private']
    sender_address = metadata['sender']
    w3 = metadata['w3']
    contract = metadata['contract']
    
    is_member = contract.functions.isTreeMember(leaf_index, pathElements, side).call()
    return is_member

if __name__ == '__main__':
    if not os.path.exists('files'): os.makedirs('files') 
    
    parser = argparse.ArgumentParser(description="ZK Incremental Merkle Tree (IMT) Operations.")
    parser.add_argument('--task', type=str, required=True, help='"insert": Generate and Insert Commitment in IMT\n"verify": Verify Commitment in IMT')
    args = parser.parse_args()
    validate = ['insert', 'verify']
    if args.task not in validate:
        raise ValueError(f"Invalid task argument. Expected one of: {validate}")
    
    if args.task == 'insert':
        commitment = generateCommitment()
        print(f"Generated commitment: {commitment}")
        leaf_index, tx_hash = insertCommitment(commitment)
        print(f"Leaf Index: {leaf_index}")
        print(f"Transaction hash: {tx_hash}")
    
    elif args.task == 'verify':
        leaf_index = int(input("Enter leaf index: "))
        pathElements, side = getPath(leaf_index)
        isMember = isTreeMember(leaf_index, pathElements, side)
        print(f"Is tree member: {isMember}")