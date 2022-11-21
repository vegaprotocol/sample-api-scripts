#!/usr/bin/python3

###############################################################################
#                       G E T   M A R K E T   D E P T H                       #
###############################################################################

#  How to get market depth information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is NOT supported on this endpoint.
#  ----------------------------------------------------------------------
#  The following path parameter is required:
#   marketId:      Vega market id
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   maxDepth:      Maximum number of levels to return
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# Load Vega market id
market_id = helpers.env_market_id()
assert market_id != ""

# __get_market_depth:
# Request market depth for a specific market using a pre-defined market id
url = f"{data_node_url_rest}/market/depth/{market_id}/latest?maxDepth=50"
response = requests.get(url)
helpers.check_response(response)
print("Market depth for market:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_market_depth__
