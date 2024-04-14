pragma circom 2.0.0;

include "MerkleRoot.circom";

template ZKVerifier(levels) {
    signal input root;
    signal input nullifier;
    signal input secret;
    signal input pathElements[levels - 1];
    signal input side[levels - 1];
    signal output valid;
    
    component treeVerifier = MerkleRoot(levels);
    treeVerifier.leaf <== nullifier;
    treeVerifier.pathElements[0] <== secret;
    treeVerifier.side[0] <== 1;
    for(var i = 1; i < levels; i++) {
        treeVerifier.pathElements[i] <== pathElements[i - 1];
        treeVerifier.side[i] <== side[i - 1];
    }
    
    treeVerifier.root === root;
    valid <== 1;
}

component main {public [root, nullifier]} = ZKVerifier(31);