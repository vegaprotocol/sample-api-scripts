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


import requests
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

wallet_server_url = os.getenv("WALLETSERVER_URL")
if wallet_server_url is None or not helpers.check_url(wallet_server_url):
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
wallet_server_url = helpers.check_wallet_url(wallet_server_url)

# Vega node: Create client for accessing public data
datacli = vac.VegaTradingDataClient(node_url_grpc)

#####################################################################################
#                           W A L L E T   S E R V I C E                             #
#####################################################################################

print(f"Logging into wallet: {wallet_name}")

# __login_wallet:
# Log in to an existing wallet
req = {"wallet": wallet_name, "passphrase": wallet_passphrase}
response = requests.post(f"{wallet_server_url}/api/v1/auth/token", json=req)
helpers.check_response(response)
token = response.json()["token"]
# :login_wallet__

assert token != ""
print("Logged in to wallet successfully")

# __get_pubkey:
# List key pairs and select public key to use
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{wallet_server_url}/api/v1/keys", headers=headers)
helpers.check_response(response)
keys = response.json()["keys"]
pubkey = keys[0]["pub"]
# :get_pubkey__

assert pubkey != ""
print("Selected pubkey for signing")

# __get_market:
# Get a list of markets
markets = datacli.Markets(vac.data_node.api.v1.trading_data.MarketsRequest()).markets
marketID = markets[0].id
# :get_market__

# __prepare_order:
# Vega node: Prepare the SubmitOrder
order = vac.data_node.api.v1.trading_data.PrepareSubmitOrderRequest(
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
request = vac.data_node.api.v1.trading_data.SubmitTransactionRequest(
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
