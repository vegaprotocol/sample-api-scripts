#!/usr/bin/python3

import json
import time
import requests
import helpers

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

# Set to False to ONLY submit/amend a liquidity commitment (no cancellation)
CANCEL_LP_AFTER_SUBMISSION = True

# Set market id in ENV or uncomment the line below to override market id directly
market_id = "e503cadb437861037cddfd7263d25b69102098a97573db23f8e5fc320cea1ce9"

#####################################################################################
#              S U B M I T   L I Q U I D I T Y   C O M M I T M E N T                #
#####################################################################################

# Hint: commitmentAmount is an integer. For example 123456 is a price of 1.23456,
# for a market which is configured to have a precision of 5 decimal places.

# __create_liquidity_commitment:
# Compose your submit liquidity provision command
# Set your own user specific reference to find the commitment by reference and
# as a foreign key to your local client/trading application
liquidity_ref = f"{pubkey}-{helpers.generate_id(30)}"
submission = {
    "liquidityProvisionSubmission": {
        "marketId": market_id,
        "commitmentAmount": "100",
        "fee": "0.01",
        "buys": [
            {
                "offset": "1",
                "proportion": "1",
                "reference": "PEGGED_REFERENCE_MID"
            },
            {
                "offset": "2",
                "proportion": "2",
                "reference": "PEGGED_REFERENCE_MID"
            }
        ],
        "sells": [
            {
                "offset": "1",
                "proportion": "1",
                "reference": "PEGGED_REFERENCE_MID"
            },
            {
                "offset": "2",
                "proportion": "2",
                "reference": "PEGGED_REFERENCE_MID"
            },
            {
                "offset": "3",
                "proportion": "5",
                "reference": "PEGGED_REFERENCE_MID"
            }
        ],
        "reference": liquidity_ref
    },
    "pubKey": pubkey,
    "propagate": True
}
# :create_liquidity_commitment__

print("Liquidity commitment submission:\n{}".format(
    json.dumps(submission, indent=2, sort_keys=True)
))

# __sign_tx_liquidity_submit:
# Sign the transaction with an liquidity commitment command
# Hint: Setting propagate to true will also submit to a Vega node
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

send_response = requests.request("POST", url, headers=headers, data=payload)

print(send_response.text)
# :sign_tx_liquidity_submit__

print(json.dumps(response.json(), indent=4, sort_keys=True))
print()

print("Signed liquidity commitment and sent to Vega")
print()

# Wait for cancellation to be included in a block
print("Waiting for blockchain...")
time.sleep(3)
