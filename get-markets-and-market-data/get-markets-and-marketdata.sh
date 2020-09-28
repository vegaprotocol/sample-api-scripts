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

# __get_markets:
# Request a list of markets available on a Vega network
url="$NODE_URL_REST/markets"
response="$(curl -s "$url")"
markets="$(echo "$response" | jq -r .markets)"
echo "Markets:
$markets"
# :get_markets__

marketID="$(echo "$response" | jq -r '.markets[0].id')"

# __get_market_data:
# Request the market data for a market on a Vega network
url="$NODE_URL_REST/markets-data/$marketID"
response="$(curl -s "$url")"
marketData="$(echo "$response" | jq -r .marketData)"
echo "MarketData:
$marketData"
# :get_market_data__