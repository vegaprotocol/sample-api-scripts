#!/usr/bin/python3

###############################################################################
#                        G E T   C H E C K P O I N T S                        #
###############################################################################

#  How to get checkpoint information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# __get_checkpoints:
# Request a list of checkpoints for a Vega network
url = f"{data_node_url_rest}/checkpoints"
response = requests.get(url)
helpers.check_response(response)
print("Checkpoints for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_checkpoints__
