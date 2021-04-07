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

import requests
import time
import os
import helpers

node_url_rest = os.getenv("NODE_URL_REST")
if not helpers.check_url(node_url_rest):
    print("Error: Invalid or missing NODE_URL_REST environment variable.")
    exit(1)

wallet_server_url = os.getenv("WALLETSERVER_URL")

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
#                              F I N D   A S S E T S                                #
#####################################################################################

# __get_assets:
# Request a list of assets available on a Vega network
url = f"{node_url_rest}/assets"
response = requests.get(url)
helpers.check_response(response)
# :get_assets__

# Debugging
# print("Assets:\n{}".format(
#    json.dumps(response.json(), indent=2, sort_keys=True)))

# __find_asset:
# Find settlement asset with name tDAI
found_asset_id = "UNKNOWN"
print(response)
assets = response.json()["assets"]

#####################################################################################
#                   G O V E R N A N C E   T O K E N   C H E C K                     #
#####################################################################################

# Get the identifier of the governance asset on the Vega network
vote_asset_id = "UNKNOWN"
for asset in assets:
    if asset["symbol"] == "tVOTE":
        vote_asset_id = asset["id"]
        break

if vote_asset_id == "UNKNOWN":
    print("tVOTE asset not found on specified Vega network, please symbol name check and try again")
    exit(1)

# Request accounts for party and check governance asset balance
url = f"{node_url_rest}/parties/{pubkey}/accounts"
response = requests.get(url)
helpers.check_response(response)

# Debugging
# print("Accounts:\n{}".format(
#    json.dumps(response.json(), indent=2, sort_keys=True)))

voting_balance = 0
accounts = response.json()["accounts"]
for account in accounts:
    if account["asset"] == vote_asset_id:
        print("Found governance asset account")
        print(account)
        voting_balance = account["balance"]
        break

if voting_balance == 0:
    print(f"Please deposit tVOTE asset to public key {pubkey} and try again")
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
#                           UPDATE NETWORK PARAMETER                                #
#####################################################################################

# Step 1 propose a network paramtere update

parameter = "market.liquidity.targetstake.triggering.ratio"
value = "0.7"

# __prepare_propose_updateNetworkParameter:
# Prepare a proposal for a network parameter update
market = {
    "partyId": pubkey,
    "proposal": {
        # Set validation timestamp to a valid time offset from the current Vega blockchain time
        "validationTimestamp": blockchain_time_seconds + 1,
        # Set closing timestamp to a valid time offset from the current Vega blockchain time
        "closingTimestamp": blockchain_time_seconds + 3600 + 60,
        # Set enactment timestamp to a valid time offset from the current Vega blockchain time
        "enactmentTimestamp": blockchain_time_seconds + 3600 + 120,
        # Note: the timestamps above are specified in seconds, and must meet minimums required by network
        # This is the main part: "key" is any network parameter and "value" is its value
        # As an example we vote to chage the parameter market.liquidity.targetstake.triggering.ratio.
        "updateNetworkParameter": {
            "changes": {
                "key": "market.liquidity.targetstake.triggering.ratio",
                "value": "0.7",
            }
        },
    },
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
url = f"{wallet_server_url}/api/v1/messages/sync"
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
            proposal_id = n["proposal"]["id"]
            print()
            print("Your proposal has been accepted by the network")
            print(n)
            done = True
            break

assert proposal_id != ""

#####################################################################################
#                            V O T E   O N   P A R A M T E R                        #
#####################################################################################

# STEP 2 - Let's vote on the market proposal

# IMPORTANT: When voting for a proposal on the Vega Testnet, typically a single
# YES vote from the proposer will not be enough to vote the market into existence.
# This is because of the network minimum threshold for voting on proposals, this
# threshold for market proposals this is currently a 66% majority vote either YES or NO.
# A proposer should enlist the help/YES votes from other community members, ideally on the
# Community forums (https://community.vega.xyz/c/testnet) or Discord (https://vega.xyz/discord)

# Further documentation on proposal voting and review here: https://docs.testnet.vega.xyz/docs/api-howtos/proposals/

# __prepare_vote:
# Prepare a vote for the proposal
vote = {
    "vote": {
        "partyId": pubkey,
        "value": "VALUE_YES",  # Can be either VALUE_YES or VALUE_NO
        "proposalId": proposal_id,
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
url = f"{wallet_server_url}/api/v1/messages/sync"
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
