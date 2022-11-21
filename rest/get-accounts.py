#!/usr/bin/python3

###############################################################################
#                           G E T   A C C O U N T S                           #
###############################################################################

#  How to get Vega account information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   filter.partyIds:      Vega party ids (public keys)
#   filter.marketIds:     Vega market ids
#   filter.assets:        Specific assets e.g. tDAI, tBTC, etc
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
#                  A C C O U N T S   B Y   M A R K E T  ( 1 )                 #
###############################################################################

market_id = helpers.env_market_id()
assert market_id != ""
print(f"Market found: {market_id}")

# __get_accounts_by_market:
# Request a list of accounts for a single market (repeat the filter for multiple markets)
url = f"{data_node_url_rest}/accounts?filter.marketIds={market_id}"
response = requests.get(url)
helpers.check_response(response)
print("Accounts filtered by market:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_accounts_by_market__

# Hint: Multiple filtering examples further down in this example script

###############################################################################
#                   A C C O U N T S   B Y   P A R T Y  ( 1 )                  #
###############################################################################

# __get_accounts_by_party:
# Request a list of accounts for a single party/pubkey (repeat the filter for multiple parties)
url = f"{data_node_url_rest}/accounts?filter.partyIds={pubkey}"
response = requests.get(url)
helpers.check_response(response)
print("Accounts filtered by party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_accounts_by_party__

# Hint: Multiple filtering examples further down in this example script

###############################################################################
#                      A C C O U N T S   B Y   A S S E T                      #
###############################################################################

# Request a list of assets and select the first one
url = f"{data_node_url_rest}/assets"
response = requests.get(url)
helpers.check_response(response)
asset_id = response.json()["assets"]["edges"][0]["node"]["id"]

assert asset_id != ""
print(f"Asset found: {asset_id}")

# __get_accounts_by_asset:
# Request a list of accounts for a single asset
url = f"{data_node_url_rest}/accounts?filter.assetId={asset_id}"
response = requests.get(url)
helpers.check_response(response)
print("Accounts filtered by asset:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_accounts_by_asset__

###############################################################################
#                  A C C O U N T S   B Y   M A R K E T  ( 2 )                 #
###############################################################################

# __get_accounts_by_market_filtered:
# Request a list of accounts for a market and asset with a specific account type (general)
url = f"{data_node_url_rest}/accounts?" \
      f"filter.marketIds={market_id}" \
      f"&filter.assetId={asset_id}" \
      f"&filter.accountTypes=ACCOUNT_TYPE_GENERAL"
response = requests.get(url)
helpers.check_response(response)
print("Accounts filtered by market and account type:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_accounts_by_market_filtered__

###############################################################################
#                   A C C O U N T S   B Y  P A R T Y  ( 2 )                   #
###############################################################################

# __get_accounts_by_party_filtered:
# Request a list of accounts for a party with a specific account types (general & margin)
url = f"{data_node_url_rest}/accounts?" \
      f"filter.partyIds={pubkey}" \
      f"&filter.accountTypes=ACCOUNT_TYPE_GENERAL" \
      f"&filter.accountTypes=ACCOUNT_TYPE_MARGIN"
response = requests.get(url)
helpers.check_response(response)
print("Accounts filtered by party and account type:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_accounts_by_party_filtered__
