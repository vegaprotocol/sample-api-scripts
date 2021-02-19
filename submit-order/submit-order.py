#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega wallet (REST)
- Vega node (REST)

Apps/Libraries:
- REST (wallet): requests (https://pypi.org/project/requests/)
- REST (node): requests (https://pypi.org/project/requests/)
"""

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__

import json
import os
import requests

import helpers

node_url_rest = os.getenv("NODE_URL_REST")
if not helpers.check_url(node_url_rest):
    print("Error: Invalid or missing NODE_URL_REST environment variable.")
    exit(1)

walletserver_url = os.getenv("WALLETSERVER_URL")
if not helpers.check_url(walletserver_url):
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
walletserver_url = helpers.check_wallet_url(walletserver_url)

# __create_wallet:
CREATE_NEW_WALLET = False
if CREATE_NEW_WALLET:
    # EITHER: Create new wallet
    url = f"{walletserver_url}/api/v1/wallets"
else:
    # OR: Log in to existing wallet
    url = f"{walletserver_url}/api/v1/auth/token"

# Make request to create new wallet or log in to existing wallet
req = {"wallet": wallet_name, "passphrase": wallet_passphrase}
response = requests.post(url, json=req)
helpers.check_response(response)

# Pull out the token and make a headers dict
token = response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}
# :create_wallet__

# __generate_keypair:
GENERATE_NEW_KEYPAIR = False
pubKey = ""
if GENERATE_NEW_KEYPAIR:
    # EITHER: Generate a new keypair
    req = {
        "passphrase": wallet_passphrase,
        "meta": [{"key": "alias", "value": "my_key_alias"}],
    }
    url = f"{walletserver_url}/api/v1/keys"
    response = requests.post(url, headers=headers, json=req)
    helpers.check_response(response)
    pubKey = response.json()["key"]["pub"]
else:
    # OR: List existing keypairs
    url = f"{walletserver_url}/api/v1/keys"
    response = requests.get(url, headers=headers)
    helpers.check_response(response)
    keys = response.json()["keys"]
    assert len(keys) > 0
    pubKey = keys[0]["pub"]
# :generate_keypair__

assert pubKey != ""

# __get_market:
# Next, get a Market ID
url = f"{node_url_rest}/markets"
response = requests.get(url)
helpers.check_response(response)
marketID = response.json()["markets"][0]["id"]
# :get_market__

# __prepare_order:
# Next, prepare a SubmitOrder
response = requests.get(f"{node_url_rest}/time")
helpers.check_response(response)
blockchaintime = int(response.json()["timestamp"])
expiresAt = str(int(blockchaintime + 120 * 1e9))  # expire in 2 minutes

req = {
    "submission": {
        "marketId": marketID,
        "partyId": pubKey,
        "price": "100000",  # Note: price is an integer. For example 123456
        "size": "100",  # is a price of 1.23456, assuming 5 decimal places.
        "side": "SIDE_BUY",
        "timeInForce": "TIME_IN_FORCE_GTT",
        "expiresAt": expiresAt,
        "type": "TYPE_LIMIT",
    }
}
print("Request for PrepareSubmitOrder:")
print(json.dumps(req, indent=2, sort_keys=True))
url = f"{node_url_rest}/orders/prepare/submit"
response = requests.post(url, json=req)
helpers.check_response(response)
preparedOrder = response.json()
# :prepare_order__
print("Response from PrepareSubmitOrder:")
print(json.dumps(preparedOrder, indent=2, sort_keys=True))

# __sign_tx:
# Wallet server: Sign the prepared transaction
blob = preparedOrder["blob"]
req = {"tx": blob, "pubKey": pubKey, "propagate": False}
print("Request for SignTx:")
print(json.dumps(req, indent=2, sort_keys=True))
url = f"{walletserver_url}/api/v1/messages/sync"
response = requests.post(url, headers=headers, json=req)
helpers.check_response(response)
signedTx = response.json()["signedTx"]
# :sign_tx__
print("Response from SignTx:")
print(json.dumps(signedTx, indent=2, sort_keys=True))

# __submit_tx:
# Vega node: Submit the signed transaction
req = {"tx": signedTx}
print("Request for SubmitTransaction:")
print(json.dumps(req, indent=2, sort_keys=True))
url = f"{node_url_rest}/transaction"
response = requests.post(url, json=req)
helpers.check_response(response)
# :submit_tx__

assert response.json()["success"]
print("All is well.")
