// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./SafeMath.sol";
import "./openzeppelin/Pausable.sol";
import "./openzeppelin/Ownable.sol";
import "./openzeppelin/ERC20Capped.sol";

contract DroppedToken is ERC20Capped, Pausable, Ownable {

    using SafeMath for uint256;

    uint8 private _decimals;

    mapping(address => bool) private allowedTransferee; // whitelisted addresses for token distribution.

    // the amount that a deployer of this account should receive
    // when tokens get minted
    uint256 immutable DEPLOYER_AMOUNT;

    struct Recipient {
        address to;
        uint256 amount;
    }

    constructor (
        string memory name, string memory symbol, uint8 initDecimals, uint256 cap
    ) ERC20(name, symbol) ERC20Capped(cap){
        _pause();
        _decimals = initDecimals;

        // @dev Whitelisting the zero address to allow token minting.
        allowedTransferee[address(0)] = true;

        DEPLOYER_AMOUNT = 10_000 * 10 ** _decimals;

        Recipient[7] memory initialRecipients = [
            Recipient(0x22DfDaA6F79079B83f9fa4e3d88a410Cc1Da4d84, 1_875_000 * 10 ** _decimals),
            Recipient(0xE9562D66f405BFeb5b40b00733279d9151DCf808, 1_500_000 * 10 ** _decimals),
            Recipient(0xe5827d6d7169a87B4c241a5973722f1dDA6b5C0D, 1_125_000 * 10 ** _decimals),
            Recipient(0x49f834Da90FAB90e60CcA730B80e7c60e15FCA0B, 1_125_000 * 10 ** _decimals),
            Recipient(0x8B86DBBF1c595025550d9dAE25cfe5eE6D8435e4, 562_500 * 10 ** _decimals),
            Recipient(0x647e778aD23b5b22D188e8d664fA4fEEc259385C, 562_500 * 10 ** _decimals),
            Recipient(0xf8F09be6daBFfAa3c02B2D653d9026cc7767eD99, 187_500 * 10 ** _decimals)
        ];

        for (uint256 i = 0; i < initialRecipients.length; i++) {
            _mint(initialRecipients[i].to, initialRecipients[i].amount);
        }
    }

    // Mints tokens to the deployer of this contract
    // mints the rest of the tokens to the DAO contract
    // and transfers ownership to the DAO contract
    function initialize(
        address treasury,
        address newOwner
    ) external onlyOwner {
        _mint(owner(), DEPLOYER_AMOUNT);
        _mint(treasury, cap().sub(totalSupply()));
        transferOwnership(newOwner);
    }

    function allowTransferee(address transferee) external onlyOwner {
        allowedTransferee[transferee] = true;
    }

    function _beforeTokenTransfer(
        address from,
        address,
        uint256
    ) internal view override(ERC20) {

        require(!paused() || allowedTransferee[from], "ERC20Pausable: token transfer are currently paused or the transferee is not allowed");
    }

    function decimals() override public view returns (uint8) {
        return _decimals;
    }

    function unpause() external onlyOwner {
        _unpause();
    }
}