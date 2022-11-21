#!/usr/bin/python3

###############################################################################
#                   G E T   G O V E R N A N C E   V O T E S                   #
###############################################################################

#  How to get votes information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list must be filtered by at least one of the following parameters:
#   partyId:      Vega party id (public key)
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                             L I S T   V O T E S                             #
###############################################################################

# Load Vega party id
party_id = helpers.env_party_id()
assert party_id != ""

# __get_votes:
# Request vote data for a Vega network
url = f"{data_node_url_rest}/votes?partyId={party_id}"
print(url)
response = requests.get(url)
helpers.check_response(response)
print("Governance (votes) data for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_votes__
