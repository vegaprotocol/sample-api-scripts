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
import os

# Needed to convert protobuf message to string/json dict for wallet signing
from google.protobuf.json_format import MessageToDict

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

# Vega node: Prepare the SubmitOrder
order_data=vac.vega.commands.v1.commands.OrderSubmission(
    market_id=marketID,
    # price is an integer. For example 123456 is a price of 1.23456,
    # assuming 5 decimal places.
    price="100000",
    side=vac.vega.vega.Side.SIDE_BUY,
    size=1,
    time_in_force=vac.vega.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
    type=vac.vega.vega.Order.Type.TYPE_LIMIT,
)

submission = {
    "orderSubmission": MessageToDict(order_data),
    "pubKey": pubkey,
    "propagate": True
}
url = f"{wallet_server_url}/api/v1/command/sync"
response = requests.post(url, headers=headers, json=submission)
helpers.check_response(response)

print("Signed order and sent to Vega")

