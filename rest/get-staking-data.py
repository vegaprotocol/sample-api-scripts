#!/usr/bin/python3

###############################################################################
#                       G E T   S T A K I N G   D A T A                       #
###############################################################################

#  How to get staking data information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The following path parameter is required:
#   partyId:       Vega party id (public key)
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                      L I S T   S T A K I N G   D A T A                      #
###############################################################################

party_id = helpers.env_party_id()
assert party_id != ""

# __get_staking_data:
# Request all staking data for a Vega network
url = f"{data_node_url_rest}/parties/{party_id}/stake"
response = requests.get(url)
helpers.check_response(response)
print("Staking data for party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_staking_data__
