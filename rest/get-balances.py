#!/usr/bin/python3

###############################################################################
#                  G E T   H I S T O R I C   B A L A N C E S                  #
###############################################################################

#  How to get balance changes for accounts from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  Date Range is supported
#   -> Check out date-range.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   filter.assetId:       Specific asset id
#   filter.partyIds:      Vega party ids (public keys)
#   filter.marketIds:     Vega market ids
#   filter.accountTypes:  Account types e.g. infrastructure, general, etc
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
#        B A L A N C E S   B Y   P A R T Y   &   A C C O U N T  T Y P E       #
###############################################################################

# Hint: Include multiple party ids as repeated filter.partyIds=XYZ query params
#       The same principle works for account types as shown below:

# __get_balances_by_party_and_account_type:
# Request a list of historic balance changes for a Vega party id and account types
url = f"{data_node_url_rest}/balance/changes?filter.partyIds={pubkey}" \
      f"&filter.accountTypes=ACCOUNT_TYPE_GENERAL&filter.accountTypes=ACCOUNT_TYPE_MARGIN"
print(url)
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Historic balance changes filtered by party and account types:\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# :get_balances_by_party_and_account_type__

# Load Vega market id
market_id = helpers.env_market_id()
assert market_id != ""

###############################################################################
#       B A L A N C E S   B Y   M A R K E T   &   A C C O U N T  T Y P E      #
###############################################################################

# Hint: Include multiple market ids as repeated filter.marketIds=XYZ query params
#       This is the same principle as in the previous example

# __get_balances_by_market_and_account_type:
# Request a list of historic balance changes for a Vega party id and account types
url = f"{data_node_url_rest}/balance/changes?filter.marketIds={market_id}" \
      f"&filter.accountTypes=ACCOUNT_TYPE_MARGIN"
print(url)
response = requests.get(url)
helpers.check_response(response)
response_json = response.json()
print("Historic balance changes filtered by market and account types:\n{}".format(
    json.dumps(response_json, indent=2, sort_keys=True)
))
# __get_balances_by_market_and_account_type:






