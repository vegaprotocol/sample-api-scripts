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

# __get_market:
# Request the identifier for the market to place on
markets = data_client.Markets(vac.data_node.api.v1.trading_data.MarketsRequest()).markets
marketID = markets[0].id
# :get_market__

assert marketID != ""
print(f"Market found: {marketID}")

#####################################################################################
#                          B L O C K C H A I N   T I M E                            #
#####################################################################################

# __get_expiry_time:
# Request the current blockchain time, calculate an expiry time
blockchain_time = data_client.GetVegaTime(vac.data_node.api.v1.trading_data.GetVegaTimeRequest()).timestamp
expiresAt = int(blockchain_time + 120 * 1e9)  # expire in 2 minutes
# :get_expiry_time__

assert blockchain_time > 0
print(f"Blockchain time: {blockchain_time}")

#####################################################################################
#                              S U B M I T   O R D E R                              #
#####################################################################################

# __prepare_submit_order:
# Compose your submit order command, with desired deal ticket information
# Set your own user specific reference to find the order in next step and
# as a foreign key to your local client/trading application
order_ref = f"{pubkey}-{uuid.uuid4()}"
order_data = vac.vega.commands.v1.commands.OrderSubmission(
    market_id=marketID,
    # price is an integer. For example 123456 is a price of 1.23456,
    # assuming 5 decimal places.
    price="1",
    side=vac.vega.vega.Side.SIDE_BUY,
    size=10,
    expires_at=expiresAt,
    time_in_force=vac.vega.vega.Order.TimeInForce.TIME_IN_FORCE_GTT,
    type=vac.vega.vega.Order.Type.TYPE_LIMIT,
    reference=order_ref
)
# :prepare_submit_order__

# __sign_tx_order:
# Sign the transaction with an order submission command
# Note: Setting propagate to true will also submit to a Vega node
submission = {
    "orderSubmission": MessageToDict(order_data),
    "pubKey": pubkey,
    "propagate": True
}
url = f"{wallet_server_url}/api/v1/command/sync"
response = requests.post(url, headers=headers, json=submission)
helpers.check_response(response)
# :sign_tx_order__

print("Signed order and sent to Vega")

# Wait for order submission to be included in a block
print("Waiting for blockchain...")
time.sleep(4)
order_ref_request = vac.data_node.api.v1.trading_data.OrderByReferenceRequest(reference=order_ref)
response = data_client.OrderByReference(order_ref_request)
orderID = response.order.id
orderStatus = helpers.enum_to_str(vac.vega.vega.Order.Status, response.order.status)
createVersion = response.order.version
orderReason = response.order.reason
print(f"Order processed, ID: {orderID}, Status: {orderStatus}, Version: {createVersion}")
if orderStatus == "STATUS_REJECTED":
    print(f"Rejection reason: {orderReason}")

#####################################################################################
#                               A M E N D   O R D E R                               #
#####################################################################################

# __prepare_amend_order:
# Compose your amend order command, with changes to your existing order
amend_data = vac.vega.commands.v1.commands.OrderAmendment(
    market_id=marketID,
    order_id=orderID,
    price=vac.vega.vega.Price(value=2),
    time_in_force=vac.vega.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
)
# :prepare_amend_order__

# __sign_tx_amend:
# Sign the prepared order transaction with an order amendment command
# Note: Setting propagate to true will also submit to a Vega node
amendment = {
    "orderAmendment": MessageToDict(amend_data),
    "pubKey": pubkey,
    "propagate": True
}
url = f"{wallet_server_url}/api/v1/command/sync"
response = requests.post(url, headers=headers, json=amendment)
helpers.check_response(response)
# :sign_tx_amend__

print("Signed amendment and sent to Vega")

# Wait for amendment to be included in a block
print("Waiting for blockchain...")
time.sleep(4)
order_id_request = vac.data_node.api.v1.trading_data.OrderByIDRequest(order_id=orderID)
response = data_client.OrderByID(order_id_request)

orderID = response.order.id
orderPrice = response.order.price
orderSize = response.order.size
orderTif = helpers.enum_to_str(vac.vega.vega.Order.TimeInForce, response.order.time_in_force)
orderStatus = helpers.enum_to_str(vac.vega.vega.Order.Status, response.order.status)
orderVersion = response.order.version
orderReason = response.order.reason

print("Amended Order:")
print(f"ID: {orderID}, Status: {orderStatus}, Price(Old): 1, "
      f"Price(New): {orderPrice}, Size(Old): 100, Size(New): {orderSize}, "
      f"TimeInForce(Old): TIME_IN_FORCE_GTT, TimeInForce(New): {orderTif}, "
      f"Version(Old): {createVersion}, Version(new): {orderVersion}")
if orderStatus == "STATUS_REJECTED":
    print(f"Rejection reason: {orderReason}")

#####################################################################################
#                             C A N C E L   O R D E R S                             #
#####################################################################################

# Select the mode to cancel orders from the following (comment out others), default = 3

# __prepare_cancel_order_req1:
# 1 - Cancel single order for party (pubkey)
cancel_data = vac.vega.commands.v1.commands.OrderCancellation(
    # Include party, market and order identifier fields to cancel single order.
    market_id=marketID,
    order_id=orderID,
)
# :prepare_cancel_order_req1__

# __prepare_cancel_order_req2:
# 2 - Cancel all orders on market for party (pubkey)
cancel_data = vac.vega.commands.v1.commands.OrderCancellation(
    # Only include market identifier field.
    market_id=marketID,
)
# :prepare_cancel_order_req2__

# __prepare_cancel_order_req3:
# 3 - Cancel all orders on all markets for party (pubkey)
cancel_data = vac.vega.commands.v1.commands.OrderCancellation(
    # No filters, cancel all
)
# :prepare_cancel_order_req3__

# __sign_tx_cancel:
# Sign the transaction for cancellation
# Note: Setting propagate to true will also submit to a Vega node
cancellation = {
    "orderCancellation": MessageToDict(cancel_data),
    "pubKey": pubkey,
    "propagate": True
}
url = f"{wallet_server_url}/api/v1/command/sync"
response = requests.post(url, headers=headers, json=cancellation)
helpers.check_response(response)
# :sign_tx_cancel__

print("Signed cancellation and sent to Vega")

# Wait for cancellation to be included in a block
print("Waiting for blockchain...")
time.sleep(4)
order_ref_request = vac.data_node.api.v1.trading_data.OrderByReferenceRequest(reference=order_ref)
response = data_client.OrderByReference(order_ref_request)
orderStatus = helpers.enum_to_str(vac.vega.vega.Order.Status, response.order.status)
orderReason = response.order.reason

print("Cancelled Order:")
print(f"ID: {orderID}, Status: {orderStatus}")
if orderStatus == "STATUS_REJECTED":
    print(f"Rejection reason: {orderReason}")

# Completed.
