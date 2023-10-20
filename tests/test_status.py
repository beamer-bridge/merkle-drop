from merkle_drop.status import get_merkle_drop_status
from tests.conftest import AIRDROP_EXPIRES_AT, TREASURY_ADDRESS


def test_status(
    web3,
    merkle_drop_contract,
    dropped_token_contract,
    root_hash_for_tree_data,
    decay_start_time,
    decay_duration,
    premint_token_value,
):
    status = get_merkle_drop_status(web3, merkle_drop_contract.address)

    assert status["address"] == merkle_drop_contract.address
    assert status["token_address"] == dropped_token_contract.address
    assert status["root"] == root_hash_for_tree_data
    assert status["token_balance"] == premint_token_value
    assert status["token_name"] == "droppedToken"
    assert status["token_symbol"] == "DTN"
    assert status["token_decimals"] == 18
    assert status["treasury_address"] == TREASURY_ADDRESS
    assert status["airdrop_expires_at"] == AIRDROP_EXPIRES_AT
