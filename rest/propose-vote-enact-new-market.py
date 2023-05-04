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

# Set to True to optionally wait/block until the new market proposal is enacted
WAIT_FOR_MARKET_AFTER_VOTE = True

###############################################################################
#                            F I N D   A S S E T S                            #
###############################################################################

# __get_assets:
# Request a list of assets available and select the first one
url = f"{data_node_url_rest}/assets"
response = requests.get(url)
helpers.check_response(response)
# :get_assets__

# __find_asset:
# Find settlement asset with name tDAI
found_asset_id = None
assets = response.json()["assets"]["edges"]
for asset in assets:
    if asset["node"]["details"]["symbol"] == "tDAI":
        print("Found an asset with symbol tDAI")
        print(json.dumps(asset["node"], indent=2, sort_keys=True))
        found_asset_id = asset["node"]["id"]
        break
# :find_asset__

if found_asset_id is None:
    print(
        "tDAI asset not found on specified Vega network, please propose and "
        "create this asset first"
    )
    exit(1)

###############################################################################
#                 G O V E R N A N C E   T O K E N   C H E C K                 #
###############################################################################

# Get the identifier of the governance asset on the Vega network
vote_asset_id = next((x["node"]["id"] for x in assets if x["node"]["details"]["symbol"] == "VEGA"), None)
if vote_asset_id is None:
    print("VEGA asset not found on specified Vega network, please symbol name check and try again")
    exit(1)

# Debugging
# print("Accounts:\n{}".format(
#    json.dumps(response.json(), indent=2, sort_keys=True)))

# Request governance stake/voting balance
url = f"{data_node_url_rest}/parties/{pubkey}/stake"
response = requests.get(url)
helpers.check_response(response)
voting_balance = response.json()["currentStakeAvailable"]
if voting_balance == 0:
    print(f"Please associate VEGA governance asset to public key {pubkey} and try again")
    exit(1)

print("Voting balance:")
print(voting_balance)

###############################################################################
#                        B L O C K C H A I N   T I M E                        #
###############################################################################

# __get_time:
# Request the current blockchain time, and convert to time in seconds
response = requests.get(f"{data_node_url_rest}/vega/time")
helpers.check_response(response)
blockchain_time = int(response.json()["timestamp"])
blockchain_time_seconds = int(blockchain_time / 1e9)  # Seconds precision
# :get_time__

assert blockchain_time > 0
assert blockchain_time_seconds > 0
print(f"Blockchain time: {blockchain_time} ({blockchain_time_seconds} seconds past epoch)")

###############################################################################
#                         P R O P O S E   M A R K E T                         #
###############################################################################

# Further documentation on creating markets:
# https://docs.vega.xyz/testnet/tutorials/proposals/new-market-proposal

# Hint: Governance tokens must be associated/staked to propose markets on Vega

# __propose_market:
# Compose a governance proposal for a new market
proposal_ref = f"{pubkey}-{helpers.generate_id(30)}"

# Set closing/enactment and validation timestamps to valid time offsets
# from the current Vega blockchain time
closing_time = blockchain_time_seconds + 80000
enactment_time = blockchain_time_seconds + 86500
validation_time = blockchain_time_seconds + 1

# A market description should be readable and is the human readable string
# for when a market is visible, this must be unique, etc
rationale_title = "New market required for tDAI April 2023 Futures"
rationale_desc = "Proposal to create a new futures market for tDAI terminating in April 2023"

