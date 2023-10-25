from typing import Dict

from deploy_tools.deploy import deploy_compiled_contract, load_contracts_json
from web3.contract import Contract


def deploy_merkle_drop_contract(
    *, web3, transaction_options: Dict = None, private_key=None, constructor_args
):

    if transaction_options is None:
        transaction_options = {}

    compiled_contracts = load_contracts_json(__name__)

    merkle_drop_abi = compiled_contracts["MerkleDrop"]["abi"]
    merkle_drop_bin = compiled_contracts["MerkleDrop"]["bytecode"]

    merkle_drop_contract: Contract = deploy_compiled_contract(
        abi=merkle_drop_abi,
        bytecode=merkle_drop_bin,
        constructor_args=constructor_args,
        web3=web3,
        transaction_options=transaction_options,
        private_key=private_key,
    )

    return merkle_drop_contract


def deploy_dropped_token_contract(
    *, web3, transaction_options: Dict = None, private_key=None, constructor_args
):

    if transaction_options is None:
        transaction_options = {}

    compiled_contracts = load_contracts_json(__name__)

    merkle_drop_abi = compiled_contracts["DroppedToken"]["abi"]
    merkle_drop_bin = compiled_contracts["DroppedToken"]["bytecode"]

    dropped_token_contract: Contract = deploy_compiled_contract(
        abi=merkle_drop_abi,
        bytecode=merkle_drop_bin,
        constructor_args=constructor_args,
        web3=web3,
        transaction_options=transaction_options,
        private_key=private_key,
    )

    return dropped_token_contract

def sum_of_airdropped_tokens(airdrop_data):
    sum = 0
    for item in airdrop_data:
        sum += item.value
    return sum
