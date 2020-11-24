#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (REST)

Apps/Libraries:
- REST: requests (https://pypi.org/project/requests/)

Responses:
- response-examples.txt
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
import requests
import os
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

#####################################################################################
#                           W A L L E T   S E R V I C E                             #
#####################################################################################

print(f"Logging into wallet: {wallet_name}")

# Log in to an existing wallet
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
pubkey = keys[0]["pub"]

assert pubkey != ""
print("Selected pubkey for signing")

#####################################################################################
#                           M A R K E T   A C C O U N T S                           #
#####################################################################################

# Request a list of markets and select the first one
url = f"{node_url_rest}/markets"
response = requests.get(url)
helpers.check_response(response)
marketID = response.json()["markets"][0]["id"]

assert marketID != ""
print(f"Market found: {marketID}")

# __get_accounts_by_market:
# Request a list of accounts for a market on a Vega network
url = f"{node_url_rest}/markets/{marketID}/accounts"
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Market accounts:\n{}".format(json.dumps(response_json, indent=2, sort_keys=True)))
# :get_accounts_by_market__

#####################################################################################
#                            P A R T Y   A C C O U N T S                            #
#####################################################################################

# __get_accounts_by_party:
# Request a list of accounts for a party (pubkey) on a Vega network
url = f"{node_url_rest}/parties/{pubkey}/accounts"
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Party accounts:\n{}".format(json.dumps(response_json, indent=2, sort_keys=True)))
# :get_accounts_by_party__

#####################################################################################
#                           P A R T Y   P O S I T I O N S                           #
#####################################################################################

# __get_positions_by_party:
# Request a list of positions for a party (pubkey) on a Vega network
url = f"{node_url_rest}/parties/{pubkey}/positions"
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Party positions:\n{}".format(json.dumps(response_json, indent=2, sort_keys=True)))
# :get_positions_by_party__
