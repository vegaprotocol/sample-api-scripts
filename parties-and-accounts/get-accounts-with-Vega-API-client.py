#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (gRPC)

Apps/Libraries:
- Vega-API-client (https://pypi.org/project/Vega-API-client/)

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

import base64
import helpers
import time
import os

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

# Help guide users against including api version suffix on url
wallet_server_url = helpers.check_wallet_url(wallet_server_url)

# __import_client:
import vegaapiclient as vac

# Vega gRPC clients for reading/writing data
data_client = vac.VegaTradingDataClient(node_url_grpc)
wallet_client = vac.WalletClient(wallet_server_url)
# :import_client__

#####################################################################################
#                           W A L L E T   S E R V I C E                             #
#####################################################################################

print(f"Logging into wallet: {wallet_name}")

# __login_wallet:
# Log in to an existing wallet
response = wallet_client.login(wallet_name, wallet_passphrase)
helpers.check_response(response)
# Note: secret wallet token is stored internally for duration of session
# :login_wallet__

print("Logged in to wallet successfully")

# __get_pubkey:
# List key pairs and select public key to use
response = wallet_client.listkeys()
helpers.check_response(response)
keys = response.json()["keys"]
pubkey = keys[0]["pub"]
# :get_pubkey__

assert pubkey != ""
print("Selected pubkey for signing")

#####################################################################################
#                           M A R K E T   A C C O U N T S                           #
#####################################################################################

# Request a list of markets and select the first one
req = vac.api.trading.MarketsRequest()
markets = data_client.Markets(req).markets
marketID = markets[0].id

assert marketID != ""
print(f"Market found: {marketID}")

# __get_accounts_by_market:
# Request a list of accounts for a market on a Vega network
request = vac.api.trading.MarketAccountsRequest(market_id=marketID)
market_accounts = data_client.MarketAccounts(request)
print("Market accounts:\n{}".format(market_accounts))
# :get_accounts_by_market__

#####################################################################################
#                            P A R T Y   A C C O U N T S                            #
#####################################################################################

# __get_accounts_by_party:
# Request a list of accounts for a party (pubkey) on a Vega network
request = vac.api.trading.PartyAccountsRequest(party_id=pubkey)
party_accounts = data_client.PartyAccounts(request)
print("Party accounts:\n{}".format(party_accounts))
# :get_accounts_by_party__

#####################################################################################
#                           P A R T Y   P O S I T I O N S                           #
#####################################################################################

# __get_positions_by_party:
# Request a list of positions for a party (pubkey) on a Vega network
request = vac.api.trading.PositionsByPartyRequest(party_id=pubkey)
party_positions = data_client.PositionsByParty(request)
print("Party positions:\n{}".format(party_positions))
# :get_positions_by_party__
