#!/usr/bin/python3

###############################################################################
#                      D A T E / T I M E    R A N G E S                       #
###############################################################################

#  Querying results within a particular date/time range is available on
#  selected Vega data node APIs.
#
#  For example, a client may need to look at orders within a specific time
#  window or only find trades on a particular market from the last week.
#
#  The examples shown below illustrate the basic concepts used with data returned
#  from most list endpoints in the Vega APIs, including (but not limited to):
#     -  Trades
#     -  Orders
#     -  Parties
#     -  Candles   ( IMPORTANT: to/from candle time window is specified with to/fromTimestamp)
#     -  Withdrawals
#     -  Deposits
#     -  Ledger entries
#     -  Balance changes
#     -  Liquidity provisions
#     -  etc.
#
#  The following parameters are typically used to control pagination:
#    dateRange.startTimestamp:      Starting timestamp in nanoseconds past epoch
#    dateRange.endTimestamp:        Ending timestamp in nanoseconds past epoch
#
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers
import datetime

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# Load Vega market ID
market_id = helpers.env_market_id()
assert market_id != ""

###############################################################################
#                  T I M E S T A M P   G E N E R A T I O N                    #
###############################################################################

#  The majority of timestamps seen on Vega's APIs are of type RFC3339Nano, an
#  integer based representation of the number of nanoseconds that have passed
#  since Thursday 1 January 1970 00:00:00 UTC.
#
#  When generating timestamps for a time window to be used in API queries the
#  caller needs to pay particular attention to the conversion. In most modern
#  programming languages a Unix timestamp can be generated relatively easily.
#
#  The code example below shows how to convert a time to nanosecond timestamp
#  with a delta in seconds (subtract or add a number of seconds from time now):

seconds_delta = 60 * 60 * 2  # Minus two hours from date/time now
time_now = datetime.datetime.now()
new_dt = time_now - datetime.timedelta(seconds=seconds_delta)
ns_ts_from = str(int(new_dt.replace(tzinfo=datetime.timezone.utc).timestamp())*1000000000)
ns_ts_to = str(int(time_now.replace(tzinfo=datetime.timezone.utc).timestamp())*1000000000)

print(f"Current Time: {time_now}")
print(f"Offset Time: {new_dt}")
print(f"Current Timestamp: {ns_ts_to}")
print(f"Offset: {ns_ts_from}")

# Hint: In a decentralised system such as Vega we need to ideally use the time
# provided by Vega's blockchain. It is advised that the caller use vega time
# (see get-vega-time.py) for more information and examples.
#
# When using a date range, the result set will be paginated and the caller will
# need to page the results (see pagination.py)

###############################################################################
#                 T R A D E S   D A T E / T I M E   R A N G E                 #
###############################################################################

# __get_trades_by_market_trades_date_range:
# Request a list of trades for a market for the given date/time window
url = f"{data_node_url_rest}/trades?marketId={market_id}" \
      f"&dateRange.startTimestamp={ns_ts_from}" \
      f"&dateRange.endTimestamp={ns_ts_to}"
print(url)
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Trades filtered by market (date/time range):\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_trades_by_market_trades_date_range__
