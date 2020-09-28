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

import json
import os
import requests
import helpers

node_url_rest = os.getenv("NODE_URL_REST")
if not helpers.check_url(node_url_rest):
    print("Error: Invalid or missing NODE_URL_REST environment variable.")
    exit(1)

# __get_trades_for_order:
# Request a list of trades for a specific order on a Vega network
orderID = "V0000929211-0046318720"
url = "{base}/orders/{orderID}/trades".format(base=node_url_rest, orderID=orderID)
response = requests.get(url)
helpers.check_response(response)
responseJson = response.json()
print("TradesByOrderID:\n{}".format(json.dumps(responseJson, indent=2, sort_keys=True)))
# :get_trades_for_order__
