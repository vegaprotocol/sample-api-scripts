#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (gRPC)

Apps/Libraries:
- Vega-API-client (https://pypi.org/project/Vega-API-client/)

Responses:
- response-examples.txt
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

# __get_parties:
# Request a list of parties trading on a Vega network
data_client = vac.VegaTradingDataClient(node_url_grpc)
req = vac.api.trading.PartiesRequest()
response = data_client.Parties(req)
print("Parties:\n{}".format(response))
# :get_parties__
