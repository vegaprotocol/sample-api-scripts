#!/usr/bin/python3

###############################################################################
#                 E S T I M A T E   F E E S   &   M A R G I N                 #
###############################################################################

#  How to get Vega account information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   filter.partyIds:      Vega party ids (public keys)
#   filter.marketIds:     Vega market ids
#   filter.assets:        Specific assets e.g. tDAI, tBTC, etc
#   filter.accountTypes:  Account types e.g. infrastructure, general, etc
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Vega wallet interaction helper, see login.py for detail
from login import pubkey

# Load Vega data node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

#####################################################################################
#                           F E E   E S T I M A T I O N                             #
#####################################################################################

market_id = helpers.env_market_id()
assert market_id != ""

# __get_fees_estimate:
# Request to estimate trading fees on a Vega network
order_price = "100000"
order_size = "100"
url = f"{data_node_url_rest}/estimate/fee?marketId={market_id}&price={order_price}&size={order_size}"
response = requests.get(url)
helpers.check_response(response)
estimatedFees = response.json()
print("Estimated fee for order:\n{}".format(
    json.dumps(estimatedFees, indent=2, sort_keys=True)))
# :get_fees_estimate__

#####################################################################################
#                         M A R G I N   E S T I M A T I O N                         #
#####################################################################################

# __get_margins_estimate:
# Request to estimate trading margin on a Vega network
order_price = "600000"
order_size = "10"
order_side = "SIDE_BUY"
order_type = "TYPE_LIMIT"

url = f"{data_node_url_rest}/estimate/margin?marketId={market_id}&partyId={pubkey}" \
      f"&price={order_price}&size={order_size}&side={order_side}&type={order_type}"
response = requests.get(url)
helpers.check_response(response)
estimatedMargin = response.json()
print("Estimated margin for order:\n{}".format(
    json.dumps(estimatedMargin, indent=2, sort_keys=True)))
# :get_margins_estimate__
