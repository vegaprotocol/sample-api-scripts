#!/usr/bin/python3

###############################################################################
#                            G E T    P A R T I E S                           #
###############################################################################

#  How to get Vega party information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by the following parameter:
#   partyId:      Vega party id (public key)
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Vega wallet interaction helper, see login.py for detail
from login import pubkey

# Load Vega data node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                      P A R T I E S   B Y   M A R K E T                      #
###############################################################################

# TODO: this needs implementing in api

market_id = helpers.env_market_id()
assert market_id != ""

# __get_parties_by_market:
# Request a list of parties for a single market (repeat the filter for multiple markets)
# url = f"{data_node_url_rest}/accounts?filter.marketIds={market_id}"
# response = requests.get(url)
# helpers.check_response(response)
# response_json = response.json()
# print("Accounts filtered by market:\n{}".format(
#     json.dumps(response_json, indent=2, sort_keys=True)
# ))
# :get_parties_by_market__

###############################################################################
#                           L I S T   P A R T I E S                           #
###############################################################################

# __get_parties:
url = f"{data_node_url_rest}/parties"
response = requests.get(url)
helpers.check_response(response)
print("Parties for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_parties__

###############################################################################
#                            P A R T Y   B Y   I D                            #
###############################################################################

party_id = helpers.env_party_id()
assert party_id != ""

# __get_party:
# Request a specific party using a pre-defined party id (pubkey)
url = f"{data_node_url_rest}/parties?partyId={party_id}"
response = requests.get(url)
helpers.check_response(response)
print("Party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_party__
