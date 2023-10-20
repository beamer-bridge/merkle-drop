import eth_tester.exceptions
import pytest
from eth_utils import to_checksum_address


@pytest.fixture()
def merkle_drop_contract_already_withdrawn(
    merkle_drop_contract,
    dropped_token_contract,
    eligible_address_0,
    eligible_value_0,
    proof_0,
):
    merkle_drop_contract.functions.withdraw(eligible_value_0, proof_0).transact(
        {"from": eligible_address_0}
    )

    assert (
        dropped_token_contract.functions.balanceOf(eligible_address_0).call()
        == eligible_value_0
    )

    return merkle_drop_contract


def test_proof_entitlement(merkle_drop_contract, tree_data, proofs_for_tree_data):
    for i in range(len(proofs_for_tree_data)):
        address = tree_data[i].address
        value = tree_data[i].value
        proof = proofs_for_tree_data[i]
        assert merkle_drop_contract.functions.verifyEntitled(
            address, value, proof
        ).call()


def test_incorrect_value_entitlement(
    merkle_drop_contract, tree_data, proofs_for_tree_data
):
    address = tree_data[0].address
    incorrect_value = tree_data[0].value + 1234
    proof = proofs_for_tree_data[0]

    assert (
        merkle_drop_contract.functions.verifyEntitled(
            address, incorrect_value, proof
        ).call()
        is False
    )


def test_incorrect_proof_entitlement(
    merkle_drop_contract, other_data, proofs_for_tree_data
):
    address = other_data[0].address
    value = other_data[0].value
    incorrect_proof = proofs_for_tree_data[0]

    assert (
        merkle_drop_contract.functions.verifyEntitled(
            address, value, incorrect_proof
        ).call()
        is False
    )


def test_withdraw(
    merkle_drop_contract, tree_data, proofs_for_tree_data, dropped_token_contract
):
    for i in range(len(proofs_for_tree_data)):
        merkle_drop_balance = dropped_token_contract.functions.balanceOf(
            merkle_drop_contract.address
        ).call()

        address = tree_data[i].address
        value = tree_data[i].value
        proof = proofs_for_tree_data[i]
        merkle_drop_contract.functions.withdraw(value, proof).transact(
            {"from": address}
        )

        assert dropped_token_contract.functions.balanceOf(address).call() == value
        assert (
            dropped_token_contract.functions.balanceOf(
                merkle_drop_contract.address
            ).call()
            == merkle_drop_balance - value
        )


def test_withdraw_already_withdrawn(
    merkle_drop_contract_already_withdrawn,
    eligible_address_0,
    eligible_value_0,
    proof_0,
):
    with pytest.raises(eth_tester.exceptions.TransactionFailed):
        merkle_drop_contract_already_withdrawn.functions.withdraw(
            eligible_value_0, proof_0
        ).transact({"from": eligible_address_0})


def test_withdraw_wrong_proof(
    merkle_drop_contract_already_withdrawn, other_data, proof_0
):
    with pytest.raises(eth_tester.exceptions.TransactionFailed):
        merkle_drop_contract_already_withdrawn.functions.withdraw(
            other_data[0].value, proof_0
        ).transact({"from": other_data[0].address})


def test_withdraw_event(
    merkle_drop_contract, web3, eligible_address_0, eligible_value_0, proof_0
):
    latest_block_number = web3.eth.blockNumber

    merkle_drop_contract.functions.withdraw(eligible_value_0, proof_0).transact(
        {"from": eligible_address_0}
    )

    event = merkle_drop_contract.events.Withdraw.createFilter(
        fromBlock=latest_block_number
    ).get_all_entries()[0]["args"]

    assert event["recipient"] == to_checksum_address(eligible_address_0)
    assert event["value"] == eligible_value_0


@pytest.fixture()
def time_travel_chain_to_decay_multiplier(chain, decay_start_time, decay_duration):
    def time_travel(decay_multiplier):
        time = int(decay_start_time + decay_duration * decay_multiplier)
        chain.time_travel(time)
        # Mining a block is usually considered here to fix unexpected behaviour with gas estimations
        # but that would make the chain time_travel past the exact decay_multiplier

    return time_travel


def test_withdraw_tokens_to_treasury_address_after_airdrop_expires(
    chain, merkle_drop_contract, dropped_token_contract
):
    chain.time_travel(merkle_drop_contract.functions.airdropExpiresAt().call())

    # test that contract triggers "The airdrop is still active." error
    with pytest.raises(eth_tester.exceptions.TransactionFailed) as e:
        merkle_drop_contract.functions.withdrawAfterAirdropExpires().transact()
        assert "The airdrop is still active." in str(e.value)

    assert (
        dropped_token_contract.functions.balanceOf(merkle_drop_contract.address).call()
        != 0
    )

    chain.time_travel(merkle_drop_contract.functions.airdropExpiresAt().call() + 1)

    merkle_drop_contract.functions.withdrawAfterAirdropExpires().transact()

    assert (
        dropped_token_contract.functions.balanceOf(merkle_drop_contract.address).call()
        == 0
    )
