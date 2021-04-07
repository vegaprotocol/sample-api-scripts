#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega wallet (REST)
- Vega node (REST)

Apps/Libraries:
- REST: requests (https://pypi.org/project/requests/)
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

import json
import os
import requests
import time
import helpers

node_url_rest = os.getenv("NODE_URL_REST")
if not helpers.check_url(node_url_rest):
    print("Error: Invalid or missing NODE_URL_REST environment variable.")
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
url = f"{node_url_rest}/markets"
response = requests.get(url)
helpers.check_response(response)
marketID = response.json()["markets"][0]["id"]
# :get_market__

assert marketID != ""
marketName = response.json()["markets"][0]["tradableInstrument"]["instrument"]["name"]
print(f"Market found: {marketID} {marketName}")

#####################################################################################
#                          B L O C K C H A I N   T I M E                            #
#####################################################################################

# __get_expiry_time:
# Request the current blockchain time, calculate an expiry time
response = requests.get(f"{node_url_rest}/time")
helpers.check_response(response)
blockchain_time = int(response.json()["timestamp"])
expiresAt = str(int(blockchain_time + 120 * 1e9))  # expire in 2 minutes
# :get_expiry_time__

assert blockchain_time > 0
print(f"Blockchain time: {blockchain_time}")

#####################################################################################
#                      S U B M I T   P E G G E D   O R D E R                        #
#####################################################################################

# __prepare_submit_pegged_order:
# Prepare a submit order message with a pegged BUY order
req = {
    "submission": {
        "marketId": marketID,
        "partyId": pubkey,
        "size": "50",
        "side": "SIDE_BUY",
        "timeInForce": "TIME_IN_FORCE_GTT",
        "expiresAt": expiresAt,
        "type": "TYPE_LIMIT",
        "peggedOrder": {
            "offset": "-5",
            "reference": "PEGGED_REFERENCE_MID"
        }
    }
}
url = f"{node_url_rest}/orders/prepare/submit"
response = requests.post(url, json=req)
helpers.check_response(response)
prepared_order = response.json()
# :prepare_submit_pegged_order__

order_ref = prepared_order["submitId"]
print(f"Prepared pegged order, ref: {order_ref}")

# __sign_tx_pegged_order:
# Sign the prepared pegged order transaction
# Note: Setting propagate to true will also submit to a Vega node
blob = prepared_order["blob"]
req = {"tx": blob, "pubKey": pubkey, "propagate": True}
url = f"{wallet_server_url}/api/v1/messages/sync"
response = requests.post(url, headers=headers, json=req)
helpers.check_response(response)
# :sign_tx_pegged_order__

print("Signed pegged order and sent to Vega")

# Wait for order submission to be included in a block
print("Waiting for blockchain...", end="", flush=True)
url = f"{node_url_rest}/orders/{order_ref}"
response = requests.get(url)
while response.status_code != 200:
  time.sleep(0.5)
  print(".", end="", flush=True)
  response = requests.get(url)

response_json = response.json()
orderID = response_json["order"]["id"]
orderStatus = response_json["order"]["status"]
orderPegged = response_json["order"]["peggedOrder"]
createVersion = response_json["order"]["version"]
orderReason = response_json["order"]["reason"]
print(f"\nPegged order processed, ID: {orderID}, Status: {orderStatus}, Version: {createVersion}")
if orderStatus == "STATUS_REJECTED":
    print(f"Rejection reason: {orderReason}")
else:
    print(f"Pegged at: {orderPegged}")

#####################################################################################
#                        A M E N D   P E G G E D   O R D E R                        #
#####################################################################################

# __prepare_amend_pegged_order:
# Prepare the amend order message
req = {
    "amendment": {
        "orderId": orderID,
        "marketId": marketID,
        "partyId": pubkey,
        "sizeDelta": "25",
        "timeInForce": "TIME_IN_FORCE_GTC",
        "peggedReference": "PEGGED_REFERENCE_BEST_BID",
        "peggedOffset": "-100",
    }
}
url = f"{node_url_rest}/orders/prepare/amend"
response = requests.post(url, json=req)
helpers.check_response(response)
prepared_amend = response.json()
blob = prepared_amend["blob"]
# :prepare_amend_pegged_order__

print(f"Amendment prepared for order ID: {orderID}")

# __sign_tx_pegged_amend:
# Sign the prepared pegged order transaction for amendment
# Note: Setting propagate to true will also submit to a Vega node
req = {"tx": blob, "pubKey": pubkey, "propagate": True}
url = f"{wallet_server_url}/api/v1/messages/sync"
response = requests.post(url, headers=headers, json=req)
helpers.check_response(response)
# :sign_tx_pegged_amend__

print("Signed pegged order amendment and sent to Vega")

# Wait for amendment to be included in a block
print("Waiting for blockchain...")
time.sleep(4)
url = f"{node_url_rest}/orders/{order_ref}"
response = requests.get(url)
response_json = response.json()
orderID = response_json["order"]["id"]
orderPrice = response_json["order"]["price"]
orderSize = response_json["order"]["size"]
orderTif = response_json["order"]["timeInForce"]
orderStatus = response_json["order"]["status"]
orderPegged = response_json["order"]["peggedOrder"]
orderVersion = response_json["order"]["version"]
orderReason = response_json["order"]["reason"]

print("Amended pegged order:")
print(f"ID: {orderID}, Status: {orderStatus}, "
      f"Size(Old): 50, Size(New): {orderSize}, "
      f"TimeInForce(Old): TIME_IN_FORCE_GTT, TimeInForce(New): {orderTif}, "
      f"Version(Old): {createVersion}, Version(new): {orderVersion}")

if orderStatus == "STATUS_REJECTED":
    print(f"Rejection reason: {orderReason}")
else:
    print(f"Pegged at: {orderPegged}")


# Completed.
