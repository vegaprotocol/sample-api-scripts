#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (gRPC)

Apps/Libraries:
- Vega-API-client (https://pypi.org/project/Vega-API-client/)
"""

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__

import os

node_url_grpc = os.getenv("NODE_URL_GRPC")

# __import_client:
import vegaapiclient as vac
data_client = vac.VegaTradingDataClient(node_url_grpc)
# :import_client__

# __get_markets:
# Request a list of markets available on the specified Vega Network
markets = data_client.Markets(vac.api.trading.MarketsRequest()).markets
print("Markets:\n{}".format(markets))
# :get_markets__

market_id = markets[0].id
assert market_id != ""

# __get_market_data:
# Request the market data for a market on a Vega network
market_data_request = vac.api.trading.MarketDataByIDRequest(
    market_id=market_id
)
market_data = data_client.MarketDataByID(market_data_request)
print("MarketData:\n{}".format(market_data))
# :get_market_data__
