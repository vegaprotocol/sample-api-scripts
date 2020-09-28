#!/usr/bin/env bash

# Script language: bash
#
# Talks to:
# - Vega node (REST)
#
# Apps/Libraries:
# - REST: curl

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__

source helpers.sh

check_url "NODE_URL_REST" || exit 1

# __get_order_by_ref:
# Request an order by reference on a Vega network
# Note: This is an example and order reference will be provided in the response
# from a prepareSubmitOrder request in the field named `submitID` or similar.
reference="4617844f-6fab-4cf6-8852-e29dbd96e5f1"
url="$NODE_URL_REST/orders/$reference"
response="$(curl -s "$url")"
order="$(echo "$response" | jq -r .order)"
echo "OrderByReference:
$order"
# :get_order_by_ref__