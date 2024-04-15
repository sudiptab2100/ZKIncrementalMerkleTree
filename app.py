import os
import random
import argparse
import json
from web3 import Web3


def generateCommitment():
    p = 21888242871839275222246405745257275088548364400416034343698204186575808495617; # Prime field
    nullifier = int.from_bytes(random.randbytes(32), 'big') % p
    secret = int.from_bytes(random.randbytes(32), 'big') % p
    data = {
        "nullifier": str(nullifier),
        "secret": str(secret)
    }
    with open('files/secrets.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    os.system('node CommitmentHasher_js/generate_witness.js CommitmentHasher_js/CommitmentHasher.wasm files/secrets.json files/witness.wtns') # Generate witness
    os.system('snarkjs wtns export json files/witness.wtns files/witness.json') # Export witness to json
    
    with open('files/witness.json') as f:
        commitment = json.load(f)[1] # Second element in witness.json is the commitment
    
    data = {
        "nullifier": nullifier,
        "secret": secret,
        "commitment": commitment
    }
    return data

def getContract():
    address = "0xAfdf815F584d61E0eeB9f56f0b30721121d9035f"
    abi = json.load(open('contracts/ABIs/zkIMT.json'))
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

def getTreeRoot():
    metadata = getContract()
    contract = metadata['contract']
    root = contract.functions.getTreeRoot().call()
    return root

if __name__ == '__main__':
    if not os.path.exists('files'): os.makedirs('files') 
    
    parser = argparse.ArgumentParser(description="ZK Incremental Merkle Tree (IMT) Operations.")
    parser.add_argument('--task', type=str, required=True, help='"insert": Generate and Insert Commitment in IMT, "verify": Verify Commitment in IMT, "zk-verify": Verify Commitment in IMT using zk-SNARK.')
    args = parser.parse_args()
    validate = ['insert', 'verify', 'zk-verify']
    if args.task not in validate:
        raise ValueError(f"Invalid task argument. Expected one of: {validate}")
    
    if args.task == 'insert':
        commitmentData = generateCommitment()
        print(f"Generated commitment: {commitmentData['commitment']}")
        leaf_index, tx_hash = insertCommitment(commitmentData['commitment'])
        print(f"Leaf Index: {leaf_index}")
        print(f"Transaction hash: {tx_hash}")
        if not os.path.exists(f'files/leaf{leaf_index}/'):
            os.makedirs(f'files/leaf{leaf_index}/')
            os.rename('files/secrets.json', f'files/leaf{leaf_index}/secrets.json')
    
    elif args.task == 'verify':
        leaf_index = int(input("Enter leaf index: "))
        pathElements, side = getPath(leaf_index)
        isMember = isTreeMember(leaf_index, pathElements, side)
        print(f"Is tree member: {isMember}")
    
    elif args.task == 'zk-verify':
        leaf_index = int(input("Enter leaf index: "))
        with open(f'files/leaf{leaf_index}/secrets.json') as f:
            data = json.load(f)
        nullifier = data["nullifier"]
        secret = data["secret"]
        pathElements, side = getPath(leaf_index)
        
        data = {
            "root": str(getTreeRoot()),
            "nullifier": str(nullifier),
            "secret": str(secret),
            "pathElements": [str(i) for i in pathElements],
            "side": [str(i) for i in side]
        }
        with open('files/input.json', 'w') as f:
            json.dump(data, f, indent=4)
        os.system('node ZKVerifier_js/generate_witness.js ZKVerifier_js/ZKVerifier.wasm files/input.json files/witness.wtns') # Generate witness
        os.system('snarkjs groth16 prove ZKStore/proving_key.zkey files/witness.wtns files/proof.json files/public.json') # Generate proof
        os.system('snarkjs groth16 verify ZKStore/verification_key.json files/public.json files/proof.json') # Verify proof locally
