#!/usr/bin/python3

###############################################################################
#                        G E T   M A R K E T   D A T A                        #
###############################################################################

#  How to get market data from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  Date Range is supported
#   -> Check out date-range.py for example usage
#  ----------------------------------------------------------------------
#  The following path parameter is required when getting latest data and
#  historic data, it is not required for listing market data for all markets:
#   marketId:      Vega market id
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

###############################################################################
#                    M A R K E T   D A T A   H I S T O R Y                    #
###############################################################################

# __get_market_data:
# Calculate the time window for the history period to return e.g. last 24 hours
time_now = helpers.ts_now()
fromTime = helpers.get_nano_ts(time_now, 24*60*60)  # 1 day ago
toTime = helpers.get_nano_ts(time_now, 0)  # to now

# Request market data history for a specific market using a market id
# Important! The startTimestamp and endTimestamp are REQUIRED fields
url = f"{data_node_url_rest}/market/data/{market_id}?startTimestamp={fromTime}&endTimestamp={toTime}"
print(url)
response = requests.get(url)
helpers.check_response(response)
print("Market data:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_market_data__

###############################################################################
#                     L A T E S T   M A R K E T   D A T A                     #
###############################################################################

# __get_latest_market_data:
# Request market data for a specific market using a market id
url = f"{data_node_url_rest}/market/data/{market_id}/latest"
response = requests.get(url)
helpers.check_response(response)
print("Market data for market:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_latest_market_data__

###############################################################################
#                            M A R K E T S   D A T A                          #
###############################################################################

# __get_markets_data:
# Request latest market data for ALL markets on a Vega network
url = f"{data_node_url_rest}/markets/data"
response = requests.get(url)
helpers.check_response(response)
print("Markets data:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_markets_data__