# The proposal command below contains the configuration for a new market
new_market = {
    "proposalSubmission": {
        "reference": proposal_ref,
        "rationale": {
            "title": rationale_title,
            "description": rationale_desc,
        },
        "terms": {
            "closingTimestamp": closing_time,
            "enactmentTimestamp": enactment_time,
            "newMarket": {
                "changes": {
                    "decimalPlaces": 5,
                    "instrument": {
                        "name": "BTC/DAI (2023, tDAI) " + helpers.generate_id(10),
                        "code": "CRYPTO:BTCDAI/APR23",
                        "future": {
                            "dataSourceSpecForSettlementData": {
                                "external": {
                                    "oracle": {
                                        "signers": [
                                            {
                                                "pubKey": {
                                                    "key": "c77fe74b64b2c97723bac8c3f110e5c3d7fb78f6c6c8915a56cb962968fbcfa7"
                                                }
                                            }
                                        ],
                                        "filters": [
                                            {
                                                "key": {
                                                    "name": "price.BTCDAI.value",
                                                    "type": "TYPE_INTEGER"
                                                },
                                                "conditions": [
                                                    {
                                                        "operator": "OPERATOR_GREATER_THAN",
                                                        "value": "0"
                                                    },
                                                    {
                                                        "operator": "OPERATOR_LESS_THAN",
                                                        "value": "999999999"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                }
                            },
                            "dataSourceSpecForTradingTermination": {
                                "external": {
                                    "oracle": {
                                        "signers": [
                                            {
                                                "pubKey": {
                                                    "key": "c77fe74b64b2c97723bac8c3f110e5c3d7fb78f6c6c8915a56cb962968fbcfa7"
                                                }
                                            }
                                        ],
                                        "filters": [
                                            {
                                                "key": {
                                                    "name": "trading.terminated.BTCDAI",
                                                    "type": "TYPE_BOOLEAN"
                                                },
                                                "conditions": [
                                                    {
                                                        "operator": "OPERATOR_EQUALS",
                                                        "value": "true"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                }
                            },
                            "dataSourceSpecBinding": {
                                "settlementDataProperty": "price.BTCDAI.value",
                                "tradingTerminationProperty": "trading.terminated.BTCDAI"
                            },
                            "quoteName": "tDAI",
                            "settlementAsset": found_asset_id,
                            "settlementDataDecimals": 5,
                        }
                    },
                    "metadata": [
                        "base:BTC",
                        "quote:DAI",
                        "class:fx/crypto",
                        "sector:defi",
                    ],
                    "priceMonitoringParameters": {
                        "triggers": [
                            {
                                "horizon": 43200,
                                "probability": "0.9999999",
                                "auctionExtension": 300
                            }
                        ]
                    },
                    "liquidityMonitoringParameters": {
                        "targetStakeParameters": {
                            "timeWindow": 3600,
                            "scalingFactor": 10
                        },
                        "triggeringRatio": 0.5,
                        "auctionExtension": 1
                    },
                    "logNormal": {
                        "riskAversionParameter": 0.001,
                        "tau": 0.0001140771161,
                        "params": {
                            "mu": 0.0,
                            "r": 0.0,
                            "sigma": 1.5
                        }
                    }
                }
            }
        }
    },
    "pubKey": pubkey,
    "propagate": True
}
# :propose_market__

# __sign_tx_proposal:
# Sign the transaction with a proposal submission command
url = "http://localhost:1789/api/v2/requests"

payload1 = {
    "id": "1",
    "jsonrpc": "2.0",
    "method": "client.send_transaction",
    "params": {
        "publicKey": pubkey,
        "sendingMode": "TYPE_SYNC",
        "transaction": new_market
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
# :sign_tx_proposal__

print(json.dumps(response.json(), indent=4, sort_keys=True))
print()
print("Signed new market proposal and sent to Vega")

# Wait for proposal to be included in a block and to be accepted by Vega network
print("Waiting for blockchain...", end="", flush=True)
proposal_id = None

url = f"{data_node_url_rest}/governances?proposerPartyId={pubkey}&proposalReference={proposal_ref}"
response = requests.get(url)
while helpers.check_nested_response(response, "connection") is not True:
    time.sleep(0.5)
    print(".", end="", flush=True)
    response = requests.get(url)
    continue

found_proposal = helpers.get_nested_response(response, "connection")[0]["node"]["proposal"]
proposal_id = found_proposal["id"]
proposal_state = found_proposal["state"]

print(found_proposal)
if (proposal_state == 'STATE_REJECTED') or (
        proposal_state == 'STATE_DECLINED') or (
        proposal_state == 'STATE_FAILED'):
    print(f"Your proposal has been {proposal_state}!")
    print("Due to: " + found_proposal["reason"])
    exit()
else:
    print("Your proposal has been accepted by the network!")
    print(json.dumps(found_proposal, indent=4, sort_keys=True))

assert proposal_id

###############################################################################
#                         V O T E   O N   M A R K E T                         #
###############################################################################

# __vote_submission:
# Prepare a vote for the proposal
vote = {
    "voteSubmission": {
        "value": "VALUE_YES",  # Can be either VALUE_YES or VALUE_NO
        "proposalId": proposal_id,
    },
    "pubKey": pubkey,
    "propagate": True
}
# :vote_submission__

# __sign_tx_vote:
# Sign the vote command
url = "http://localhost:1789/api/v2/requests"

payload1 = {
    "id": "1",
    "jsonrpc": "2.0",
    "method": "client.send_transaction",
    "params": {
        "publicKey": pubkey,
        "sendingMode": "TYPE_SYNC",
        "transaction": vote
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
# :sign_tx_vote__

print(json.dumps(response.json(), indent=4, sort_keys=True))

print()
print("Signed vote on proposal and sent to Vega")

print("Waiting for voting on proposal to succeed or fail...", end="", flush=True)
while True:
    time.sleep(0.5)
    print(".", end="", flush=True)
    url = f"{data_node_url_rest}/governances?proposerPartyId={pubkey}&proposalReference={proposal_ref}"
    response = requests.get(url)

    found_proposal = helpers.get_nested_response(response, "connection")[0]["node"]["proposal"]
    proposal_id = found_proposal["id"]
    proposal_state = found_proposal["state"]

    if proposal_state == "STATE_OPEN":
        continue

    if proposal_state == "STATE_PASSED":
        print("proposal vote has succeeded, waiting for enactment")
        continue

    if proposal_state == "STATE_ENACTED":
        break

# Optional: wait for network parameter change to be enacted
if WAIT_FOR_MARKET_AFTER_VOTE is not True:
    exit(1)

###############################################################################
#                        W A I T   F O R   M A R K E T                        #
###############################################################################

# IMPORTANT: When voting for a proposal on Vega networks, typically a single
# YES vote from the proposer will not be enough to vote the proposal in.
# As described on docs.vega.xyz, a network parameter change will need community
# voting support to be passed and then enacted.

# __wait_for_market:
print("Waiting for new market to be enacted...", end="", flush=True)
while True:
    time.sleep(0.5)
    print(".", end="", flush=True)
    url = f"{data_node_url_rest}/markets"
    response = requests.get(url)
    if response.status_code != 200:
        continue

    for edge in response.json()["markets"]["edges"]:
        if edge["node"]["id"] == proposal_id:
            print()
            print(edge["node"])
            break
# :wait_for_market__
