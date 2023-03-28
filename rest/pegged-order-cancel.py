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

# Grab order reference from original order submission
order_ref = "" 

url = f"{data_node_url_rest}/orders?partyId={pubkey}&reference={order_ref}"
response = requests.get(url)

found_order = helpers.get_nested_response(response, "orders")[0]["node"]

orderID = found_order["id"]
orderStatus = found_order["status"]
createVersion = found_order["version"]
orderPegged = found_order["peggedOrder"]
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
# Hint: Setting propagate to true will also submit to a Vega node
url = f"{wallet_server_url}/api/v2/requests"
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(url, headers=headers, json=cancellation)
helpers.check_response(response)
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
