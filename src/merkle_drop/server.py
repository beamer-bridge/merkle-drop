import logging
from eth_utils import encode_hex, is_address, to_canonical_address, to_checksum_address
from flask import Flask, abort, jsonify
from flask_cors import CORS

from merkle_drop.airdrop import get_balance, get_item, to_items
from merkle_drop.load_csv import load_airdrop_file
from merkle_drop.merkle_tree import build_tree, create_proof

app = Flask("Merkle Airdrop Backend Server")

airdrop_dict = None
airdrop_tree = None
decay_start_time = -1
decay_duration_in_seconds = -1


def init_gunicorn_logging():
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


def init_cors(**kwargs):
    """enable CORS

    see https://flask-cors.corydolphin.com/en/latest/api.html#extension
    for allowed kwargs

    The default is to allow '*', but one can pass
    e.g. origins='http://example.com' to allow request from one domain
    only." """
    CORS(app=app, **kwargs)


def init(
    airdrop_filename: str,
):
    global airdrop_dict
    global airdrop_tree

    app.logger.info(f"Initializing merkle tree from file {airdrop_filename}")
    airdrop_dict = load_airdrop_file(airdrop_filename)
    app.logger.info(f"Building merkle tree from {len(airdrop_dict)} entries")
    airdrop_tree = build_tree(to_items(airdrop_dict))


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=404, message="Not found"), 404


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=400, message=e.description), 400


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=500, message="There was an internal server error"), 500


@app.route("/entitlement/<string:address>", methods=["GET"])
def get_entitlement_for(address):
    if not is_address(address):
        abort(400, "The address is not in checksum-case or invalid")
    canonical_address = to_canonical_address(address)

    eligible_tokens = get_balance(canonical_address, airdrop_dict)
    if eligible_tokens == 0:
        proof = []
        tokens = 0
    else:
        proof = create_proof(get_item(canonical_address, airdrop_dict), airdrop_tree)
        tokens = eligible_tokens
    return jsonify(
        {
            "address": to_checksum_address(address),
            "tokens": tokens,
            "proof": [encode_hex(hash_) for hash_ in proof],
        }
    )


# See also MerkleDrop.sol:6


# Only for testing
if __name__ == "__main__":
    init_cors(origins="*")
    init("airdrop.csv")
    app.run()
