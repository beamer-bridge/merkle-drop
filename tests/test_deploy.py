from merkle_drop.deploy import deploy_merkle_drop


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
    merkle_drop = deploy_merkle_drop(web3=web3, constructor_args=constructor_args)

    assert merkle_drop.functions.airdropExpiresAt().call() == airdrop_expires_at
