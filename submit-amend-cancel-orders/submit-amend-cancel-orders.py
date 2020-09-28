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

# __get_market:
# Request the identifier for the market to place on
url = f"{node_url_rest}/markets"
response = requests.get(url)
helpers.check_response(response)
marketID = response.json()["markets"][0]["id"]
# :get_market__

assert marketID != ""
print(f"Market found: {marketID}")

# __get_expiry_time:
# Request the current blockchain time, calculate an expiry time
response = requests.get(f"{node_url_rest}/time")
helpers.check_response(response)
blockchain_time = int(response.json()["timestamp"])
expiresAt = str(int(blockchain_time + 120 * 1e9))  # expire in 2 minutes
# :get_expiry_time__

assert blockchain_time > 0
print(f"Blockchain time: {blockchain_time}")

# __prepare_submit_order:
# Prepare a submit order message
req = {
    "submission": {
        "marketID": marketID,
        "partyID": pubkey,
        "price": "1",  # Note: price is an integer. For example 123456
        "size": "100",  # is a price of 1.23456, assuming 5 decimal places.
        "side": "SIDE_BUY",
        "timeInForce": "TIF_GTT",
        "expiresAt": expiresAt,
        "type": "TYPE_LIMIT",
    }
}
url = f"{node_url_rest}/orders/prepare/submit"
response = requests.post(url, json=req)
helpers.check_response(response)
prepared_order = response.json()
# :prepare_submit_order__

order_ref = prepared_order["submitID"]
print(f"Prepared order, ref: {order_ref}")

# __sign_tx_order:
# Sign the prepared transaction
# Note: Setting propagate to true will also submit to a Vega node
blob = prepared_order["blob"]
req = {"tx": blob, "pubKey": pubkey, "propagate": True}
url = f"{wallet_server_url}/api/v1/messages"
response = requests.post(url, headers=headers, json=req)
helpers.check_response(response)
# :sign_tx_order__

print("Signed order and sent to Vega")

# Wait for order submission to be included in a block
print("Waiting for blockchain...", end="", flush=True)
url = f"{node_url_rest}/orders/{order_ref}"
response = requests.get(url)
while response.status_code != 200:
  print(".", end="", flush=True)
  response = requests.get(url)

response_json = response.json()
orderID = response_json["order"]["id"]
orderStatus = response_json["order"]["status"]
print(f"\nOrder processed, ID: {orderID}, Status: {orderStatus}")

# -----------------------------
# TODO: Order amendment >= 0.25
# -----------------------------

# __prepare_cancel_order:
# Prepare a cancel order message
req = {
    "cancellation": {
        "partyID": pubkey,
        "marketID": marketID,
        "orderID": orderID,
    }
}
url = f"{node_url_rest}/orders/prepare/cancel"
response = requests.post(url, json=req)
helpers.check_response(response)
prepared_cancel = response.json()
blob = prepared_cancel["blob"]
# :prepare_cancel_order__

print(f"Cancellation prepared for order ID: {orderID}")

# __sign_tx_cancel:
# Sign the prepared transaction for cancellation
# Note: Setting propagate to true will also submit to a Vega node
req = {"tx": blob, "pubKey": pubkey, "propagate": True}
url = f"{wallet_server_url}/api/v1/messages"
response = requests.post(url, headers=headers, json=req)
helpers.check_response(response)
# :sign_tx_cancel__

print("Signed cancellation and sent to Vega")

# Wait for cancellation to be included in a block
print("Waiting for blockchain...")
time.sleep(2.5)
url = f"{node_url_rest}/orders/{order_ref}"
response = requests.get(url)
response_json = response.json()
orderID = response_json["order"]["id"]
orderStatus = response_json["order"]["status"]

# Completed.
print("Cancelled Order:")
print(f"ID: {orderID}, Status: {orderStatus}")
