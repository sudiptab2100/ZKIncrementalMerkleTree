pragma circom  2.0.0;

include "MiMC5Sponge.circom";

template CommitmentHasher() {
    signal input nullifier;
    signal input secret;
    signal output commitmentHash;
    
    component hasher = MiMC5Sponge(2);
    hasher.inputs[0] <== nullifier;
    hasher.inputs[1] <== secret;
    
    commitmentHash <== hasher.op;
}

component main = CommitmentHasher();
