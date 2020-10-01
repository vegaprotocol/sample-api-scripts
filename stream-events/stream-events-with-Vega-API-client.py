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

node_url_grpc = os.getenv("NODE_URL_GRPC")

from google.protobuf.empty_pb2 import Empty
# __import_client:
import vegaapiclient as vac
data_client = vac.VegaTradingDataClient(node_url_grpc)
# :import_client__

def signal_handler(sig, frame):
    print('Exit requested.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# __get_market:
# Request the identifier for a market
markets = data_client.Markets(Empty()).markets
market_id = markets[0].id
# :get_market__

# __stream_events:
# Subscribe to the events bus stream for the marketID specified
# Required: type field - default ALL
# Optional: Market identifier - filter by market
#           Party identifier - filter by party
# By default, all events on all markets for all parties will be returned on the stream.
subscribe_events_request = vac.api.trading.ObserveEventsRequest(marketID=market_id)
for stream_resp in data_client.ObserveEventBus(subscribe_events_request):
    for events in stream_resp.events:
        # All events (as per request filter) arriving over the channel/stream will be printed
        print(events)
# :stream_events__
