#!/usr/bin/python3

###############################################################################
#                          G E T   P O S I T I O N S                          #
###############################################################################

#  How to get rewards information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   partyId:   Vega party id (public key)
#   marketId:  Vega market id
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# Load Vega market and party ids
party_id = helpers.env_party_id()
market_id = helpers.env_market_id()
assert party_id != ""
assert market_id != ""

###############################################################################
#                          L I S T   P O S I T I O N S                        #
###############################################################################

# __get_positions:
# Request a list of trading positions for a Vega network
url = f"{data_node_url_rest}/positions?partyId={party_id}&marketId={market_id}"
response = requests.get(url)
helpers.check_response(response)
print("Positions for party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_positions__
