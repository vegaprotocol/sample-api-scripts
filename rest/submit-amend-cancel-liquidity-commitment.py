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
market_id = "3aa2a828687cc3d59e92445d294891cbbd40e2165bbfb15674158ef5d4e8848d"

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


# Send liqudity commitment
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

print(json.dumps(send_response.json(), indent=4, sort_keys=True))
print()

print("Signed liquidity commitment and sent to Vega")
print()

# Wait for cancellation to be included in a block
print("Waiting for blockchain...")
time.sleep(3)

#####################################################################################
#                 L I S T   L I Q U I D I T Y   P R O V I S I O N S                 #
#####################################################################################

#__get_liquidity_provisions:
# Request liquidity provisions for a party on a Vega network
url = f"{data_node_url_rest}/liquidity/provisions?partyId={pubkey}"
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(url)
helpers.check_response(response)
print("Liquidity Provisions for party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
#:get_liquidity_provisions__

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

# First sign liquidity commitment
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


print("Liquidity commitment amendment:\n{}".format(
    json.dumps(submission, indent=2, sort_keys=True)
))


print("Signed liquidity commitment amendment and sent to Vega")

if CANCEL_LP_AFTER_SUBMISSION is not True:
    exit(1)

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
# First sign liquidity commitment
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

# :sign_tx_liquidity_cancel__

print("Signed liquidity commitment cancellation and sent to Vega")

# Wait for cancellation to be included in a block
print("Waiting for blockchain...")
time.sleep(3)
