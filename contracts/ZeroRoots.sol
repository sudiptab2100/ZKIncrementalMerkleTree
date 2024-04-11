// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "./MiMC5Sponge.sol";

contract ZeroRoots is MiMC5Sponge {
    uint8 constant public levels = 32;
    uint256[levels] public roots;
    
    function setRoots() public {
        roots[0] = 0;
        for(uint8 i = 1; i < levels; i++) {
            roots[i] = miMCSponge(roots[i - 1], roots[i]);
        }
    }
    
    function getAllRoots() public view returns (uint256[levels] memory) {
        return roots;
    }
}