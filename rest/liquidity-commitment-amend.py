#!/usr/bin/python3

import json
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
#               A M E N D    L I Q U I D I T Y   C O M M I T M E N T                #
#####################################################################################

# __amend_liquidity_commitment:
# Compose a liquidity commitment order message
# (it will now serve as an amendment request):
# modify fields you want to be amended
submission = {
    "liquidityProvisionAmendment": {
        "marketId": market_id,
        "commitmentAmount": "500000000000000000000",
        "fee": "0.005",
        "buys": [
            {
                "offset": "1",
                "proportion": "1",
                "reference": "PEGGED_REFERENCE_MID"
            }
        ],
        "sells": [
            {
                "offset": "1",
                "proportion": "1",
                "reference": "PEGGED_REFERENCE_MID"
            }
        ]
    },
    "pubKey": pubkey,
    "propagate": True
}
# :amend_liquidity_commitment__

print("Liquidity commitment amendment:\n{}".format(
    json.dumps(submission, indent=2, sort_keys=True)
))

# __sign_tx_liquidity_amend:
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
# :sign_tx_liquidity_amend__

print("Signed liquidity commitment amendment and sent to Vega")

if CANCEL_LP_AFTER_SUBMISSION is not True:
    exit(1)
