#!/usr/bin/python3

###############################################################################
#               G E T   G O V E R N A N C E   P R O P O S A L S               #
###############################################################################

#  How to get proposals information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   proposalState:      Proposal state e.g. STATE_OPEN
#   proposalType:       Proposal type e.g. TYPE_NEW_MARKET
#   proposerPartyId:    Party id (public key) of a proposer
#   proposalReference:  Custom proposal reference (set by the proposer)
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                         L I S T   P R O P O S A L S                         #
###############################################################################

# __get_proposals:
# Request proposal data for a Vega network
url = f"{data_node_url_rest}/governances"
response = requests.get(url)
helpers.check_response(response)
print("Governance (proposals) data for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_proposals__

# Find the first delegation in the list (above)
first_proposal = response.json()["connection"]["edges"][0]["node"]["proposal"]
proposal_id = first_proposal["id"]

###############################################################################
#                         P R O P O S A L   B Y   I D                         #
###############################################################################

print(f"Governance proposal for id: {proposal_id}")

# __get_proposal_by_id:
# Request proposal data for a specific proposal id
url = f"{data_node_url_rest}/governance?proposalId={proposal_id}"
response = requests.get(url)
helpers.check_response(response)
print("Proposal:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_proposal_by_id__
