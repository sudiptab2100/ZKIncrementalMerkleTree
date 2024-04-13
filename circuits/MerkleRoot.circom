pragma circom 2.0.0;

include "MiMC5Sponge.circom";

template DualMux() {
    signal input in[2];
    signal input s;
    signal output op[2];
    
    s * (1 - s) === 0;
    op[0] <== (in[1] - in[0]) * s + in[0];
    op[1] <== (in[0] - in[1]) * s + in[1];
}

template MerkleRoot(levels) {
    signal input leaf;
    signal input pathElements[levels];
    signal input side[levels];
    signal output root;
    
    component mux[levels];
    component hasher[levels];
    signal hashes[levels + 1];
    hashes[0] <== leaf;
    for(var i = 0; i < levels; i++) {
        mux[i] = DualMux();
        mux[i].in[0] <== pathElements[i];
        mux[i].in[1] <== hashes[i];
        mux[i].s <== side[i];
        
        hasher[i] = MiMC5Sponge(2);
        hasher[i].inputs[0] <== mux[i].op[0];
        hasher[i].inputs[1] <== mux[i].op[1];
        
        hashes[i + 1] <== hasher[i].op;
    }
    
    root <== hashes[levels];
}

component main = MerkleRoot(32);