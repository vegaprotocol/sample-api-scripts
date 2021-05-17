#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega wallet (REST)
- Vega node (gRPC)

Apps/Libraries:
- REST (wallet): Vega-API-client (https://pypi.org/project/Vega-API-client/)
- gRPC (node): Vega-API-client (https://pypi.org/project/Vega-API-client/)
"""

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__


import base64
import grpc
import json
import os

# __import_client:
import vegaapiclient as vac

# :import_client__

import helpers

node_url_grpc = os.getenv("NODE_URL_GRPC")
if node_url_grpc is None or not helpers.check_var(node_url_grpc):
    print("Error: Invalid or missing NODE_URL_GRPC environment variable.")
    exit(1)

walletserver_url = os.getenv("WALLETSERVER_URL")
if walletserver_url is None or not helpers.check_url(walletserver_url):
    print("Error: Invalid or missing WALLETSERVER_URL environment variable.")
    exit(1)

wallet_name = os.getenv("WALLET_NAME")
if wallet_name is None or not helpers.check_var(wallet_name):
    print("Error: Invalid or missing WALLET_NAME environment variable.")
    exit(1)

wallet_passphrase = os.getenv("WALLET_PASSPHRASE")
if wallet_passphrase is None or not helpers.check_var(wallet_passphrase):
    print("Error: Invalid or missing WALLET_PASSPHRASE environment variable.")
    exit(1)

# Help guide users against including api version suffix on url
walletserver_url = helpers.check_wallet_url(walletserver_url)

# __create_wallet:
# Vega node: Create client for accessing public data
datacli = vac.VegaTradingDataClient(node_url_grpc)

# Vega node: Create client for trading (e.g. submitting orders)
tradingcli = vac.VegaTradingClient(node_url_grpc)

# Wallet server: Create a walletclient (see above for details)
walletclient = vac.WalletClient(walletserver_url)
login_response = walletclient.login(wallet_name, wallet_passphrase)
# :create_wallet__
helpers.check_response(login_response)

# __get_market:
# Get a list of markets
markets = datacli.Markets(vac.api.trading.MarketsRequest()).markets
marketID = markets[0].id
# :get_market__

# __generate_keypair:
GENERATE_NEW_KEYPAIR = False
if GENERATE_NEW_KEYPAIR:
    # If you don't already have a keypair, generate one.
    response = walletclient.generatekey(wallet_passphrase, [])
    helpers.check_response(response)
    pubKey = response.json()["key"]["pub"]
else:
    # List keypairs
    response = walletclient.listkeys()
    helpers.check_response(response)
    keys = response.json()["keys"]
    assert len(keys) > 0
    pubKey = keys[0]["pub"]
# :generate_keypair__

# __prepare_order:
# Vega node: Prepare the SubmitOrder
order = vac.api.trading.PrepareSubmitOrderRequest(
    submission=vac.commands.v1.commands.OrderSubmission(
        market_id=marketID,
        # price is an integer. For example 123456 is a price of 1.23456,
        # assuming 5 decimal places.
        price=100000,
        side=vac.vega.Side.SIDE_BUY,
        size=1,
        time_in_force=vac.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
        type=vac.vega.Order.Type.TYPE_LIMIT,
    )
)
print(f"Request for PrepareSubmitOrder: {order}")
try:
    prepare_response = tradingcli.PrepareSubmitOrder(order)
except grpc.RpcError as exc:
    print(json.dumps(vac.grpc_error_detail(exc), indent=2, sort_keys=True))
    exit(1)
print(f"Response from PrepareSubmitOrder: {prepare_response}")
# :prepare_order__

# __sign_tx:
# Wallet server: Sign the prepared transaction
blob_base64 = base64.b64encode(prepare_response.blob).decode("ascii")
print(f"Request for SignTx: blob={blob_base64}, pubKey={pubKey}")
response = walletclient.signtx(blob_base64, pubKey, False)
helpers.check_response(response)
responsejson = response.json()
print("Response from SignTx:")
print(json.dumps(responsejson, indent=2, sort_keys=True))
signedTx = responsejson["signedTx"]
# :sign_tx__

# __submit_tx:
# Vega node: Submit the signed transaction
request = vac.api.trading.SubmitTransactionRequest(
    tx=vac.vega.SignedBundle(
        tx=base64.b64decode(signedTx["tx"]),
        sig=vac.vega.Signature(
            sig=base64.b64decode(signedTx["sig"]["sig"]),
            algo="vega/ed25519",
            version=1,
        ),
    ),
)
print(f"Request for SubmitTransaction: {request}")
submittx_response = tradingcli.SubmitTransaction(request)
# :submit_tx__
assert submittx_response.success
print("All is well.")
