#!/usr/bin/python3

###############################################################################
#                          G E T   V E G A   T I M E                          #
###############################################################################

#  How to get vega time (current block time) from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is NOT supported on this endpoint.
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# __get_time:
# Request the latest timestamp in nanoseconds since epoch from the Vega network
url = f"{data_node_url_rest}/vega/time"
response = requests.get(url)
helpers.check_response(response)

# The "timestamp" field contains the resulting data we need.
vega_time = response.json()["timestamp"]
print("Vega time:\n{}".format(vega_time))
# :get_time__

# Print the human readable value of vega time (timestamp is a nanoseconds since epoch timestamp)
print(helpers.nano_ts_to_human_date(float(vega_time)))
