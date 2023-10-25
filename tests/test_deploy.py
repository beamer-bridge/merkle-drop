from merkle_drop.deploy import deploy_merkle_drop_contract, deploy_dropped_token_contract


def test_deploy(web3):
    zero_address = "0x0000000000000000000000000000000000000000"
    root = b"12"
    treasury_address = "0x1234567890123456789012345678901234567890"
    airdrop_expires_at = 123
    constructor_args = (
        zero_address,
        root,
        treasury_address,
        airdrop_expires_at,
    )
    merkle_drop = deploy_merkle_drop_contract(web3=web3, constructor_args=constructor_args)

    assert merkle_drop.functions.airdropExpiresAt().call() == airdrop_expires_at


def test_deploy_token(web3):
    name = "DroppedToken"
    symbol ="DT"
    decimals = 18
    cap = 100_000_000 * 10 ** 18
    constructor_args = (
        name,
        symbol,
        decimals,
        cap,
    )

    token = deploy_dropped_token_contract(web3=web3, constructor_args=constructor_args)

    assert token.functions.name().call() ==  name
    assert token.functions.symbol().call() == symbol
    assert token.functions.decimals().call() == decimals
    assert token.functions.cap().call() == cap
