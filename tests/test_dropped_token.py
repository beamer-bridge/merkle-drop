import pytest


def test_before_token_transfer(dropped_token_contract):
    w3 = dropped_token_contract.web3
    
    owner = dropped_token_contract.functions.owner().call()
    account1 = w3.eth.accounts[1]
    account2 = w3.eth.accounts[2]

    dropped_token_contract.functions.transfer(account1, 1000 * 10**18).transact({'from': owner})

    # Initially, the contract is paused
    assert dropped_token_contract.functions.paused().call()

    # Trying to transfer tokens when paused and not in allowedTransferee should fail
    with pytest.raises(Exception):
        dropped_token_contract.functions.transfer(account2, 1000 * 10**18).transact({'from': account1})

    # Allow account1 in allowedTransferee
    dropped_token_contract.functions.allowTransferee(account1).transact({'from': owner})
    assert dropped_token_contract.functions.allowedTransferee(account1).call()

    # Now account1 should be able to transfer tokens
    tx_hash =  dropped_token_contract.functions.transfer(account2, 1000 * 10**18).transact({'from': account1})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert receipt.status == 1

    # Trying to transfer tokens when paused and not in allowedTransferee should fail
    with pytest.raises(Exception):
        dropped_token_contract.functions.transfer(account1, 1000 * 10 ** 18).transact({'from': account2})

    # Unpause the contract
    dropped_token_contract.functions.unpause().transact({'from': owner})
    assert not dropped_token_contract.functions.paused().call()

    # Any account should be able to transfer tokens now
    tx_hash = dropped_token_contract.functions.transfer(account1, 1000 * 10 ** 18).transact({'from': account2})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert receipt.status == 1