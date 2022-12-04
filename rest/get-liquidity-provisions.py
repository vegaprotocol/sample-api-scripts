#!/usr/bin/python3

###############################################################################
#               G E T   L I Q U I D I T Y   P R O V I S I O N S               #
###############################################################################

#  How to get LP information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   partyId:    Vega party id (public key)
#   marketId:   Vega market id
#   reference:  A unique/custom reference
#      Note that with a reference, a marketId or partyId is also required
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")
market_id = helpers.env_market_id()

###############################################################################
#                          L P S   B Y   M A R K E T                          #
###############################################################################

# __get_lps_by_market:
# Request liquidity provisions for a market on a Vega network
url = f"{data_node_url_rest}/liquidity/provisions?marketId={market_id}"
response = requests.get(url)
helpers.check_response(response)
print("Liquidity Provisions for market:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_lps_by_market__

# Find the first delegation in the list (above)
first_lp = response.json()["liquidityProvisions"]["edges"][0]["node"]
party_id = first_lp["partyId"]
custom_ref = first_lp["reference"]

###############################################################################
#                          L P S   B Y   P A R T Y                            #
###############################################################################

# __get_lps_by_party:
# Request liquidity provisions for a party on a Vega network
url = f"{data_node_url_rest}/liquidity/provisions?partyId={party_id}"
response = requests.get(url)
helpers.check_response(response)
print("Liquidity Provisions for party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_lps_by_party__

###############################################################################
#                       L P S   B Y   R E F E R E N C E                       #
###############################################################################

# __get_lps_by_reference:
# Request liquidity provisions for a reference on a Vega network
#  Note: A partyId or marketId must be supplied with the reference field
url = f"{data_node_url_rest}/liquidity/provisions?marketId={market_id}&reference={custom_ref}"
response = requests.get(url)
helpers.check_response(response)
print("Liquidity Provisions for reference:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_lps_by_reference__
