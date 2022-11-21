#!/usr/bin/python3

###############################################################################
#                      G E T   M A R G I N   L E V E L S                      #
###############################################################################

#  How to get margin level information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   partyId:       Vega party id (public key)
#   marketId:      Vega market id
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")
market_id = helpers.env_market_id()
party_id = helpers.env_party_id()

###############################################################################
#                   L I S T   M A R G I N   L E V E L S                       #
###############################################################################

# __get_margin_levels:
# Request all margin level data for a Vega network
url = f"{data_node_url_rest}/margin/levels"
response = requests.get(url)
helpers.check_response(response)
print("Margin level data for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_margin_levels__

# Find the first party and market id in the list (above) if they exists
# Hint: Comment out following 4 lines to always use env party/market id values
if helpers.check_nested_response(response, "marginLevels"):
    first_level = helpers.get_nested_response(response, "marginLevels")[0]["node"]
    party_id = first_level["partyId"]
    market_id = first_level["marketId"]

###############################################################################
#                 M A R G I N   L E V E L S   B Y   P A R T Y                 #
###############################################################################

# __get_margin_levels_by_party:
# Request margin level data for a specific party id (pubkey)
url = f"{data_node_url_rest}/margin/levels?partyId={party_id}"
response = requests.get(url)
helpers.check_response(response)
print("Margin level data for party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_margin_levels_by_party__

###############################################################################
#                M A R G I N   L E V E L S   B Y   M A R K E T                #
###############################################################################

# __get_margin_levels_by_market:
# Request margin level data for a specific market id
url = f"{data_node_url_rest}/margin/levels?marketId={market_id}"
response = requests.get(url)
helpers.check_response(response)
print("Margin level data for market:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_margin_levels_by_market__

###############################################################################
#        M A R G I N   L E V E L S   B Y   M A R K E T   &   P A R T Y        #
###############################################################################

# __get_margin_levels_by_market_and_party:
# Request margin level data for a specific market and party id
url = f"{data_node_url_rest}/margin/levels?marketId={market_id}&partyId={party_id}"
response = requests.get(url)
helpers.check_response(response)
print("Margin level data for market and party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_margin_levels_by_market_and_party__
