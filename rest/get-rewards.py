#!/usr/bin/python3

###############################################################################
#                            G E T   R E W A R D S                            #
###############################################################################

#  How to get rewards information from a Data Node using REST calls:
#  ----------------------------------------------------------------------
#  Pagination is supported [default page size is 1000]
#   -> Check out pagination.py for example usage
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   partyId:  Vega party id (public key)
#   assetId:  Vega asset id
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

###############################################################################
#                           L I S T   R E W A R D S                           #
###############################################################################

# __get_rewards:
# Request a list of rewards for a Vega network
url = f"{data_node_url_rest}/rewards"
response = requests.get(url)
helpers.check_response(response)
print("Rewards for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_rewards__

# Find the first reward in the list (above) if it exists
asset_id = "3a834328d835cf79880dfc238a989c238fe32a62562690d717ab1ff42ad5003f"
if helpers.check_nested_response(response, "rewards"):
    first_reward = helpers.get_nested_response(response, "rewards")[0]["node"]
    asset_id = first_reward["assetId"]

###############################################################################
#                       R E W A R D S   B Y   P A R T Y                       #
###############################################################################

party_id = helpers.env_party_id()
assert party_id != ""

# __get_rewards_by_party:
# Request a list of rewards for a party on a Vega network
url = f"{data_node_url_rest}/deposits?partyId={party_id}"
response = requests.get(url)
helpers.check_response(response)
print("Rewards for a specific party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_rewards_by_party__

###############################################################################
#                       R E W A R D S   B Y   A S S E T                       #
###############################################################################

# Hint: Combine both rewards by asset and party to refine the query and improve performance

# __get_rewards_by_asset:
# Request a list of all rewards for an asset on a Vega network
url = f"{data_node_url_rest}/deposits?assetId={asset_id}"
response = requests.get(url)
helpers.check_response(response)
print("Rewards for a specific asset:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_rewards_by_asset__

###############################################################################
#                  L I S T   R E W A R D   S U M M A R I E S                  #
###############################################################################

# Hint: Rewards summaries are rewards grouped by party and asset
# For example, for a party/asset pair this is the sum of all rewards of all types over all time

# __get_reward_summaries:
# Request a list of all rewards for a Vega network
url = f"{data_node_url_rest}/rewards/summaries"
response = requests.get(url)
helpers.check_response(response)
print("Rewards summaries for network:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_reward_summaries__

###############################################################################
#              R E W A R D   S U M M A R I E S   ( F I L T E R S )              #
###############################################################################

# __get_reward_summaries_by_party:
# Request a list of all rewards for a party on a Vega network
url = f"{data_node_url_rest}/deposits?partyId={party_id}"
response = requests.get(url)
helpers.check_response(response)
print("Rewards summaries for a specific party:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_rewards_by_party__

###############################################################################
#                       R E W A R D S   B Y   A S S E T                       #
###############################################################################

# Hint: Combine both rewards by asset and party to refine the query and improve performance

# __get_rewards_by_asset:
# Request a list of all rewards for an asset on a Vega network
url = f"{data_node_url_rest}/deposits?assetId={asset_id}"
response = requests.get(url)
helpers.check_response(response)
print("Rewards summaries for a specific asset:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)
))
# :get_rewards_by_asset__
