#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega wallet (REST)
- Vega node (gRPC)

Apps/Libraries:
- REST: requests (https://pypi.org/project/requests/)
"""

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__

import os
import requests
import helpers

node_url_grpc = os.getenv("NODE_URL_GRPC")

# __import_client:
import vegaapiclient as vac
data_client = vac.VegaTradingDataClient(node_url_grpc)
# :import_client__

wallet_server_url = os.getenv("WALLETSERVER_URL")
if not helpers.check_url(wallet_server_url):
    print("Error: Invalid or missing WALLETSERVER_URL environment variable.")
    exit(1)

wallet_name = os.getenv("WALLET_NAME")
if not helpers.check_var(wallet_name):
    print("Error: Invalid or missing WALLET_NAME environment variable.")
    exit(1)

wallet_passphrase = os.getenv("WALLET_PASSPHRASE")
if not helpers.check_var(wallet_passphrase):
    print("Error: Invalid or missing WALLET_PASSPHRASE environment variable.")
    exit(1)

# Help guide users against including api version suffix on url
wallet_server_url = helpers.check_wallet_url(wallet_server_url)

#####################################################################################
#                           W A L L E T   S E R V I C E                             #
#####################################################################################

print(f"Logging into wallet: {wallet_name}")

# __existing_wallet:
# Make request to log in to existing wallet
req = {"wallet": wallet_name, "passphrase": wallet_passphrase}
response = requests.post(f"{wallet_server_url}/api/v1/auth/token", json=req)
helpers.check_response(response)
token = response.json()["token"]

assert token != ""
print("Logged in to wallet successfully")

# List key pairs and select public key to use
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{wallet_server_url}/api/v1/keys", headers=headers)
helpers.check_response(response)
keys = response.json()["keys"]
pubKey = keys[0]["pub"]

assert pubKey != ""
print("Selected pubkey for signing")
# :existing_wallet__

# __get_orders_for_party:
# Request a list of orders by party (pubKey)
orders_by_party_request = vac.data_node.api.v1.trading_data.OrdersByPartyRequest(
    party_id=pubKey
)
orders_response = data_client.OrdersByParty(orders_by_party_request)
print("OrdersByParty:\n{}".format(orders_response))
# :get_orders_for_party__

# __get_trades_for_party:
# Request a list of trades by party (pubKey)
trades_by_party_request = vac.data_node.api.v1.trading_data.TradesByPartyRequest(
    party_id=pubKey
)
trades_response = data_client.TradesByParty(trades_by_party_request)
print("TradesByParty:\n{}".format(trades_response))
# :get_trades_for_party__
