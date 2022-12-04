#!/usr/bin/python3

###############################################################################
#                             G E T   A S S E T S                             #
###############################################################################

#  How to get Vega asset information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   assetId:    Vega asset id
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers
import sys

# Load Vega data node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                            L I S T   A S S E T S                            #
###############################################################################

# __get_assets:
# Request a list of assets available and select the first one
url = f"{data_node_url_rest}/assets"
response = requests.get(url)
helpers.check_response(response)
print("Assets:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_assets__

# Find asset with name tDAI (available on Fairground Testnet)
asset_id = None
assets = response.json()["assets"]["edges"]
for asset in assets:
    if asset["node"]["details"]["symbol"] == "tDAI":
        print("Found an asset with symbol tDAI")
        asset_id = asset["node"]["id"]
        break

if asset_id is None:
    print("tDAI asset not found on specified Vega network" )
    sys.exit(1)

###############################################################################
#                           S I N G L E   A S S E T                           #
###############################################################################

# __get_asset:
# Request a specific asset using a pre-defined asset id
url = f"{data_node_url_rest}/asset/{asset_id}"
response = requests.get(url)
helpers.check_response(response)
print("Asset:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_asset__
