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
# Hint: Setting propagate to true will also submit to a Vega node
url = f"{wallet_server_url}/api/v2/requests"
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(url, headers=headers, json=submission)
helpers.check_response(response)
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