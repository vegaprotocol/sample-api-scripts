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

import helpers
import os

node_url_grpc = os.getenv("NODE_URL_GRPC")
if not helpers.check_var(node_url_grpc):
    print("Error: Invalid or missing NODE_URL_GRPC environment variable.")
    exit(1)

# __import_client:
import vegaapiclient as vac

# Vega gRPC clients for reading/writing data
data_client = vac.VegaTradingDataClient(node_url_grpc)
# :import_client__

#####################################################################################
#                        N E T W O R K   P A R A M E T E R S                        #
#####################################################################################

# __get_network_params:
# Request a list of network parameters configured on a Vega network
request = vac.api.trading.NetworkParametersRequest()
network_params = data_client.NetworkParameters(request)
print("Network Parameter:\n{}".format(network_params))
# :get_network_params__
