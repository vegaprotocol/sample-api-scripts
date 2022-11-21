#!/usr/bin/python3

###############################################################################
#                        G E T   W I T H D R A W A L S                        #
###############################################################################

#  How to get withdrawal information from a Data Node using REST calls:
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
#                       L I S T   W I T H D R A W A L S                       #
###############################################################################

# __get_withdrawals:
# Request a list of withdrawals for a Vega network
url = f"{data_node_url_rest}/withdrawals"
response = requests.get(url)
helpers.check_response(response)
print("Withdrawals for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_withdrawals__

# Find the first withdrawal in the list (above) if it exists
withdrawal_id = "3a834328d835cf79880dfc238a989c238fe32a62562690d717ab1ff42ad5003f"
if helpers.check_nested_response(response, "withdrawals"):
    first_withdrawal = helpers.get_nested_response(response, "withdrawals")[0]["node"]
    withdrawal_id = first_withdrawal["id"]

###############################################################################
#                   W I T H D R A W A L S   B Y   P A R T Y                   #
###############################################################################

# __get_withdrawals_by_party:
# Request a list of withdrawals for a party on a Vega network
url = f"{data_node_url_rest}/withdrawals?partyId={pubkey}"
response = requests.get(url)
helpers.check_response(response)
print("Withdrawals for a specific party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_withdrawals_by_party__

###############################################################################
#                       W I T H D R A W A L   B Y   I D                       #
###############################################################################

# __get_withdrawal_by_id:
# Request a single withdrawal for withdrawal id
url = f"{data_node_url_rest}/withdrawal/{withdrawal_id}"
response = requests.get(url)
helpers.check_response(response)
print("Withdrawal for id:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_withdrawal_by_id__
