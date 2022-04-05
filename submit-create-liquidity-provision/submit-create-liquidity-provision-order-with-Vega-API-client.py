#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega wallet (REST)
- Vega node (gRPC)

Apps/Libraries:
- Vega-API-client (https://pypi.org/project/Vega-API-client/)
"""

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__
#

# Needed to convert protobuf message to string/json dict for wallet signing
from google.protobuf.json_format import MessageToDict

import helpers
import requests
import time
import os
import uuid

node_url_grpc = os.getenv("NODE_URL_GRPC")
if not helpers.check_var(node_url_grpc):
    print("Error: Invalid or missing NODE_URL_GRPC environment variable.")
    exit(1)

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

marketID = os.getenv("VEGA_MARKET")
if not helpers.check_var(marketID):
    print("Error: Invalid or missing VEGA_MARKET environment variable.")
    exit(1)

# Help guide users against including api version suffix on url
wallet_server_url = helpers.check_wallet_url(wallet_server_url)

# __import_client:
import vegaapiclient as vac

# Vega gRPC clients for reading/writing data
data_client = vac.VegaTradingDataClient(node_url_grpc)
# :import_client__

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

#####################################################################################
#                               F I N D   M A R K E T                               #
#####################################################################################
# Helper code to list out the available markets                                     #
#####################################################################################

# __get_market:
# Request the identifier for the market to place on
# markets = data_client.Markets(vac.data_node.api.v1.trading_data.MarketsRequest()).markets
# marketID = markets[0].id
# :get_market__

# assert marketID != ""
# marketName = markets[0].tradable_instrument.instrument.name
# print(f"Market found: {marketID} {marketName}")

#####################################################################################
#                 L I S T   L I Q U I D I T Y   P R O V I S I O N S                 #
#####################################################################################

# __get_liquidity_provisions:
# Request liquidity provisions for the market
partyID="" # specify party ID if needed, otherwise all liquidity provisions for the market get returned 
liquidityProvisions = data_client.LiquidityProvisions(vac.data_node.api.v1.trading_data.LiquidityProvisionsRequest(
    party=partyID,
    market=marketID
))

print("Liquidity provisions:\n{}".format(liquidityProvisions))
# :get_liquidity_provisions__

#####################################################################################
#              S U B M I T   L I Q U I D I T Y   C O M M I T M E N T                #
#####################################################################################

# Note: commitment_amount is an integer. For example 123456 is a price of 1.23456,
# for a market which is configured to have a precision of 5 decimal places.

# __prepare_liquidity_order:
# Prepare a liquidity commitment transaction message
lp_ref = f"{pubkey}-{uuid.uuid4()}"
lp_data=vac.vega.commands.v1.commands.LiquidityProvisionSubmission(
    market_id=marketID,
    commitment_amount="100",
    fee="0.01",
    reference=lp_ref,
    buys=[
        vac.vega.vega.LiquidityOrder(
            reference=vac.vega.vega.PEGGED_REFERENCE_MID,
            proportion=1,
            offset="1"
        ),
        vac.vega.vega.LiquidityOrder(
            reference=vac.vega.vega.PEGGED_REFERENCE_MID,
            proportion=2,
            offset="2"
        )
    ],
    sells=[
        vac.vega.vega.LiquidityOrder(
            reference=vac.vega.vega.PEGGED_REFERENCE_MID,
            proportion=1,
            offset="1"
        ),
        vac.vega.vega.LiquidityOrder(
            reference=vac.vega.vega.PEGGED_REFERENCE_MID,
            proportion=2,
            offset="2"
        ),
        vac.vega.vega.LiquidityOrder(
            reference=vac.vega.vega.PEGGED_REFERENCE_MID,
            proportion=5,
            offset="3"
        )
    ]
)
# :prepare_liquidity_order__

print("Liquidity provision: ", lp_data)

# __sign_tx_liquidity_order:
# Sign the transaction with an lp submission
# Note: Setting propagate to true will also submit to a Vega node
submission = {
    "liquidityProvisionSubmission": MessageToDict(lp_data),
    "pubKey": pubkey,
    "propagate": True
}
url = f"{wallet_server_url}/api/v1/command/sync"
response = requests.post(url, headers=headers, json=submission)
helpers.check_response(response)
# :sign_tx_liquidity_order__

print("Signed LP submission and sent to Vega")
