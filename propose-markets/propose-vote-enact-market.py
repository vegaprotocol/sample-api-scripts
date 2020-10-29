#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (REST)
- Vega wallet (REST)

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

import json
import requests
import time
import os
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
#                               F I N D   A S S E T                                 #
#####################################################################################

# __get_assets:
# Request a list of assets available on a Vega network
url = "{base}/assets".format(base=node_url_rest)
response = requests.get(url)
helpers.check_response(response)
# :get_assets__

# Debugging
# print("Assets:\n{}".format(
#    json.dumps(response.json(), indent=2, sort_keys=True)))

# __find_asset:
# Find asset with name DAI
found_asset_id = "UNKNOWN"
assets = response.json()["assets"]
for asset in assets:
    if asset["name"] == "DAI":
        print("Found an asset with name DAI")
        print(asset)
        found_asset_id = asset["ID"]
        break
# __find_asset:

if found_asset_id == "UNKNOWN":
    print("DAI asset not found on specified Vega network, please propose and create this asset first")
    exit(1)

#####################################################################################
#                          B L O C K C H A I N   T I M E                            #
#####################################################################################

# __get_time:
# Request the current blockchain time, and convert to time in seconds
response = requests.get(f"{node_url_rest}/time")
helpers.check_response(response)
blockchain_time = int(response.json()["timestamp"])
blockchain_time_seconds = int(blockchain_time / 1e9)  # Seconds precision
# :get_time__

assert blockchain_time > 0
assert blockchain_time_seconds > 0
print(f"Blockchain time: {blockchain_time} ({blockchain_time_seconds} seconds past epoch)")

#####################################################################################
#                           P R O P O S E   M A R K E T                             #
#####################################################################################

# STEP 1 - Propose a BTC/DAI futures market

# __prepare_propose_market:
# Prepare a market proposal for a new market
market = {
    "partyID": pubkey,
    "proposal": {
        # Set validation timestamp to current time on Vega + 1 second
        "validationTimestamp": blockchain_time_seconds + 1,
        # Set closing timestamp to current time on Vega + 15 second
        "closingTimestamp": blockchain_time_seconds + 15,
        # Set enactment timestamp to current time on Vega + 20 second
        "enactmentTimestamp": blockchain_time_seconds + 20,
        # Note: timestamps must be in seconds precision
        "newMarket": {
            "changes": {
                "continuous": {"tickSize": "0.01"},
                "decimalPlaces": "5",
                "instrument": {
                    "baseName": "BTC",
                    "code": "CRYPTO:BTCDAI/DEC20",
                    "future": {
                        # Settlement asset identifier (found above)
                        "asset": found_asset_id,
                        "maturity": "2020-12-31T22:59:59Z",
                        # "settlementPriceSource: {
                        #     "sourceType": "signedMessage",
                        #     "sourcePubkeys": ["YOUR_PUBKEY_HERE"],
                        #     "field": "price",
                        #     "dataType": "decimal",
                        #     "filters": [
                        #         { "field": "feed_id", "equals": "BTCUSD/EOD" },
                        #         { "field": "mark_time", "equals": "31/12/20" }
                        #     ]
                        # }
                    },
                    "name": "BTC/DAI",
                    "quoteName": "DAI",
                },
                "logNormal": {
                    "params": {"mu": 0, "r": 0.016, "sigma": 0.05},
                    "riskAversionParameter": 0.01,
                    "tau": 1.90128526884173e-06,
                },
                "metadata": [],
                # Set opening auction duration (in seconds)
                "openingAuctionDuration": "120",
                "simple": {"factorLong": 0, "factorShort": 0},
            }
        },
    }
}

url = f"{node_url_rest}/governance/prepare/proposal"
response = requests.post(url, json=market)
helpers.check_response(response)
prepared_proposal = response.json()
# :prepare_propose_market__

proposal_ref = prepared_proposal["pendingProposal"]["reference"]
print(f"Prepared proposal, ref: {proposal_ref}")
assert proposal_ref != ""

# __sign_tx_proposal:
# Sign the prepared proposal transaction
# Note: Setting propagate to true will also submit to a Vega node
blob = prepared_proposal["blob"]
req = {"tx": blob, "pubKey": pubkey, "propagate": True}
url = f"{wallet_server_url}/api/v1/messages"
response = requests.post(url, headers=headers, json=req)
helpers.check_response(response)
# :sign_tx_proposal__

print("Signed market proposal and sent to Vega")

# Debugging
# print("Signed transaction:\n", response.json(), "\n")

# Wait for proposal to be included in a block and to be accepted by Vega network
print("Waiting for blockchain...", end="", flush=True)
proposal_id = ""
done = False
while not done:
    time.sleep(0.5)
    print(".", end="", flush=True)
    my_proposals = requests.get(node_url_rest + "/parties/" + pubkey + "/proposals")
    if my_proposals.status_code != 200:
        continue

    for n in my_proposals.json()["data"]:
        if n["proposal"]["reference"] == proposal_ref:
            proposal_id = n["proposal"]["ID"]
            print()
            print("Your proposal has been accepted by the network")
            print(n)
            done = True
            break


assert proposal_id != ""

#####################################################################################
#                             V O T E   O N   M A R K E T                           #
#####################################################################################

# STEP 2 - Let's vote on the proposal

# __prepare_vote:
# Prepare a vote for the market proposal
vote = {
    "vote": {
        "partyID": pubkey,
        "value": "VALUE_YES",           # Can be either VALUE_YES or VALUE_NO
        "proposalID": proposal_id,
        "timestamp": blockchain_time_seconds,
    }
}

url = f"{node_url_rest}/governance/prepare/vote"
response = requests.post(url, json=vote)
helpers.check_response(response)
prepared_vote = response.json()
# :prepare_vote__

# Debugging
# print("Prepared vote:\n", prepared_vote, "\n")

# __sign_tx_vote:
# Sign the prepared vote transaction
# Note: Setting propagate to true will also submit to a Vega node
blob = prepared_vote["blob"]
req = {"tx": blob, "pubKey": pubkey, "propagate": True}
url = f"{wallet_server_url}/api/v1/messages"
response = requests.post(url, headers=headers, json=req)
helpers.check_response(response)
# :sign_tx_vote__

print("Signed vote on proposal and sent to Vega")

# Debugging
# print("Signed transaction:\n", response.json(), "\n")

print("Waiting for vote on proposal to succeed or fail...", end="", flush=True)
done = False
while not done:
    time.sleep(0.5)
    my_proposals = requests.get(node_url_rest + "/parties/" + pubkey + "/proposals")
    if my_proposals.status_code != 200:
        continue

    for n in my_proposals.json()["data"]:
        if n["proposal"]["reference"] == proposal_ref:
            if n["proposal"]["state"] != "STATE_OPEN":
                print(n["proposal"]["state"])
                if n["proposal"]["state"] == "STATE_ENACTED":
                    done = True
                    break
                elif n["proposal"]["state"] == "STATE_PASSED":
                    print("proposal vote has succeeded, waiting for enactment")
                else:
                    print(n)
                    exit(1)

#####################################################################################
#                           W A I T   F O R   M A R K E T                           #
#####################################################################################

# STEP 3 - Wait for market to be enacted

print("Waiting for proposal to be enacted or failed...", end="", flush=True)
done = False
while not done:
    time.sleep(0.5)
    print(".", end="", flush=True)
    markets = requests.get(node_url_rest + "/markets")
    if markets.status_code != 200:
        continue

    for n in markets.json()["markets"]:
        if n["id"] == proposal_id:
            print()
            print(n)
            done = True
            break

# Completed.
