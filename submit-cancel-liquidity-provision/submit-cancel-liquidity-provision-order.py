#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega wallet (REST)
- Vega node (REST)

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
#

import json
import os
import requests
import time
import helpers

node_url_rest = os.getenv("NODE_URL_REST")
if not helpers.check_url(node_url_rest):
    print("Error: Invalid or missing NODE_URL_REST environment variable.")
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
# Helper code to list the available markets                                         #
#####################################################################################

# __get_market:
# Request the identifier for the market to place on
# url = f"{node_url_rest}/markets"
# response = requests.get(url)
# helpers.check_response(response)
# marketID = response.json()["markets"][0]["id"]
# :get_market__

# assert marketID != ""
# marketName = response.json()["markets"][0]["tradableInstrument"]["instrument"]["name"]
# print(f"Market found: {marketID} {marketName}")

#####################################################################################
#                 L I S T   L I Q U I D I T Y   P R O V I S I O N S                 #
#####################################################################################

# __get_liquidity_provisions:
# Request liquidity provisions for the market
partyID="" # specify party ID if needed, otherwise all liquidity provisions for the market get returned 
url = "{base}/liquidity-provisions/party/{party}/market/{marketId}".format(base=node_url_rest, party=partyID, marketId=marketID)
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()

print("Liquidity provisions:\n{}".format(json.dumps(response_json, indent=2, sort_keys=True)))
# :get_liquidity_provisions__

#####################################################################################
#               C A N C E L    L I Q U I D I T Y   C O M M I T M E N T              #
#####################################################################################

# __cancel_liquidity_order:
# Compose a liquidity commitment order message
# (it will now serve as a cancellation request): set commitmentAmount to 0,
# note that transaction may get rejected if removing previously supplied liquidity 
# will result in insufficient liquidity for the market
submission = {
    "liquidityProvisionCancellation": {
        "marketId": marketID,
    },
    "pubKey": pubkey,
    "propagate": True
}
# :cancel_liquidity_order__

print("Liquidity provision cancellation: ", submission)

# Sign the transaction with a liquidity provision submission command
# Note: Setting propagate to true will also submit to a Vega node
url = f"{wallet_server_url}/api/v1/command/sync"
response = requests.post(url, headers=headers, json=submission)
helpers.check_response(response)

print("Signed liquidity commitment (cancellation) and sent to Vega")

# Completed.
