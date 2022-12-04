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

# Set to True to optionally wait/block until the new parameter change is confirmed
WAIT_FOR_PARAMETER_AFTER_VOTE = False

#####################################################################################
#                              F I N D   A S S E T S                                #
#####################################################################################

# __get_assets:
# Request a list of assets available
url = f"{data_node_url_rest}/assets"
response = requests.get(url)
helpers.check_response(response)
# :get_assets__

#####################################################################################
#                   G O V E R N A N C E   T O K E N   C H E C K                     #
#####################################################################################

# Get the identifier of the governance asset on the Vega network
assets = response.json()["assets"]["edges"]
vote_asset_id = next((x["node"]["id"] for x in assets if x["node"]["details"]["symbol"] == "VEGA"), None)
if vote_asset_id is None:
    print("VEGA asset not found on specified Vega network, please symbol name check and try again")
    exit(1)

# Request accounts for party and check governance asset balance
url = f"{data_node_url_rest}/accounts?filter.partyIds={pubkey}"
response = requests.get(url)
helpers.check_response(response)

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

#####################################################################################
#                          B L O C K C H A I N   T I M E                            #
#####################################################################################

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

#####################################################################################
#          P R O P O S E   N E T W O R K   P A R A M E T E R   U P D A T E          #
#####################################################################################

# Set the following network parameter key and value to the pair you are looking
# to change via network parameter update proposal:

rationale_title = "Update governance.proposal.asset.minEnact"
rationale_desc = "Proposal to update governance.proposal.asset.minEnact to 2 minutes"
parameter = "governance.proposal.asset.minEnact"
value = "2m0s"

# Hint: for a full list of available network params see get-network-parameters.py

# __propose_update_network_parameter:
# Compose a governance proposal for updating a network parameter with your custom reference
proposal_ref = f"{pubkey}-{helpers.generate_id(30)}"

# Set closing/enactment and validation timestamps to valid time offsets
# from the current Vega blockchain time
closing_time = blockchain_time_seconds + 172800
enactment_time = blockchain_time_seconds + 172900

submission = {
    "proposalSubmission": {
        "reference": proposal_ref,
        "rationale": {
            "title": rationale_title,
            "description": rationale_desc
        },
        "terms": {
            "closingTimestamp": closing_time,
            "enactmentTimestamp": enactment_time,
            "updateNetworkParameter": {
                "changes": {
                    "key": parameter,
                    "value": value,
                }
            },
        }
    },
    "pubKey": pubkey,
    "propagate": True
}
# :propose_update_network_parameter__

print("Network params update proposal: ", json.dumps(submission, indent=2, sort_keys=True))
print()

# __sign_tx_proposal:
# Sign the transaction with a proposal submission command
# Hint: Setting propagate to true will also submit to a Vega node
url = f"{wallet_server_url}/api/v1/command/sync"
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(url, headers=headers, json=submission)
helpers.check_response(response)
# :sign_tx_proposal__

print(json.dumps(response.json(), indent=4, sort_keys=True))

print()
print("Signed network parameters proposal and sent to Vega")

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

print()
if (proposal_state == 'STATE_REJECTED') or (
        proposal_state == 'STATE_DECLINED') or (
        proposal_state == 'STATE_FAILED'):
    print(f"Your proposal has been {proposal_state}!")
    print("Due to: " + found_proposal["reason"])
    if (found_proposal["errorDetails"]) != '':
        print("Further details: " + found_proposal["errorDetails"])
    exit()
else:
    print("Your proposal has been accepted by the network!")
    print(json.dumps(found_proposal, indent=4, sort_keys=True))

assert proposal_id

#####################################################################################
#                         V O T E   O N   P A R A M E T E R                         #
#####################################################################################

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
# Hint: Setting propagate to true will also submit to a Vega node
url = f"{wallet_server_url}/api/v1/command/sync"
response = requests.post(url, headers=headers, json=vote)
helpers.check_response(response)
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

# Optional: wait for network parameter change to be visible on network
if WAIT_FOR_PARAMETER_AFTER_VOTE is not True:
    exit(1)

###############################################################################
#                     W A I T   F O R   P A R A M E T E R                     #
###############################################################################

# IMPORTANT: When voting for a proposal on Vega networks, typically a single
# YES vote from the proposer will not be enough to vote the proposal in.
# As described on docs.vega.xyz, a network parameter change will need community
# voting support to be passed and then enacted.

# __wait_for_param:
print("Waiting for network parameter update to be completed...", end="", flush=True)
while True:
    time.sleep(0.5)
    print(".", end="", flush=True)
    url = f"{data_node_url_rest}/network/parameters"
    response = requests.get(url)
    if response.status_code != 200:
        continue

    for edge in response.json()["networkParameters"]["edges"]:
        if edge["node"]["key"] == parameter and edge["node"]["value"] == value:
            print()
            print(edge["node"])
            break
# :wait_for_param__
