#!/usr/bin/python3

###############################################################################
#                       G E T   E P O C H S   D A T A                         #
###############################################################################

#  How to get epoch information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is NOT supported on this endpoint.
#  ----------------------------------------------------------------------
#  The list can be optionally filtered by:
#   id:    Vega epoch id (also referred to as the epochSeq field)
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                            L I S T   E P O C H S                            #
###############################################################################

# __get_epochs:
# Request all epoch data for a Vega network
url = f"{data_node_url_rest}/epoch"
response = requests.get(url)
helpers.check_response(response)
print("Epoch data for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_epochs__

# Find the first delegation in the list (above)
first_delegation = response.json()["epoch"]["delegations"][0]
epoch_id = first_delegation["epochSeq"]

###############################################################################
#                            E P O C H   B Y   I D                            #
###############################################################################

# __get_epochs_by_id:
# Request epoch data for a specific epoch id
url = f"{data_node_url_rest}/epoch?id={epoch_id}"
response = requests.get(url)
helpers.check_response(response)
print("Epoch data for epoch id:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_epochs_by_id__
