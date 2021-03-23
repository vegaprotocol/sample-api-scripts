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

import queue
import os
import signal
import sys

node_url_grpc = os.getenv("NODE_URL_GRPC")

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
markets = data_client.Markets(vac.api.trading.MarketsRequest()).markets
market_id = markets[0].id
# :get_market__

print("Found market:")
print(market_id)

print("Connecting to stream...")

# __stream_events:
# Subscribe to the events bus stream for the marketID specified
# Required: type field - A collection of one or more event types e.g. BUS_EVENT_TYPE_ORDER.
# Required: batch_size field - Default: 0 - Total number of events to batch on server before sending to client.
# Optional: Market identifier - filter by market
#           Party identifier - filter by party
# By default, all events on all markets for all parties will be returned on the stream.
# e.g. all_types = vac.events.BUS_EVENT_TYPE_ALL
event_types = vac.events.BUS_EVENT_TYPE_MARKET_TICK
subscribe_events_request = vac.api.trading.ObserveEventBusRequest(batch_size=0, type=[event_types], market_id=market_id)
send_queue = queue.SimpleQueue()
stream = data_client.ObserveEventBus(iter(send_queue.get, None))
send_queue.put_nowait(subscribe_events_request)
for stream_resp in stream:
    for events in stream_resp.events:
        # All events (as per request filter) arriving over the channel/stream will be printed
        print(events)
# :stream_events__

print("Stream disconnected.")