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

# Set market id in ENV or uncomment the line below to override market id directly
market_id = "e503cadb437861037cddfd7263d25b69102098a97573db23f8e5fc320cea1ce9"

#####################################################################################
#                C A N C E L   L I Q U I D I T Y   C O M M I T M E N T              #
#####################################################################################

# __cancel_liquidity_commitment:
# Compose a liquidity commitment cancellation command
# Hint: The transaction may get rejected if removing previously supplied liquidity
# will result in insufficient liquidity for the market to operate
submission = {
    "liquidityProvisionCancellation": {
        "marketId": market_id,
    },
    "pubKey": pubkey,
    "propagate": True
}
# :cancel_liquidity_commitment__

print("Liquidity commitment cancellation:\n{}".format(
    json.dumps(submission, indent=2, sort_keys=True)
))

# __sign_tx_liquidity_cancel:
# Sign the transaction with an order submission command
# Hint: Setting propagate to true will also submit to a Vega node
url = f"{wallet_server_url}/api/v2/requests"
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(url, headers=headers, json=submission)
helpers.check_response(response)
# :sign_tx_liquidity_cancel__

print("Signed liquidity commitment cancellation and sent to Vega")

# Wait for cancellation to be included in a block
print("Waiting for blockchain...")
time.sleep(3)
