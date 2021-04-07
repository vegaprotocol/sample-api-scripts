#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (gRPC)

Apps/Libraries:
- REST: requests (https://pypi.org/project/requests/)
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

markets = data_client.Markets(vac.api.trading.MarketsRequest()).markets
market_id = markets[0].id
assert market_id != ""

# __get_orders_for_market:
# Request a list of orders by market on a Vega network
orders_by_market_request = vac.api.trading.OrdersByMarketRequest(
    market_id=market_id
)
orders_response = data_client.OrdersByMarket(orders_by_market_request)
print("OrdersByMarket:\n{}".format(orders_response))
# :get_orders_for_market__

# __get_trades_for_market:
# Request a list of trades by market on a Vega network
trades_by_market_request = vac.api.trading.TradesByMarketRequest(
    market_id=market_id
)
trades_response = data_client.TradesByMarket(trades_by_market_request)
print("TradesByMarket:\n{}".format(trades_response))
# :get_trades_for_market__
