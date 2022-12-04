#!/usr/bin/python3

###############################################################################
#                            G E T   M A R K E T S                            #
###############################################################################

#  How to get market information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                           L I S T   M A R K E T S                           #
###############################################################################

# __get_markets:
# Request a list of markets on a Vega network
url = f"{data_node_url_rest}/markets"
print(url)
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Markets:\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_markets__

# Find the first market in the list (above) if it exists
market_id = "6a834328d835ca79880dfc238a989c238fe32a62562690d717ab1ff42ad5004d"
if helpers.check_nested_response(response, "markets"):
    first_market = helpers.get_nested_response(response, "markets")[0]["node"]
    market_id = first_market["id"]

###############################################################################
#                          M A R K E T   B Y   I D                            #
###############################################################################

# Hint: Requesting a market by ID is a different REST route to listing markets
# and therefore it does not have filters or pagination (unlike the above request)

# __get_market:
# Request a specific market using a pre-defined market id
url = f"{data_node_url_rest}/market/{market_id}"
response = requests.get(url)
helpers.check_response(response)
print("Market:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_market__
