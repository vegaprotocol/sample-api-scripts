#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (gRPC)

Apps/Libraries:
- gRPC (node): Vega-API-client (https://pypi.org/project/Vega-API-client/)
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
import signal
import sys

# __import_client:
import vegaapiclient as vac
# :import_client__

node_url_grpc = os.getenv("NODE_URL_GRPC")

def signal_handler(sig, frame):
    print('Exit requested.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# __create_client:
# Create a Vega gRPC data client
data_client = vac.VegaTradingDataClient(node_url_grpc)
# :create_client__

# __stream_orders_by_ref:
# Stream orders by reference on a Vega network
# Note: This is an example and order reference will be provided in the response
# from a prepareSubmitOrder request in the field named `submitID` or similar.
reference = "4617844f-6fab-4cf6-8852-e29dbd96e5f1"
pubkey = "94c21a5bfc212c0b4ee6e3593e8481559972ad31f1fb453491f255e72bdb6fdb"
subscribe_request = vac.api.trading.OrdersSubscribeRequest(party_id=pubkey)
for stream_resp in data_client.OrdersSubscribe(subscribe_request):
    for order in stream_resp.orders:
        # Check orders arriving over the channel/stream for reference
        if order.reference == reference:
            # Order with reference found
            print(order)
# :stream_orders_by_ref__
