#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (REST)
- Vega wallet (REST)

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
import requests
import time
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
#                            L I S T   P R O P O S A L S                            #
#####################################################################################

# There are two types of REST request for proposals on Vega:
# 1 - MARKET proposals (/governance/market/proposals)
# 2 - ASSET proposals (/governance/asset/proposals)
# Note: In the future users will be able to call an endpoint to retrieve ALL proposals.

# __get_proposals:
# Request a list of proposals on a Vega network
response = requests.get(node_url_rest + "/governance/market/proposals")
helpers.check_response(response)
proposals = response.json()
print("Proposals:\n{}".format(json.dumps(proposals, indent=2, sort_keys=True)))
# :get_proposals__

proposalID = proposals["data"][0]["proposal"]["id"]
assert proposalID != ""
print(f"Proposal found: {proposalID}")

#####################################################################################
#                         P R O P O S A L   D E T A I L S                           #
#####################################################################################

# __get_proposal_detail:
# Request results of a specific proposal on a Vega network
response = requests.get(node_url_rest + "/governance/proposal/" + proposalID)
helpers.check_response(response)
response_json = response.json()
print("Proposal:\n{}".format(json.dumps(response_json, indent=2, sort_keys=True)))
# :get_proposal_detail__

#####################################################################################
#                          P A R T Y   P R O P O S A L S                            #
#####################################################################################

# __get_proposals_by_party:
# Request results of a specific proposal on a Vega network
response = requests.get(node_url_rest + "/parties/" + pubkey + "/proposals")
helpers.check_response(response)
response_json = response.json()
print("Party proposals:\n{}".format(json.dumps(response_json, indent=2, sort_keys=True)))
# :get_proposals_by_party__
