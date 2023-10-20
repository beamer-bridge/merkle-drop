// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./openzeppelin/IERC20.sol";

contract MerkleDrop {

    bytes32 public root;
    IERC20 public droppedToken;
    address public treasuryAddress;
    uint public airdropExpiresAt;

    mapping (address => bool) public withdrawn;

    event Withdraw(address recipient, uint value);

    constructor(IERC20 _droppedToken, bytes32 _root, address _treasuryAddress, uint _airdropExpiresAt) {
        droppedToken = _droppedToken;
        root = _root;
        treasuryAddress = _treasuryAddress;
        airdropExpiresAt = _airdropExpiresAt;
    }

    function withdraw(uint valueToSend, bytes32[] memory proof) public {
        require(verifyEntitled(msg.sender, valueToSend, proof), "The proof could not be verified.");
        require(!withdrawn[msg.sender], "You have already withdrawn your entitled token.");

        require(droppedToken.balanceOf(address(this)) >= valueToSend, "The MerkleDrop does not have tokens to drop yet / anymore.");
        require(valueToSend != 0, "The decayed entitled value is now zero.");

        withdrawn[msg.sender] = true;

        require(droppedToken.transfer(msg.sender, valueToSend));
        emit Withdraw(msg.sender, valueToSend);
    }

    function verifyEntitled(address recipient, uint value, bytes32[] memory proof) public view returns (bool) {
        // We need to pack the 20 bytes address to the 32 bytes value
        // to match with the proof made with the python merkle-drop package
        bytes32 leaf = keccak256(abi.encodePacked(recipient, value));
        return verifyProof(leaf, proof);
    }

    function verifyProof(bytes32 leaf, bytes32[] memory proof) internal view returns (bool) {
        bytes32 currentHash = leaf;

        for (uint i = 0; i < proof.length; i += 1) {
            currentHash = parentHash(currentHash, proof[i]);
        }

        return currentHash == root;
    }

    function parentHash(bytes32 a, bytes32 b) internal pure returns (bytes32) {
        if (a < b) {
            return keccak256(abi.encode(a, b));
        } else {
            return keccak256(abi.encode(b, a));
        }
    }

    function withdrawAfterAirdropExpires() external {
        require(block.timestamp > airdropExpiresAt, "The airdrop is still active.");

        require(droppedToken.transfer(treasuryAddress, droppedToken.balanceOf(address(this))));
        emit Withdraw(treasuryAddress, droppedToken.balanceOf(address(this)));
    }

}
