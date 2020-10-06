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

import json
import os
import requests
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

# Help guide users against including api version suffix on url
wallet_server_url = helpers.check_wallet_url(wallet_server_url)

# __existing_wallet:
# Make request to log in to existing wallet
url = "{base}/api/v1/auth/token".format(base=wallet_server_url)
req = {"wallet": wallet_name, "passphrase": wallet_passphrase}
response = requests.post(url, json=req)
helpers.check_response(response)
# :existing_wallet__

token = response.json()["token"]

# __find_keypair:
# Find an existing keypair for wallet
headers = {"Authorization": "Bearer " + token}
url = "{base}/api/v1/keys".format(base=wallet_server_url)
response = requests.get(url, headers=headers)
helpers.check_response(response)
keys = response.json()["keys"]
assert len(keys) > 0
pubKey = keys[0]["pub"]
# :find_keypair__

assert pubKey != ""

# __get_orders_for_party:
# Request a list of orders by party (pubKey)
url = "{base}/parties/{party}/orders".format(base=node_url_rest, party=pubKey)
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("OrdersByParty:\n{}".format(json.dumps(response_json, indent=2, sort_keys=True)))
# :get_orders_for_party__

# __get_trades_for_party:
# Request a list of trades by party (pubKey)
url = "{base}/parties/{party}/trades".format(base=node_url_rest, party=pubKey)
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("TradesByParty:\n{}".format(json.dumps(response_json, indent=2, sort_keys=True)))
# :get_trades_for_party__
