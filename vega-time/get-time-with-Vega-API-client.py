#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (gRPC)

Apps/Libraries:
- gRPC: Vega-API-client (https://pypi.org/project/Vega-API-client/)
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

# __import_client:
import vegaapiclient as vac
# :import_client__

node_url_grpc = os.getenv("NODE_URL_GRPC")

# __get_time:
# Request the latest timestamp in nanoseconds since epoch from the Vega network
data_client = vac.VegaTradingDataClient(node_url_grpc)

# The "timestamp" field contains the resulting data we need.
vega_time = data_client.GetVegaTime(vac.api.trading.GetVegaTimeRequest())
print("Vega time:\n{}".format(vega_time))
# :get_time__
