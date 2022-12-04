#!/usr/bin/python3

###############################################################################
#                             G E T   T R A D E S                             #
###############################################################################

#  How to get trade information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  Date Range is supported
#   -> Check out date-range.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   partyId:    Vega party id (public key)
#   marketId:   Vega market id
#   orderId:    Vega order id
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Vega wallet interaction helper, see login.py for detail
from login import pubkey

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                        T R A D E S   B Y   M A R K E T                      #
###############################################################################

market_id = helpers.env_market_id()
assert market_id != ""

# __get_trades_by_market:
# Request a list of trades for a market
url = f"{data_node_url_rest}/trades?marketId={market_id}"
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Trades filtered by market:\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_trades_by_market__

# Find the first trade in the list (above) if it exists
trade_id = "6a834328d835ca79880dfc238a989c238fe32a62562690d717ab1ff42ad5004d"
order_id = "165968e2f7d488bc2d55b5da6a9137af207b839c3241352253ef1c2c253eb620"
if helpers.check_nested_response(response, "trades"):
    first_trade = helpers.get_nested_response(response, "trades")[0]["node"]
    trade_id = first_trade["id"]
    order_id = first_trade["buyOrder"]

###############################################################################
#                        T R A D E S   B Y   P A R T Y                        #
###############################################################################

# __get_trades_by_party:
# Request a list of trades for a party (pubkey) on a Vega network
url = f"{data_node_url_rest}/trades?partyId={pubkey}"
print(url)
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Trades filtered by party:\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_trades_by_party__

###############################################################################
#                      T R A D E S   B Y   O R D E R  I D                     #
###############################################################################

# __get_trades_by_order:
# Request a list of orders with a matching custom reference string
url = f"{data_node_url_rest}/trades?orderId={order_id}"
print(url)
response = requests.get(url)
helpers.check_response(response)
print("Trades by order:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_trades_by_order__

###############################################################################
#                            T R A D E   B Y   I D                            #
###############################################################################
# todo: uncomment below when work done to add trade by ID to v2 API

# Note: Requesting a trade by ID is a different REST route to listing trades
# and therefore it does not have filters or pagination (unlike the above requests)

# __get_trade_by_id:
# Request a specific trade using a pre-defined trade id
# url = f"{data_node_url_rest}/trade/{trade_id}"
# response = requests.get(url)
# helpers.check_response(response)
# print("Trade:\n{}".format(
#     json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_trade_by_id__

###############################################################################
#                           L A T E S T   T R A D E                           #
###############################################################################

# __get_latest_trade:
# Request the latest trade on a given Vega market
url = f"{data_node_url_rest}/market/{market_id}/trade/latest"
response = requests.get(url)
helpers.check_response(response)
print("Latest trade:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_latest_trade__

