#!/usr/bin/python3

###############################################################################
#                     G E T   L E D G E R   E N T R I E S                     #
###############################################################################

#  How to get ledger entries from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:

#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Vega wallet interaction helper, see login.py for detail
# from login import pubkey

# Load Vega data node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                    L I S T   L E D G E R   E N T R I E S                    #
###############################################################################

party_id = helpers.env_party_id()
assert party_id != ""
party_id = "d8742dbe34198241b96381012be71615a48da2b1c60f76f25ae5ed87fea9c500"

# __get_ledger_entries_from_account:
# List ledger entries with filtering on the sending account (accountFrom...)
url = f"{data_node_url_rest}/ledgerentry/history?filter.accountFromFilter.partyIds={party_id}"
print(url)
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Ledger entries (sending account):\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_ledger_entries_from_account__


# __get_ledger_entries_to_account:
# List ledger entries with filtering on the receiving account (accountFrom...)
url = f"{data_node_url_rest}/ledgerentry/history?filter.accountToFilter.partyIds={party_id}"
print(url)
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Ledger entries (receiving account):\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_ledger_entries_to_account__

# todo: can also refine further with a particular asset id, market id or account type
# todo: can also refine further with a particular asset id, market id or account type
# todo: list ledger entries with filtering on the sending AND receiving account
# todo: list ledger entries with filtering on the transfer type (on top of above or as a standalone)
