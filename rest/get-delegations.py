#!/usr/bin/python3

###############################################################################
#                        G E T   D E L E G A T I O N S                        #
###############################################################################

#  How to get delegation (staking) information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   partyId:  Vega party id (public key)
#   nodeId:   Vega node id
#   epochId:  Vega epoch id
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                       L I S T   D E L E G A T I O N S                       #
###############################################################################

# __get_delegations:
# Request a list of all delegations for a Vega network
url = f"{data_node_url_rest}/delegations"
response = requests.get(url)
helpers.check_response(response)
print("Delegations for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_delegations__

# Find the first delegation in the list (above) and set epochId / nodeId vars
first_delegation = helpers.get_nested_response(response, "delegations")[0]
nodeId = first_delegation["node"]["nodeId"]
epochId = first_delegation["node"]["epochSeq"]
partyId = first_delegation["node"]["party"]

# Tip: You can combine the filters epochId, partyId, and nodeId to refine the
# returned delegation data, for instance, all delegations for party to a node
# Each filter is shown below, but they can be combined as described...

###############################################################################
#                   D E L E G A T I O N S   B Y   P A R T Y                   #
###############################################################################

# __get_delegations_by_party:
# Request a list of all delegations for a party (pubkey)
url = f"{data_node_url_rest}/delegations?partyId={partyId}"
response = requests.get(url)
helpers.check_response(response)
print("Delegations filtered by party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_delegations_by_party__

###############################################################################
#                   D E L E G A T I O N S   B Y   E P O C H                   #
###############################################################################

# __get_delegations_by_epoch:
# Request a list of all delegations for a specific epoch number
url = f"{data_node_url_rest}/delegations?epochId={epochId}"
response = requests.get(url)
helpers.check_response(response)
print("Delegations filtered by epoch:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_delegations_by_epoch__

###############################################################################
#                    D E L E G A T I O N S   B Y   N O D E                    #
###############################################################################

# __get_delegations_by_epoch:
# Request a list of all delegations for a specific Vega node
url = f"{data_node_url_rest}/delegations?nodeId={nodeId}"
response = requests.get(url)
helpers.check_response(response)
print("Delegations filtered by Vega node:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_delegations_by_epoch__
