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
market_id = "e503cadb437861037cddfd7263d25b69102098a97573db23f8e5fc320cea1ce9"

#####################################################################################
#                          B L O C K C H A I N   T I M E                            #
#####################################################################################

# __get_expiry_time:
# Request the current blockchain time, calculate an expiry time
response = requests.get(f"{data_node_url_rest}/vega/time")
helpers.check_response(response)
blockchain_time = int(response.json()["timestamp"])
expiresAt = str(int(blockchain_time + 120 * 1e9))  # expire in 2 minutes
# :get_expiry_time__

assert blockchain_time > 0
print(f"Blockchain time: {blockchain_time}")

#####################################################################################
#                      S U B M I T   P E G G E D   O R D E R                        #
#####################################################################################

# __submit_pegged_order:
# Compose your submit pegged order command
# Set your own user specific reference to find the order in next step and
# as a foreign key to your local client/trading application
order_ref = f"{pubkey}-{helpers.generate_id(30)}"
submission = {
    "orderSubmission": {
        "marketId": market_id,
        "size": "50",
        "side": "SIDE_BUY",
        "timeInForce": "TIME_IN_FORCE_GTT",
        "expiresAt": expiresAt,
        "type": "TYPE_LIMIT",
        "reference": order_ref,
        "peggedOrder": {
            "offset": "5",
            "reference": "PEGGED_REFERENCE_MID"
        }
    },
    "pubKey": pubkey,
    "propagate": True
}
# :submit_pegged_order__

print()
print("Pegged order submission: ", json.dumps(submission, indent=2, sort_keys=True))
print()

# __sign_tx_pegged_order:
# Sign the transaction with a pegged order submission command
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
# :sign_tx_pegged_order__

print(json.dumps(response.json(), indent=4, sort_keys=True))
print()

print("Signed pegged order and sent to Vega")

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
orderPegged = found_order["peggedOrder"]

print()
print(f"\nPegged order processed, ID: {orderID}, Status: {orderStatus}, Version: {createVersion}")
if orderStatus == "STATUS_REJECTED":
    print("The pegged order was rejected by Vega")
    exit(1)  # Halt processing at this stage
else:
    print(f"Pegged at: {orderPegged}")

#####################################################################################
#                        A M E N D   P E G G E D   O R D E R                        #
#####################################################################################

# __amend_pegged_order:
# Compose your amend order command, with changes to existing order
amendment = {
    "orderAmendment": {
        "orderId": orderID,
        "marketId": market_id,
        "sizeDelta": "25",
        "timeInForce": "TIME_IN_FORCE_GTC",
        "peggedReference": "PEGGED_REFERENCE_BEST_BID",
        "peggedOffset": "-100",
    },
    "pubKey": pubkey,
    "propagate": True
}
# :amend_pegged_order__

print()
print("Pegged order amendment: ", json.dumps(amendment, indent=2, sort_keys=True))
print()

# __sign_tx_pegged_amend:
# Sign the transaction with a pegged order amendment command
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
# :sign_tx_pegged_amend__

print("Signed pegged order amendment and sent to Vega")

# Wait for order amendment to be included in a block
print("Waiting for blockchain...")
time.sleep(3)

url = f"{data_node_url_rest}/orders?partyId={pubkey}&reference={order_ref}"
response = requests.get(url)

found_order = helpers.get_nested_response(response, "orders")[0]["node"]

orderID = found_order["id"]
orderStatus = found_order["status"]
orderVersion = found_order["version"]
orderPegged = found_order["peggedOrder"]
orderPrice = found_order["price"]
orderSize = found_order["size"]
orderTif = found_order["timeInForce"]

print()
print("Amended pegged order:")
print(f"ID: {orderID}, Status: {orderStatus}, "
      f"Size(Old): 50, Size(New): {orderSize}, "
      f"TimeInForce(Old): TIME_IN_FORCE_GTT, TimeInForce(New): {orderTif}, "
      f"Version(Old): {createVersion}, Version(new): {orderVersion}")

if orderStatus == "STATUS_REJECTED":
    print("The pegged order amendment was rejected by Vega")
    exit(1)  # Halt processing at this stage
else:
    print(f"Pegged at: {orderPegged}")

#####################################################################################
#                      C A N C E L   P E G G E D   O R D E R                        #
#####################################################################################

# Hint: For a full example with combinations please see submit-amend-cancel-order.py

# __cancel_pegged_order:
# # Cancellation command for the specific order
cancellation = {
    "orderCancellation": {
        # Include market and order identifier fields to cancel single order.
        "marketId": market_id,
        "orderId": orderID,
    },
    "pubKey": pubkey,
    "propagate": True,
}
# :cancel_pegged_order__

print()
print("Pegged order cancellation: ", json.dumps(cancellation, indent=2, sort_keys=True))
print()

# __sign_tx_pegged_cancel:
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
# :sign_tx_pegged_cancel__

print("Signed pegged cancellation and sent to Vega")
print()

# Wait for cancellation to be included in a block
print("Waiting for blockchain...")
time.sleep(3)

url = f"{data_node_url_rest}/orders?partyId={pubkey}&reference={order_ref}"
response = requests.get(url)

found_order = helpers.get_nested_response(response, "orders")[0]["node"]

orderID = found_order["id"]
orderStatus = found_order["status"]

print("Cancelled pegged order:")
print(f"ID: {orderID}, Status: {orderStatus}")
if orderStatus == "STATUS_REJECTED":
    print("The pegged order cancellation was rejected by Vega")
    exit(1)  # Halt processing at this stage

print("Pegged order cancelled")
