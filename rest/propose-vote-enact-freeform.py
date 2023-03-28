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
#                         F R E E F O R M   P R O P O S A L                         #
#####################################################################################

# __propose_new_freeform:
# Compose a freeform governance proposal
proposal_ref = f"{pubkey}-{helpers.generate_id(30)}"
# Title is designed to be a short/relatively unique title to help identify the freeform proposal
proposal_title = "An example freeform proposal relating to an IPFS document"
# Description can be a more longer form description of the proposal including links or guidance
proposal_description = "I propose that everyone evaluate the following IPFS document and vote " \
                        "Yes if they agree. [bafybeigwwctpv37xdcwacqxvekr6e4kaemqsrv34em6glkbic" \
                        "eo3fcy4si](https://dweb.link/ipfs/bafybeigwwctpv37xdcwacqxvekr6e4kaemq" \
                        "srv34em6glkbiceo3fcy4si)"


# Set closing/enactment and validation timestamps to valid time offsets
# from the current Vega blockchain time
closing_time = blockchain_time_seconds + 60 * 60 * 2  # Two hours from blockchain time

new_freeform = {
    "proposalSubmission": {
        "reference": proposal_ref,
        "rationale": {
            "description": proposal_description,
            "title": proposal_title
        },
        "terms": {
            "closingTimestamp": closing_time,
            "newFreeform": {},
        }
    },
    "pubKey": pubkey,
    "propagate": True
}
# :propose_new_freeform__

# __sign_tx_proposal:
# Sign the transaction with a proposal submission command
# Hint: Setting propagate to true will also submit to a Vega node
url = f"{wallet_server_url}/api/v2/requests"
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(url, headers=headers, json=new_freeform)
helpers.check_response(response)
# :sign_tx_proposal__

print(json.dumps(response.json(), indent=4, sort_keys=True))
print()
print("Signed freeform proposal and sent to Vega")

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
assert proposal_id != ""

#####################################################################################
#                         V O T E   O N   P A R A M E T E R                         #
#####################################################################################

# STEP 2 - Let's vote on the proposal

# IMPORTANT: When voting for a proposal on the Vega Testnet, typically a single
# YES vote from the proposer will not be enough to vote the proposal into existence.
# This is because of the network minimum threshold for voting on proposals.
# A proposer should enlist the help/YES votes from other community members, ideally on the
# Community forums (https://community.vega.xyz/c/testnet) or Discord (https://vega.xyz/discord)

# Further documentation on proposal voting and review here: https://docs.testnet.vega.xyz/docs/api-howtos/proposals/

# __prepare_vote:
# Prepare a vote for the proposal
vote = {
    "voteSubmission": {
        "value": "VALUE_YES",  # Can be either VALUE_YES or VALUE_NO
        "proposalId": proposal_id,
    },
    "pubKey": pubkey,
    "propagate": True
}
# :prepare_vote__

# Debugging
# print("Prepared vote:\n", prepared_vote, "\n")

# __sign_tx_vote:
# Sign the vote transaction
# Note: Setting propagate to true will also submit to a Vega node
url = f"{wallet_server_url}/api/v2/requests"
response = requests.post(url, headers=headers, json=vote)
helpers.check_response(response)
# :sign_tx_vote__

print("Signed vote on proposal and sent to Vega")

# Debugging
#   print("Signed transaction:\n", response.json(), "\n")

#####################################################################################
#                          V O T E   O N   F R E E F O R M                          #
#####################################################################################

# __vote_submission:
# Prepare a vote for the freeform proposal
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
url = f"{wallet_server_url}/api/v2/requests"
response = requests.post(url, headers=headers, json=vote)
helpers.check_response(response)
# :sign_tx_vote__

print(json.dumps(response.json(), indent=4, sort_keys=True))
print()
print("Signed vote on freeform proposal and sent to Vega")

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
