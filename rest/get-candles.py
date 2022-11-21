#!/usr/bin/python3

###############################################################################
#                           G E T   C A N D L E S                             #
###############################################################################

#  How to get Vega candle (ohlc) information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The specific candles are obtained using parameters:
#   candleId:      Vega candle id (contains interval) see List Candle Intervals
#  Date range is supported but by using the following required params:
#   fromTimestamp: Starting timestamp for candles in nanoseconds since the epoch
#   toTimestamp:   Ending timestamp for candles in nanoseconds since the epoch
#
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega data node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")
market_id = helpers.env_market_id()

###############################################################################
#                 L I S T   C A N D L E   I N T E R V A L S                   #
###############################################################################

# Hint: In order to get candles of a suitable bucket size e.g. 5 minutes and
# market id e.g. 13b081fe5bc8fd256b0a374dc04d94b904118312dd0d942e891a5f57ce0c556c
# you should use the list candle intervals API to get back a candle id:

# __get_candle_intervals:
# Request a list of candle intervals available for a market and select a candle id
url = f"{data_node_url_rest}/candle/intervals?marketId={market_id}"
response = requests.get(url)
helpers.check_response(response)
print("Candle intervals for market:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_candle_intervals__

# Find the first candle id in the list e.g. trades_candle_5_minutes_<market_id> etc
candle_id = response.json()["intervalToCandleId"][0]["candleId"]
assert candle_id != ""
print(f"Candle found: {candle_id}")

###############################################################################
#                     C A N D L E S   ( F I L T E R E D )                     #
###############################################################################

# Calculate the time window for the candles period to return e.g. last 24 hours
time_now = helpers.ts_now()
fromTime = helpers.get_nano_ts(time_now, 24*60*60)  # 1 day ago
toTime = helpers.get_nano_ts(time_now, 0)  # to now

# __get_candles_by_id:
# Request specific candles for a market using candle id (from above)
url = f"{data_node_url_rest}/candle?candleId={candle_id}" \
  f"&fromTimestamp={fromTime}" \
  f"&toTimestamp={toTime}"
print(url)
response = requests.get(url)
helpers.check_response(response)
print("Candles for id and ns timestamp window:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_candles_by_id__
