#!/usr/bin/python3

import requests
import time
import helpers
import json

# Vega wallet interaction helper, see login.py for detail
from login import token, pubkey

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")
# Load Vega wallet server URL, set in same way as above
wallet_server_url = helpers.get_from_env("WALLET_SERVER_URL")

# Load Vega market id
market_id = helpers.env_market_id()
assert market_id != ""

# Set to False to ONLY submit/amend an order (no cancellation)
# e.g. orders will remain on the book
CANCEL_ORDER_AFTER_SUBMISSION = True

# Set market id in ENV or uncomment the line below to override market id directly
# market_id = "e503cadb437861037cddfd7263d25b69102098a97573db23f8e5fc320cea1ce9"

###############################################################################
#                          B L O C K C H A I N   T I M E                      #
###############################################################################

# __get_expiry_time:
# Request the current blockchain time, calculate an expiry time
response = requests.get(f"{data_node_url_rest}/vega/time")
helpers.check_response(response)
blockchain_time = int(response.json()["timestamp"])
expiresAt = str(int(blockchain_time + 120 * 1e9))  # expire in 2 minutes
# :get_expiry_time__

assert blockchain_time > 0
print(f"Blockchain time: {blockchain_time}")


###############################################################################
#                              S U B M I T   O R D E R                        #
###############################################################################

# __submit_order:
# Compose your submit order command, with desired deal ticket information
# Set your own user specific reference to find the order in next step and
# as a foreign key to your local client/trading application
order_ref = f"{pubkey}-{helpers.generate_id(30)}"
submission = {
    "orderSubmission": {
        "marketId": market_id,
        "price": "1",  # Hint: price is an integer. For example 123456
        "size": "100",  # is a price of 1.23456, assuming 5 decimal places.
        "side": "SIDE_BUY",
        "timeInForce": "TIME_IN_FORCE_GTT",
        "expiresAt": expiresAt,
        "type": "TYPE_LIMIT",
        "reference": order_ref
    },
    "pubKey": pubkey,
    "propagate": True
}
# :submit_order__

print("Order submission: ", json.dumps(submission, indent=2, sort_keys=True))
print()

# __sign_tx_order:
# Sign the transaction with an order submission command
url = "http://localhost:1789/api/v2/requests"

payload1 = {
    "id": "1",
    "jsonrpc": "2.0",
    "method": "client.send_transaction",
    "params": {
        "publicKey": pubkey,
        "sendingMode": "TYPE_SYNC",
        "transaction": submission
    }
}

payload = json.dumps(payload1)

