#!/usr/bin/python3

###############################################################################
#                         V E G A   S T A T I S T I C S                       #
###############################################################################

#  How to get statistics from a Vega Node using REST calls:
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# Note: The statistics endpoint is proxied from Vega core so we must drop the api
# v2 portion of the url for testnet configurations, other networks might need
# a different url specified here...
node_url_rest = data_node_url_rest.strip("/api/v2")

# __get_statistics:
# Request statistics for a node on Vega
url = f"{node_url_rest}/statistics"
response = requests.get(url)
helpers.check_response(response)
print("Node statistics:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_statistics__
