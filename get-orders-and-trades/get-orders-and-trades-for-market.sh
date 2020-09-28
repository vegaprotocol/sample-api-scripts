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

url="$NODE_URL_REST/markets"
echo "get market ID url: $url"
response="$(curl -s "$url")"
marketID="$(echo "$response" | jq -r '.markets[0].id')"

# __get_orders_for_market:
# Request a list of orders by market on a Vega network
url="$NODE_URL_REST/markets/$marketID/orders"
response="$(curl -s "$url")"
orders="$(echo "$response" | jq -r .orders)"
echo "OrdersByMarket:
$orders"
# :get_orders_for_market__

# __get_trades_for_market:
# Request a list of trades by market on a Vega network
url="$NODE_URL_REST/markets/$marketID/trades"
response="$(curl -s "$url")"
trades="$(echo "$response" | jq -r .trades)"
echo "TradesByMarket:
$trades"
# :get_trades_for_market__