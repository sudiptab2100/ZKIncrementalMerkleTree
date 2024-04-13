# ZK Incremental Merkle Tree (zk-IMT)

## Introduction

### Incremental Merkle Tree

Incremental Merkle Tree (**IMT**) is a specialized form of a Merkle tree designed to allow for efficient appending of new elements, making it useful in applications where the dataset is expected to grow over time and updates need to be processed efficiently.

### What is zk-IMT?

**zk-IMT** is a zero-knowledge proof system for Incremental Merkle Trees. It allows a prover to prove tree membership and non-membership of a leaf in an IMT without revealing the leaf itself. The prover can also prove the consistency of two IMTs without revealing the entire tree.

## Code Usage

### Circuits

- #### Generate Commitment
