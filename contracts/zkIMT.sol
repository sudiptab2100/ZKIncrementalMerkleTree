// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "./ZKVerifier.sol";
import "./IMT.sol";

contract zkIMT is IMT, Groth16Verifier {
    mapping(uint256 => bool) public usedProofs;
    Groth16Verifier verifier;
    constructor() {
        verifier = Groth16Verifier(this);
    }
    function isTreeMemberZK(uint[2] calldata _pA, uint[2][2] calldata _pB, uint[2] calldata _pC, uint[3] calldata _pubSignals) public {
        uint nullifier = _pubSignals[2];
        require(!usedProofs[nullifier], "Proof already used");
        require(verifier.verifyProof(_pA, _pB, _pC, _pubSignals), "Invalid proof");
        usedProofs[nullifier] = true;
    }
}