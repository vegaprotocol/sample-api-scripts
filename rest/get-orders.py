#!/usr/bin/python3

###############################################################################
#                             G E T   O R D E R S                             #
###############################################################################

#  How to get order information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  Date Range is supported
#   -> Check out date-range.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   partyId:    Vega party id (public key)
#   marketId:   Vega market id
#   reference:  Custom order reference (set by the creator)
#   liveOnly:   Set to True to return only live orders (not filled etc)
#               See below for toggle True/False
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# Set to True to return only orders that are currently live on the market
# for example, not filled, expired or cancelled
# Set to False to return all orders of all status
live_only = True

###############################################################################
#                        O R D E R S   B Y   M A R K E T                      #
###############################################################################

market_id = helpers.env_market_id()
assert market_id != ""

# __get_orders_by_market:
# Request a list of orders for a market
url = f"{data_node_url_rest}/orders?marketId={market_id}&liveOnly={live_only}"
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Orders filtered by market:\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_orders_by_market__

# Find the first order in the list (above) if it exists
order_id = "6a834328d835ca79880dfc238a989c238fe32a62562690d717ab1ff42ad5004d"
if helpers.check_nested_response(response, "orders"):
    first_order = helpers.get_nested_response(response, "orders")[0]["node"]
    order_id = first_order["id"]

###############################################################################
#                        O R D E R S   B Y   P A R T Y                        #
###############################################################################

party_id = helpers.env_party_id()
assert party_id != ""

# __get_orders_by_party:
# Request a list of accounts for a party (pubkey) on a Vega network
url = f"{data_node_url_rest}/orders?partyId={party_id}&liveOnly={live_only}"
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Orders filtered by party:\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_orders_by_party__

###############################################################################
#                     O R D E R S   B Y   R E F E R E N C E                   #
###############################################################################

# __get_orders_by_ref:
custom_ref = "traderbot"
# Request a list of orders with a matching custom reference string
url = f"{data_node_url_rest}/orders?partyId={party_id}&reference={custom_ref}&liveOnly={live_only}"
response = requests.get(url)
helpers.check_response(response)
print("Orders filtered by reference:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_orders_by_ref__

###############################################################################
#                            O R D E R   B Y   I D                            #
###############################################################################

# Hint: Requesting an order by ID is a different REST route to listing orders
# and therefore it does not have filters or pagination (unlike the above requests)

# __get_order:
# Request specific order information for an order id
url = f"{data_node_url_rest}/order/{order_id}"
response = requests.get(url)
helpers.check_response(response)
print("Order:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_order__


###############################################################################
#                          O R D E R   H I S T O R Y                          #
###############################################################################

# Hint: This request lists all (if any) revisions to an order in order history
#       and not just the current version of the order

# __get_order_history:
# Request order revision history for an order id
url = f"{data_node_url_rest}/order/versions/{order_id}"
response = requests.get(url)
helpers.check_response(response)
print("Order:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_order_history__