headers = {
  'Content-Type': 'application/json-rpc',
  'Accept': 'application/json-rpc',
  'Origin': 'application/json-rpc', 
  'Authorization': f'{token}'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
# :sign_tx_order__

print(json.dumps(response.json(), indent=4, sort_keys=True))
print()

print("Signed order and sent to Vega")

# Wait for order submission to be included in a block
print("Waiting for blockchain...", end="", flush=True)
url = f"{data_node_url_rest}/orders?partyId={pubkey}&reference={order_ref}"
response = requests.get(url)
while helpers.check_nested_response(response, "orders") is not True:
    time.sleep(0.5)
    print(".", end="", flush=True)
    response = requests.get(url)

found_order = helpers.get_nested_response(response, "orders")[0]["node"]

orderID = found_order["id"]
orderStatus = found_order["status"]
createVersion = found_order["version"]

print()
print(f"\nOrder processed, ID: {orderID}, Status: {orderStatus}, Version: {createVersion}")
if orderStatus == "STATUS_REJECTED":
    print("The order was rejected by Vega")
    exit(1)  # Halt processing at this stage

#####################################################################################
#                               A M E N D   O R D E R                               #
#####################################################################################

# __amend_order:
# Compose your amend order command, with changes to existing order
amendment = {
    "orderAmendment": {
        "orderId": orderID,
        "marketId": market_id,
        "price": "2",
        "sizeDelta": "-25",
        "timeInForce": "TIME_IN_FORCE_GTC",
    },
    "pubKey": pubkey,
    "propagate": True
}
# :amend_order__

print()
print("Order amendment: ", json.dumps(amendment, indent=2, sort_keys=True))
print()

# __sign_tx_amend:
# Sign the transaction with an order amendment command
url = "http://localhost:1789/api/v2/requests"

payload1 = {
    "id": "1",
    "jsonrpc": "2.0",
    "method": "client.send_transaction",
    "params": {
        "publicKey": pubkey,
        "sendingMode": "TYPE_SYNC",
        "transaction": amendment
    }
}

payload = json.dumps(payload1)

headers = {
  'Content-Type': 'application/json-rpc',
  'Accept': 'application/json-rpc',
  'Origin': 'application/json-rpc', 
  'Authorization': f'{token}'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
# :sign_tx_amend__

print("Signed amendment and sent to Vega")

# Wait for amendment to be included in a block
print("Waiting for blockchain...", end="", flush=True)
time.sleep(3)

url = f"{data_node_url_rest}/orders?partyId={pubkey}&reference={order_ref}"
response = requests.get(url)

found_order = helpers.get_nested_response(response, "orders")[0]["node"]

orderID = found_order["id"]
orderPrice = found_order["price"]
orderSize = found_order["size"]
orderTif = found_order["timeInForce"]
orderStatus = found_order["status"]
orderVersion = found_order["version"]

print()
print("Amended Order:")
print(f"ID: {orderID}, Status: {orderStatus}, Price(Old): 1, "
      f"Price(New): {orderPrice}, Size(Old): 100, Size(New): {orderSize}, "
      f"TimeInForce(Old): TIME_IN_FORCE_GTT, TimeInForce(New): {orderTif}, "
      f"Version(Old): {createVersion}, Version(new): {orderVersion}")
if orderStatus == "STATUS_REJECTED":
    print("The order amendment was rejected by Vega")
    exit(1)  # Halt processing at this stage

if CANCEL_ORDER_AFTER_SUBMISSION is not True:
    exit(1)

#####################################################################################
#                             C A N C E L   O R D E R S                             #
#####################################################################################

# Select the mode to cancel orders from the following (comment out others), default = 3

# __cancel_order_req1:
# 1 - Cancel single order for party (pubkey)
cancellation = {
    "orderCancellation": {
        # Include market and order identifier fields to cancel single order.
        "marketId": market_id,
        "orderId": orderID,
    },
    "pubKey": pubkey,
    "propagate": True,
}
# :cancel_order_req1__

# __cancel_order_req2:
# 2 - Cancel all orders on market for party (pubkey)
cancellation = {
    "orderCancellation": {
        # Only include market identifier field.
        "marketId": market_id,
    },
    "pubKey": pubkey,
    "propagate": True,
}
# :cancel_order_req2__

# __cancel_order_req3:
# 3 - Cancel all orders on all markets for party (pubkey)
cancellation = {
    "orderCancellation": {},
    "pubKey": pubkey,
    "propagate": True,
}
# :cancel_order_req3__

print()
print("Order cancellation: ", json.dumps(cancellation, indent=2, sort_keys=True))
print()

# __sign_tx_cancel:
# Sign the transaction for cancellation
url = "http://localhost:1789/api/v2/requests"

payload1 = {
    "id": "1",
    "jsonrpc": "2.0",
    "method": "client.send_transaction",
    "params": {
        "publicKey": pubkey,
        "sendingMode": "TYPE_SYNC",
        "transaction": cancellation
    }
}

payload = json.dumps(payload1)

headers = {
  'Content-Type': 'application/json-rpc',
  'Accept': 'application/json-rpc',
  'Origin': 'application/json-rpc', 
  'Authorization': f'{token}'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
# :sign_tx_cancel__

print("Signed cancellation and sent to Vega")
print()

# Wait for cancellation to be included in a block
print("Waiting for blockchain...")
time.sleep(3)

url = f"{data_node_url_rest}/orders?partyId={pubkey}&reference={order_ref}"
response = requests.get(url)

found_order = helpers.get_nested_response(response, "orders")[0]["node"]

orderID = found_order["id"]
orderStatus = found_order["status"]

print("Cancelled Order(s):")
print(f"ID: {orderID}, Status: {orderStatus}")
if orderStatus == "STATUS_REJECTED":
    print("The order cancellation was rejected by Vega")
    exit(1)  # Halt processing at this stage

print("Order(s) cancelled")
