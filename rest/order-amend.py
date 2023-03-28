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
# Hint: Setting propagate to true will also submit to a Vega node
url = f"{wallet_server_url}/api/v2/requests"
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(url, headers=headers, json=amendment)
helpers.check_response(response)
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
