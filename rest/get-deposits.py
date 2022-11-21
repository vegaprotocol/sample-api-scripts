#!/usr/bin/python3

###############################################################################
#                           G E T   D E P O S I T S                           #
###############################################################################

#  How to get deposit information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   partyId:  Vega party id (public key)
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Vega wallet interaction helper, see login.py for detail
from login import pubkey

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                          L I S T   D E P O S I T S                          #
###############################################################################

# __get_deposits:
# Request a list of deposits for a Vega network
url = f"{data_node_url_rest}/deposits"
response = requests.get(url)
helpers.check_response(response)
print("Deposits for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_deposits__

# Find the first deposit in the list (above) if it exists
deposit_id = "3a834328d835cf79880dfc238a989c238fe32a62562690d717ab1ff42ad5003f"
if helpers.check_nested_response(response, "deposits"):
    first_deposit = helpers.get_nested_response(response, "deposits")[0]["node"]
    deposit_id = first_deposit["id"]

###############################################################################
#                      D E P O S I T S   B Y   P A R T Y                      #
###############################################################################

# __get_deposits_by_party:
# Request a list of deposits for a party on a Vega network
url = f"{data_node_url_rest}/deposits?partyId={pubkey}"
response = requests.get(url)
helpers.check_response(response)
print("Deposits for a specific party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_deposits_by_party__

###############################################################################
#                         D E P O S I T   B Y   I D                           #
###############################################################################

# __get_deposit_by_id:
# Request a single deposit for deposit id
url = f"{data_node_url_rest}/deposit/{deposit_id}"
response = requests.get(url)
helpers.check_response(response)
print("Deposit for id:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_deposit_by_id__
