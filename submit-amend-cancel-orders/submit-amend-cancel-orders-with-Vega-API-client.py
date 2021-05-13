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
trading_client = vac.VegaTradingClient(node_url_grpc)
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
#                          B L O C K C H A I N   T I M E                            #
#####################################################################################

# __get_expiry_time:
# Request the current blockchain time, calculate an expiry time
blockchain_time = data_client.GetVegaTime(vac.api.trading.GetVegaTimeRequest()).timestamp
expiresAt = int(blockchain_time + 120 * 1e9)  # expire in 2 minutes
# :get_expiry_time__

assert blockchain_time > 0
print(f"Blockchain time: {blockchain_time}")

#####################################################################################
#                              S U B M I T   O R D E R                              #
#####################################################################################

# __prepare_submit_order:
# Prepare a submit order message
order = vac.api.trading.PrepareSubmitOrderRequest(
    submission=vac.commands.v1.commands.OrderSubmission(
        market_id=marketID,
        # price is an integer. For example 123456 is a price of 1.23456,
        # assuming 5 decimal places.
        price=1,
        side=vac.vega.Side.SIDE_BUY,
        size=10,
        expires_at=expiresAt,
        time_in_force=vac.vega.Order.TimeInForce.TIME_IN_FORCE_GTT,
        type=vac.vega.Order.Type.TYPE_LIMIT,
    )
)
prepared_order = trading_client.PrepareSubmitOrder(order)
# :prepare_submit_order__

order_ref = prepared_order.submit_id
print(f"Prepared order, ref: {order_ref}")

# __sign_tx_order:
# Sign the prepared transaction
# Note: Setting propagate to true will submit to a Vega node
blob_base64 = base64.b64encode(prepared_order.blob).decode("ascii")
response = wallet_client.signtx(blob_base64, pubkey, True)
helpers.check_response(response)
signedTx = response.json()["signedTx"]
# :sign_tx_order__

print("Signed order and sent to Vega")

# Wait for order submission to be included in a block
print("Waiting for blockchain...")
time.sleep(4)
order_ref_request = vac.api.trading.OrderByReferenceRequest(reference=order_ref)
response = data_client.OrderByReference(order_ref_request)
orderID = response.order.id
orderStatus = helpers.enum_to_str(vac.vega.Order.Status, response.order.status)
createVersion = response.order.version
orderReason = response.order.reason
print(f"Order processed, ID: {orderID}, Status: {orderStatus}, Version: {createVersion}")
if orderStatus == "STATUS_REJECTED":
    print(f"Rejection reason: {orderReason}")

#####################################################################################
#                               A M E N D   O R D E R                               #
#####################################################################################

# __prepare_amend_order:
# Prepare the amend order message
amend = vac.commands.v1.commands.OrderAmendment(
    market_id=marketID,
    order_id=orderID,
    price=vac.vega.Price(value=2),
    time_in_force=vac.vega.Order.TimeInForce.TIME_IN_FORCE_GTC,
)
order = vac.api.trading.PrepareAmendOrderRequest(amendment=amend)
prepared_order = trading_client.PrepareAmendOrder(order)
blob_base64 = base64.b64encode(prepared_order.blob).decode("ascii")
# :prepare_amend_order__

print(f"Amendment prepared for order ID: {orderID}")

# __sign_tx_amend:
# Sign the prepared order transaction for amendment
# Note: Setting propagate to true will also submit to a Vega node
response = wallet_client.signtx(blob_base64, pubkey, True)
helpers.check_response(response)
# :sign_tx_amend__

print("Signed amendment and sent to Vega")

# Wait for amendment to be included in a block
print("Waiting for blockchain...")
time.sleep(4)
order_id_request = vac.api.trading.OrderByIDRequest(order_id=orderID)
response = data_client.OrderByID(order_id_request)

orderID = response.order.id
orderPrice = response.order.price
orderSize = response.order.size
orderTif = helpers.enum_to_str(vac.vega.Order.TimeInForce, response.order.time_in_force)
orderStatus = helpers.enum_to_str(vac.vega.Order.Status, response.order.status)
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
cancel = vac.commands.v1.commands.OrderCancellation(
    # Include party, market and order identifier fields to cancel single order.
    market_id=marketID,
    order_id=orderID,
)
# :prepare_cancel_order_req1__

# __prepare_cancel_order_req2:
# 2 - Cancel all orders on market for party (pubkey)
cancel = vac.vega.OrderCancellation(
    # Only include party & market identifier fields.
    market_id=marketID,
    party_id=pubkey,
)
# :prepare_cancel_order_req2__

# __prepare_cancel_order_req3:
# 3 - Cancel all orders on all markets for party (pubkey)
cancel = vac.vega.OrderCancellation(
    # Only include party identifier field.
    party_id=pubkey,
)
# :prepare_cancel_order_req3__

# __prepare_cancel_order:
# Prepare the cancel order message
order = vac.api.trading.PrepareCancelOrderRequest(cancellation=cancel)
prepared_order = trading_client.PrepareCancelOrder(order)
blob_base64 = base64.b64encode(prepared_order.blob).decode("ascii")
# :prepare_cancel_order__

print(f"Cancellation prepared for order ID: {orderID}")

# __sign_tx_cancel:
# Sign the prepared order transaction for cancellation
# Note: Setting propagate to true will submit to a Vega node
response = wallet_client.signtx(blob_base64, pubkey, True)
helpers.check_response(response)
# :sign_tx_cancel__

print("Signed cancellation and sent to Vega")

# Wait for cancellation to be included in a block
print("Waiting for blockchain...")
time.sleep(4)
order_ref_request = vac.api.trading.OrderByReferenceRequest(reference=order_ref)
response = data_client.OrderByReference(order_ref_request)
orderStatus = helpers.enum_to_str(vac.vega.Order.Status, response.order.status)
orderReason = response.order.reason

print("Cancelled Order:")
print(f"ID: {orderID}, Status: {orderStatus}")
if orderStatus == "STATUS_REJECTED":
    print(f"Rejection reason: {orderReason}")

# Completed.
