#!/usr/bin/python3

###############################################################################
#                  G E T   N E T W O R K   P A R A M E T E R S                #
###############################################################################

#  How to get Vega network parameters from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import requests
import helpers

# Load Vega data node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                L I S T   N E T W O R K   P A R A M E T E R S                #
###############################################################################

# __get_network_params:
# Request a list of network parameters configured on a Vega network
url = f"{data_node_url_rest}/network/parameters"
response = requests.get(url)
helpers.check_response(response)
print("Network parameters:\n")
for edge in response.json()['networkParameters']['edges']:
    print(edge['node'])
# :get_network_params__

parameter_key = response.json()['networkParameters']['edges'][0]['node']['key']
assert parameter_key != ""

print()
print(f"Selected parameter key: {parameter_key}")
print()

###############################################################################
#                S I N G L E   N E T W O R K   P A R A M E T E R              #
###############################################################################

# __get_network_param:
# Request a specific network parameter from those configured on a Vega network
url = f"{data_node_url_rest}/network/parameters/{parameter_key}"
response = requests.get(url)
helpers.check_response(response)
print(f"Network parameter for key {parameter_key}:\n")
print(response.json())
# :get_network_param__
