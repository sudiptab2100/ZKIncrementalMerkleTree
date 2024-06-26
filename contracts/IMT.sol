// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "./MiMC5Sponge.sol";

contract IMT is MiMC5Sponge {
    uint32 constant public levels = 31;
    uint32 constant public maxLeaves = uint32(2)**levels - 1;
    uint256[levels] public zeroRoots = [
        0,
        6582740095095376936388179666706376640995777958302529689294846430676159692127,
        8291668007025243113576010826009280576126528460462551748847925060204499207549,
        7205403601894335557207733361341756837163824990769449878189284266106914815663,
        12442197021216120756210400420132539044434217923810091370110864027741750608426,
        18196168473434676653351164269269983707090081494183046355959034522126992224661,
        16022460673495512149388122318609912183048153702460404932107879900529075398655,
        21281193276409760902071641304228560557120104381381933458494701228797534396159,
        6673598531432471661012732503141590735907930372145994207921508645117746322676,
        16248046957317788843030514656760092955146066414963352206466714849347438706460,
        6539245614977511065197440797134010653938215334120387187053892705081173542113,
        21664405369096857022323692241727485514773409217048026961985255593712961543764,
        19156548592637987395041217495089813456058389907633895713646629957028254188839,
        15115686190840774358635227509181662219503914270546465550272153644583347570970,
        20526646698433491635530176745335962705816689835584235111904717353274075938906,
        15228594108904066360950028986231417596906314330433810014102477124345095875434,
        17470562590176036170639214021053960151988972851037273266894322153182820445849,
        21440730643241192727354105919975069465264445385735760638982622511415702172787,
        1000074687489941837497080737712255397161570907733454033583973221287136478437,
        14310647458661452624821597668327697742544082187597290326421545390047690942213,
        9869040598593410032800321376153590761105259316382098519617901429065669823924,
        13696103255612843439807160153817828471240326052788110153316294935747972634509,
        455274969449377096823658453741999496396059249959910127783636655723326737866,
        6804348493414373307218437323324005507116835600973307050076386923940949801731,
        17935357191656600795200554159082748081791767139212755702875208823625689546614,
        18157652788546441218169842877407932719535398915943402773930299930812665249565,
        16828695175045431152385396713722892559515840748817421822582746676834569232640,
        14083322988715353955901845750763566395731764595038800177519051618277910237063,
        2782659158641090674643061650992992326531022271553679363426617678511928010659,
        17227751302073075686238562956735112623151347244410776383529828611163819532562,
        4976089704124332696046290704307831245012791466976093273749713585287636454452
    ];
    uint32 public currentLeafIndex = 0;
    mapping(uint32 => mapping(uint32 => uint256)) private tree;
    mapping(uint32 => mapping(uint32 => bool)) private isTreeSet;
    
    function getTreeNode(uint32 _level, uint32 _index) public view returns (uint256) {
        if(isTreeSet[_level][_index]) return tree[_level][_index];
        return zeroRoots[_level];
    }
    
    function setTreeNode(uint32 _level, uint32 _index, uint256 _value) private {
        tree[_level][_index] = _value;
        isTreeSet[_level][_index] = true;
    }
    
    function getTreeRoot() public view returns (uint256) {
        return getTreeNode(levels - 1, 0);
    }
    
    function insertLeaf(uint256 _leaf) public {
        require(currentLeafIndex <= maxLeaves, "Tree is full");
        setTreeNode(0, currentLeafIndex, _leaf);
        // Update the path till the root
        uint32 currIdx = currentLeafIndex;
        uint256 currHash = _leaf;
        for(uint32 i = 1; i < levels; i++) {
            uint256 left;
            uint256 right;
            if(currIdx % 2 == 0) {
                left = currHash;
                right = getTreeNode(i - 1, currIdx + 1);
            } else {
                left = getTreeNode(i - 1, currIdx - 1);
                right = currHash;
            }
            currHash = miMCSponge(left, right);
            currIdx /= 2;
            setTreeNode(i, currIdx, currHash);
        }
        currentLeafIndex++;
    }
    
    function getPath(uint32 _leafIdx) public view returns (uint256[levels - 1] memory pathElements, uint8[levels - 1] memory side) {
        require(_leafIdx <= maxLeaves, "Invalid Leaf Index");
        
        uint32 currIdx = _leafIdx;
        for(uint32 i = 0; i < levels - 1; i++) {
            if(currIdx % 2 == 0) { // neighbor is right
                pathElements[i] = getTreeNode(i, currIdx + 1);
                side[i] = 1;
            } else { // neighbor is left
                pathElements[i] = getTreeNode(i, currIdx - 1);
                side[i] = 0;
            }
            currIdx /= 2;
        }
    }
    
    function isTreeMember(uint32 _leafIdx, uint256[levels - 1] memory pathElements, uint8[levels - 1] memory side) public view returns (bool) {
        require(_leafIdx <= maxLeaves, "Invalid Leaf Index");
        
        uint256 root = getTreeNode(0, _leafIdx);
        for(uint32 i = 0; i < levels - 1; i++) {
            if(side[i] == 1) {
                root = miMCSponge(root, pathElements[i]);
            } else {
                root = miMCSponge(pathElements[i], root);
            }
        }
        
        return root == getTreeRoot();
    }
    
    function testMembership(uint32 _leafIdx) public view returns (bool) {
        uint256[levels - 1] memory el;
        uint8[levels - 1] memory side;
        (el, side) = getPath(_leafIdx);
        return isTreeMember(_leafIdx, el, side);
    }
}