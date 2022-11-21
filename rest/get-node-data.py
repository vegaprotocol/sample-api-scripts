#!/usr/bin/python3

###############################################################################
#                     G E T   V E G A   N O D E   D A T A                     #
###############################################################################
#  How to get Vega node information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported by list nodes only [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list nodes endpoint can be filtered by the following parameter:
#   epochSeq:    Epoch number
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import requests
import helpers
import json

# Load Vega data node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                        L I S T   N O D E S   D A T A                        #
###############################################################################

# __get_nodes:
# Request a list of information on the set of Vega nodes on a network
url = f"{data_node_url_rest}/nodes"
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Vega nodes:\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_nodes__

node_id = response.json()['nodes']['edges'][0]['node']['id']
assert node_id != ""

print()
print(f"Selected node with id: {node_id}")
print()

###############################################################################
#                              N O D E   D A T A                              #
###############################################################################

# __get_node_data:
# Request the node data for an id on a Vega network
url = f"{data_node_url_rest}/node/{node_id}"
response = requests.get(url)
helpers.check_response(response)
print("Node data:\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_node_data__

###############################################################################
#                         N O D E   S I G N A T U R E S                       #
###############################################################################

# __get_node_signatures:
# Request a list of node signatures on a Vega network
url = f"{data_node_url_rest}/node/signatures?id={node_id}"
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Vega node signatures:\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_node_signatures__
