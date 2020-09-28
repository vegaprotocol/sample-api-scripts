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
import requests
import os
import helpers

node_url_rest = os.getenv("NODE_URL_REST")
if not helpers.check_url(node_url_rest):
    print("Error: Invalid or missing NODE_URL_REST environment variable.")
    exit(1)

# __get_order_by_ref:
# Request an order by reference on a Vega network
# Note: This is an example and order reference will be provided in the response
# from a prepareSubmitOrder request in the field named `submitID` or similar.
reference = "4617844f-6fab-4cf6-8852-e29dbd96e5f1"
url = "{base}/orders/{ref}".format(base=node_url_rest, ref=reference)
response = requests.get(url)
helpers.check_response(response)
print("OrderByReference:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_order_by_ref__
