#!/usr/bin/python3

###############################################################################
#                          G E T   T R A N S F E R S                          #
###############################################################################

#  How to get transfer information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   pubkey:     Vega party id (public key)
#   direction:  Which direction the transfer took place, e.g.
#               TRANSFER_DIRECTION_TRANSFER_FROM
#               TRANSFER_DIRECTION_TRANSFER_TO
#               TRANSFER_DIRECTION_TRANSFER_TO_OR_FROM
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                         L I S T   T R A N S F E R S                         #
###############################################################################

# __get_transfers:
# Request a list of transfers for a Vega network
url = f"{data_node_url_rest}/transfers"
response = requests.get(url)
helpers.check_response(response)
print("Transfers for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_transfers__

from_pubkey = "e4a81f9e67acee66406a84ace9fe2f70512a775c62301fbeb17eb6ecec83b2b9"
if helpers.check_nested_response(response, "transfers"):
    first_transfer = helpers.get_nested_response(response, "transfers")[0]["node"]
    from_pubkey = first_transfer["from"]

# Uncomment the following two lines to use an env specified party id
# from_pubkey = helpers.env_party_id()
# assert from_pubkey != ""

###############################################################################
#           T R A N S F E R S   B Y   P A R T Y  &  D I R E C T I O N         #
###############################################################################

# Hint: Both party (pubkey) and direction are required when specifying a pubkey

# __get_transfers_by_party:
# Request a list of transfers for a party (and direction) on a Vega network
url = f"{data_node_url_rest}/transfers?pubkey={from_pubkey}&direction=TRANSFER_DIRECTION_TRANSFER_TO"
response = requests.get(url)
helpers.check_response(response)
print("Transfers for a specific party and direction (TRANSFER_DIRECTION_TRANSFER_TO):\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_transfers_by_party__
