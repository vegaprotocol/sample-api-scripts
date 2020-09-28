#!/usr/bin/env bash

# Script language: bash
#
# Talks to:
# - Vega wallet (REST)
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
check_url "WALLETSERVER_URL" || exit 1
check_var "WALLET_NAME" || exit 1
check_var "WALLET_PASSPHRASE" || exit 1

# Log in to wallet
req='{"wallet": "'"$WALLET_NAME"'","passphrase": "'"$WALLET_PASSPHRASE"'"}'
url="$WALLETSERVER_URL/api/v1/auth/token"
response="$(curl -s -XPOST -d "$req" "$url")"
token="$(echo "$response" | jq -r .token)"
echo $response

# Get first key pair
test "$token" == null && exit 1
hdr="Authorization: Bearer $token"
url="$WALLETSERVER_URL/api/v1/keys"
response="$(curl -s -XGET -H "$hdr" "$url")"
pubKey="$(echo "$response" | jq -r '.keys[0].pub')"
echo $response

# __get_orders_for_party:
# Request a list of orders by party (pubKey)
url="$NODE_URL_REST/parties/$pubKey/orders"
response="$(curl -s "$url")"
echo $response
orders="$(echo "$response" | jq -r .orders)"
echo "OrdersByParty:
$orders"
# :get_orders_for_party__

# __get_trades_for_party:
# Request a list of trades by party (pubKey)
url="$NODE_URL_REST/parties/$pubKey/trades"
response="$(curl -s "$url")"
echo $response
trades="$(echo "$response" | jq -r .trades)"
echo "TradesByParty:
$trades"
# :get_trades_for_party__