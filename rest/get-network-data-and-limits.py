#!/usr/bin/python3

###############################################################################
#               G E T   N E T W O R K   D A T A  /  L I M I T S               #
###############################################################################

#  How to get network data/limits information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is NOT supported on these endpoints.
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                           N E T W O R K   D A T A                           #
###############################################################################

# __get_network_data:
# Request all data for a Vega network
url = f"{data_node_url_rest}/network/data"
response = requests.get(url)
helpers.check_response(response)
print("Network data:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_network_data__

###############################################################################
#                         N E T W O R K   L I M I T S                         #
###############################################################################

# __get_network_limits:
# Request all limits for a Vega network
url = f"{data_node_url_rest}/network/limits"
response = requests.get(url)
helpers.check_response(response)
print("Network limits:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_network_limits__
