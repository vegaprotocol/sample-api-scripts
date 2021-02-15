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
import os
import helpers

node_url_rest = os.getenv("NODE_URL_REST")
if not helpers.check_url(node_url_rest):
    print("Error: Invalid or missing NODE_URL_REST environment variable.")
    exit(1)

# __get_time:
# Request the latest timestamp in nanoseconds since epoch from the Vega network
url = "{base}/time".format(base=node_url_rest)
response = requests.get(url)
helpers.check_response(response)

# The "timestamp" field contains the resulting data we need.
vega_time = response.json()["timestamp"]
print("Vega time:\n{}".format(vega_time))
# :get_time__
