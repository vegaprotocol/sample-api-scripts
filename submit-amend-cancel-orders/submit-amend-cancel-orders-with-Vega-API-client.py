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

import base64
import helpers
import requests
import time
import os

from google.protobuf.empty_pb2 import Empty

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
trading_client = vac.VegaTradingClient(node_url_grpc)
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

# __get_market:
# Request the identifier for the market to place on
markets = data_client.Markets(Empty()).markets
marketID = markets[0].id
# :get_market__

assert marketID != ""
print(f"Market found: {marketID}")

#####################################################################################
#                          B L O C K C H A I N   T I M E                            #
#####################################################################################

# __get_expiry_time:
# Request the current blockchain time, calculate an expiry time
blockchain_time = data_client.GetVegaTime(Empty()).timestamp
expiresAt = int(blockchain_time + 120 * 1e9)  # expire in 2 minutes
# :get_expiry_time__

assert blockchain_time > 0
print(f"Blockchain time: {blockchain_time}")

#####################################################################################
#                              S U B M I T   O R D E R                              #
#####################################################################################

# __prepare_submit_order:
# Prepare a submit order message
order = vac.api.trading.SubmitOrderRequest(
    submission=vac.vega.OrderSubmission(
        marketID=marketID,
        partyID=pubkey,
        # price is an integer. For example 123456 is a price of 1.23456,
        # assuming 5 decimal places.
        price=1,
        side=vac.vega.Side.SIDE_BUY,
        size=10,
        expiresAt=expiresAt,
        timeInForce=vac.vega.Order.TimeInForce.TIF_GTT,
        type=vac.vega.Order.Type.TYPE_LIMIT,
    )
)
prepared_order = trading_client.PrepareSubmitOrder(order)
# :prepare_submit_order__

order_ref = prepared_order.submitID
print(f"Prepared order, ref: {order_ref}")

# __sign_tx_order:
# Sign the prepared transaction
# Note: Setting propagate to true will submit to a Vega node
blob_base64 = base64.b64encode(prepared_order.blob).decode("ascii")
req = {"tx": blob_base64, "pubKey": pubkey, "propagate": True}
url = f"{wallet_server_url}/api/v1/messages"
response = requests.post(url, headers=headers, json=req)
helpers.check_response(response)
signedTx = response.json()["signedTx"]
# :sign_tx_order__

print("Signed order and sent to Vega")

# Wait for order submission to be included in a block
print("Waiting for blockchain...")
time.sleep(2.5)
order_ref_request = vac.api.trading.OrderByReferenceRequest(reference=order_ref)
response = data_client.OrderByReference(order_ref_request)
orderID = response.order.id

print("Order processed:")
print(response)

#####################################################################################
#                               A M E N D   O R D E R                               #
#####################################################################################

# -----------------------------------
# TODO: Order amendment [coming soon]
# -----------------------------------

#####################################################################################
#                             C A N C E L   O R D E R S                             #
#####################################################################################

# Select the mode to cancel orders from the following (comment out others), default = 3

# __prepare_cancel_order_req1:
# 1 - Cancel single order for party (pubkey)
cancel = vac.vega.OrderCancellation(
    # Include party, market and order identifier fields to cancel single order.
    marketID=marketID,
    partyID=pubkey,
    orderID=orderID,
)
# :prepare_cancel_order_req1__

# __prepare_cancel_order_req2:
# 2 - Cancel all orders on market for party (pubkey)
cancel = vac.vega.OrderCancellation(
    # Only include party & market identifier fields.
    marketID=marketID,
    partyID=pubkey,
)
# :prepare_cancel_order_req2__

# __prepare_cancel_order_req3:
# 3 - Cancel all orders on all markets for party (pubkey)
cancel = vac.vega.OrderCancellation(
    # Only include party identifier field.
    partyID=pubkey,
)
# :prepare_cancel_order_req3__

# __prepare_cancel_order:
# Prepare the cancel order message
order = vac.api.trading.CancelOrderRequest(cancellation=cancel)
prepared_order = trading_client.PrepareCancelOrder(order)
blob_base64 = base64.b64encode(prepared_order.blob).decode("ascii")
# :prepare_cancel_order__

print(f"Cancellation prepared for order ID: {orderID}")

# __sign_tx_cancel:
# Sign the prepared order transaction for cancellation
# Note: Setting propagate to true will submit to a Vega node
req = {"tx": blob_base64, "pubKey": pubkey, "propagate": True}
url = f"{wallet_server_url}/api/v1/messages"
response = requests.post(url, headers=headers, json=req)
helpers.check_response(response)
# :sign_tx_cancel__

print("Signed cancellation and sent to Vega")

# Wait for cancellation to be included in a block
print("Waiting for blockchain...")
time.sleep(3)
order_ref_request = vac.api.trading.OrderByReferenceRequest(reference=order_ref)
response = data_client.OrderByReference(order_ref_request)

# Completed.
print("Cancelled Order:")
print(response)
