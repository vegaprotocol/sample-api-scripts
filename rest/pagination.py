#!/usr/bin/python3

###############################################################################
#                            P A G I N A T I O N                              #
###############################################################################

#  Pagination is available and enabled by default on many of the Vega data node
#  APIs.
#
#  When querying for data the results will be 'paged' into sets of results
#  and the default page size is 1000 results (this figure can be overridden).
#
#  Vega APIs us a cursor based pagination model (aka key-set pagination). This
#  is a common pagination strategy that avoids many of the pitfalls of “offset–
#  limit” pagination. For example, with offset–limit pagination, if an item
#  from a prior page is deleted while the client is paginating, all subsequent
#  results will be shifted forward by one.
#
#  Each result returned from an API endpoint will have a 'cursor', example:
#
#     "edges": [
#       {
#         "cursor": "eyJ2ZWdhX3RpbWUiOiIyMDIyLTExLTExVDE0OjM2OjU4LjE2ODY2OVoifQ==",
#         "node": {
#            ...
#
#  And each result set page will have 'pageInfo', example:
#
#    "pageInfo": {
#       "endCursor": "eyJ2ZWdhX3RpbWUiOiIyMDIyLTExLTExVDE0OjI2OjQzLjg2MTIxWiJ9",
#       "hasNextPage": false,
#       "hasPreviousPage": false,
#       "startCursor": "eyJ2ZWdhX3RpbWUiOiIyMDIyLTExLTExVDE0OjM2OjU4LjE2ODY2OVoifQ=="
#     }
#
#  The examples shown below illustrate the basic concepts used with data returned
#  from most list endpoints in the Vega APIs, including (but not limited to):
#     -  Trades
#     -  Orders
#     -  Parties
#     -  Candles
#     -  Withdrawals
#     -  Deposits
#     -  Rewards
#     -  Ledger entries
#     -  Balance changes
#     -  Liquidity provisions
#     -  Governance
#     -  etc.
#
#  The following parameters are typically used to control pagination:
#    pagination.first:         Non-negative integer e.g. 100 (forward pagination)
#    pagination.after:         Cursor value                  (forward pagination)
#    pagination.last:          Non-negative integer e.g. 100 (backward pagination)
#    pagination.before:        Cursor value                  (backward pagination)
#    pagination.newestFirst:   Newest records first, older records last, default is true.
#                              >This effectively reverses the forward/backward direction above.
#
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                    A S C E N D I N G   P A G I N A T I O N                  #
###############################################################################

market_id = helpers.env_market_id()
assert market_id != ""

# __get_trades_by_market_basic_pagination_asc:
page_size = 50
# Request a list of the first trades for a market, limit page size to `50` results (default is 1000)
url = f"{data_node_url_rest}/trades?marketId={market_id}" \
      f"&pagination.first={page_size}"
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Trades filtered by market (first 50 asc):\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_trades_by_market_basic_pagination_asc__

# Find the trades list pageInfo from the query above and collect the page information:
pageInfo = response_json["trades"]["pageInfo"]
startCursor = pageInfo["startCursor"]          # The starting cursor string value
endCursor = pageInfo["endCursor"]              # The ending cursor string value
hasNextPage = pageInfo["hasNextPage"]          # True if has next page (based on page size)
hasPrevPage = pageInfo["hasPreviousPage"]      # True if has a previous page (based on page size)

# Hint: startCursor and endCursor correspond to the first and last nodes in edges, respectively.
# and the endCursor value from the initial page of results is used in the next request...

if not hasNextPage:
    print("Result set returned does not have a next page")
if not hasPrevPage:
    print("Result set returned does not have a previous page")

# __get_trades_by_market_basic_pagination_asc_next_page:
# Request a list of the next page of 50 trades for a market, after the page we returned previously
url = f"{data_node_url_rest}/trades?marketId={market_id}" \
      f"&pagination.first={page_size}" \
      f"&pagination.after={endCursor}" \

response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Trades filtered by market (next page, asc):\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_trades_by_market_basic_pagination_asc_next_page__

###############################################################################
#                  D E S C E N D I N G   P A G I N A T I O N                  #
###############################################################################

# __get_trades_by_market_basic_pagination_desc:
page_size = 25
# Request a list of the last trades for a market, limit page size to `25` results (default is 1000)
url = f"{data_node_url_rest}/trades?marketId={market_id}" \
      f"&pagination.last={page_size}"
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Trades filtered by market (last 25, desc):\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_trades_by_market_basic_pagination_desc__

# Find the trades list pageInfo from the query above and collect the page information:
pageInfo = response_json["trades"]["pageInfo"]
startCursor = pageInfo["startCursor"]          # The starting cursor string value
endCursor = pageInfo["endCursor"]              # The ending cursor string value
hasNextPage = pageInfo["hasNextPage"]          # True if has next page (based on page size)
hasPrevPage = pageInfo["hasPreviousPage"]      # True if has a previous page (based on page size)

if not hasNextPage:
    print("Result set returned does not have a next page")
if not hasPrevPage:
    print("Result set returned does not have a previous page")

# __get_trades_by_market_basic_pagination_desc_next_page:
# Request a list of the next page of 25 trades for a market, before the page we returned previously
url = f"{data_node_url_rest}/trades?marketId={market_id}" \
      f"&pagination.last={page_size}" \
      f"&pagination.before={endCursor}" \

response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Trades filtered by market (next page, desc):\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_trades_by_market_basic_pagination_desc_next_page__
