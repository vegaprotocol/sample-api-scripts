#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (REST)

Apps/Libraries:
- REST: requests (https://pypi.org/project/requests/)
"""

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__

import requests
import json
import os
import helpers

node_url_rest = os.getenv("NODE_URL_REST")
if not helpers.check_url(node_url_rest):
    print("Error: Invalid or missing NODE_URL_REST environment variable.")
    exit(1)

# __get_assets:
# Request a list of assets available on a Vega network
url = "{base}/assets".format(base=node_url_rest)
response = requests.get(url)
helpers.check_response(response)
print("Assets:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_assets__

# Find asset with name DAI
found_asset_id = "UNKNOWN"
assets = response.json()["assets"]
for asset in assets:
    if asset["symbol"] == "tDAI":
        print()
        print("Found an asset with symbol tDAI:")
        found_asset_id = asset["id"]
        print(found_asset_id)
        print()
        break

if found_asset_id == "UNKNOWN":
    print("tDAI asset not found on specified Vega network, please propose and create the tDAI asset")

assert found_asset_id != "UNKNOWN"
print()

# __get_asset:
# Request a single asset by identifier on a Vega network
url = "{base}/assets/{id}".format(base=node_url_rest, id=found_asset_id)
response = requests.get(url)
helpers.check_response(response)
print("Asset by ID:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_asset__

# Completed.



