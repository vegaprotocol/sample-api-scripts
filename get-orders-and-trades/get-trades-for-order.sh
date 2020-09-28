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

# __get_trades_for_order:
# Request a list of trades for a specific order on a Vega network
orderID="V0000929211-0046318720"
url="$NODE_URL_REST/orders/$orderID/trades"
response="$(curl -s "$url")"
trades="$(echo "$response" | jq -r .trades)"
echo "TradesByOrderID:
$trades"
# :get_trades_for_order__