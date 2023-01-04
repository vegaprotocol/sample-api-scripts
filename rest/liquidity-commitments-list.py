#!/usr/bin/python3

import json
import requests
import helpers

# Vega wallet interaction helper, see login.py for detail
from login import token, pubkey

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")
# Load Vega wallet server URL, set in same way as above
wallet_server_url = helpers.get_from_env("WALLET_SERVER_URL")

# Load Vega market id
market_id = helpers.env_market_id()
assert market_id != ""

# Set market id in ENV or uncomment the line below to override market id directly
market_id = "e503cadb437861037cddfd7263d25b69102098a97573db23f8e5fc320cea1ce9"

#####################################################################################
#                 L I S T   L I Q U I D I T Y   P R O V I S I O N S                 #
#####################################################################################
# __get_liquidity_provisions:
# Request liquidity provisions for a party on a Vega network
url = f"{data_node_url_rest}/liquidity/provisions?partyId={pubkey}"
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(url)
helpers.check_response(response)
print("Liquidity Provisions for party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))

