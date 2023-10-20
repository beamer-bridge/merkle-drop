// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./SafeMath.sol";
import "./openzeppelin/Pausable.sol";
import "./openzeppelin/Ownable.sol";
import "./openzeppelin/ERC20Capped.sol";

contract DroppedToken is ERC20Capped, Pausable, Ownable {

    using SafeMath for uint256;

    uint8 private _decimals;

    // the amount that a deployer of this account should receive
    // when tokens get minted
    uint256 constant DEPLOYER_AMOUNT = 10000 * 10 ** 18;

    struct Recipient {
        address to;
        uint256 amount;
    }

    constructor (
        string memory name, string memory symbol, uint8 initDecimals, uint256 cap
    ) ERC20(name, symbol) ERC20Capped(cap){
        _pause();
        _decimals = initDecimals;
    }

    // Mints tokens to the specified recipients
    // Mints tokens to the deployer of this contract
    // mints the rest of the tokens to the DAO contract
    function initialize(
        Recipient[] calldata _recipients,
        address treasury,
        address newOwner
    ) external onlyOwner {
        for (uint256 i = 0; i < _recipients.length; i++) {
            _mint(_recipients[i].to, _recipients[i].amount);
        }

        _mint(owner(), DEPLOYER_AMOUNT);
        _mint(treasury, cap().sub(totalSupply()));
        transferOwnership(newOwner);
    }

    function _beforeTokenTransfer(
        address,
        address,
        uint256
    ) internal view override(ERC20) {
        require(!paused(), "ERC20Pausable: token transfer are currently paused");
    }

    function decimals() override public view returns (uint8) {
        return _decimals;
    }

    function unpause() external onlyOwner {
        _unpause();
    }
}