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

# __get_trades_for_order:
# Request a list of trades for a specific order on a Vega network
orderID = "V0000929211-0046318720"
trades_by_order_request = vac.api.trading.TradesByOrderRequest(
    # Note: orderID has capitalised ID in TradesByOrderRequest
    orderID=orderID
)
trades_response = data_client.TradesByOrder(trades_by_order_request)
print("TradesByOrderID:\n{}".format(trades_response))
# :get_trades_for_order__
