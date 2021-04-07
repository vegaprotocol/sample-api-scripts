#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (gRPC)

Apps/Libraries:
- gRPC: Vega-API-client (https://pypi.org/project/Vega-API-client/)
"""

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__

import helpers
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
#                               F I N D   M A R K E T                               #
#####################################################################################

# __get_market:
# Request the identifier for the market to place on
markets = data_client.Markets(vac.api.trading.MarketsRequest()).markets
marketID = markets[0].id
# :get_market__

assert marketID != ""
print(f"Market found: {marketID}")

#####################################################################################
#                           F E E   E S T I M A T I O N                             #
#####################################################################################

# __get_fees_estimate:
# Request to estimate trading fees on a Vega network
estimate = vac.api.trading.EstimateFeeRequest(
    order=vac.vega.Order(
        market_id=marketID,
        party_id=pubkey,
        price=100000,
        size=100,
        side=vac.vega.Side.SIDE_BUY,
        time_in_force=vac.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
        type=vac.vega.Order.Type.TYPE_LIMIT,
    )
)
estimated_fees = data_client.EstimateFee(estimate)
print("FeeEstimates:\n{}".format(estimated_fees))
# :get_fees_estimate__

#####################################################################################
#                         M A R G I N   E S T I M A T I O N                         #
#####################################################################################

# __get_margins_estimate:
# Request to estimate trading margin on a Vega network
estimate = vac.api.trading.EstimateMarginRequest(
    order=vac.vega.Order(
        market_id=marketID,
        party_id=pubkey,
        price=600000,
        size=10,
        side=vac.vega.Side.SIDE_BUY,
        time_in_force=vac.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
        type=vac.vega.Order.Type.TYPE_LIMIT,
    )
)
estimated_margins = data_client.EstimateMargin(estimate)
print("MarginEstimates:\n{}".format(estimated_margins))
# :get_margins_estimate__
