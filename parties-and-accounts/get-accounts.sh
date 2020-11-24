#!/usr/bin/env bash

# Script language: bash

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
#

source helpers.sh

check_url "NODE_URL_REST" || exit 1
check_url "WALLETSERVER_URL" || exit 1

check_var "WALLET_NAME" || exit 1
check_var "WALLET_PASSPHRASE" || exit 1

#####################################################################################
#                           W A L L E T   S E R V I C E                             #
#####################################################################################

echo "Logging into wallet: $WALLET_NAME"

# __login_wallet:
# Log in to an existing wallet
req='{"wallet": "'"$WALLET_NAME"'","passphrase": "'"$WALLET_PASSPHRASE"'"}'
url="$WALLETSERVER_URL/api/v1/auth/token"
response="$(curl -s -XPOST -d "$req" "$url")"
token="$(echo "$response" | jq -r .token)"
# :login_wallet__

test "$token" == null && exit 1
echo "Logged in to wallet successfully"

# __get_pubkey:
# List key pairs and select public key to use
hdr="Authorization: Bearer $token"
url="$WALLETSERVER_URL/api/v1/keys"
response="$(curl -s -XGET -H "$hdr" "$url")"
pubkey="$(echo "$response" | jq -r '.keys[0].pub')"
# :get_pubkey__

test -n "$pubkey" || exit 1
test "$pubkey" == null && exit 1
echo "Selected pubkey for signing"

#####################################################################################
#                           M A R K E T   A C C O U N T S                           #
#####################################################################################

# Request a list of markets and select the first one
url="$NODE_URL_REST/markets"
response="$(curl -s "$url")"
marketID="$(echo "$response" | jq -r '.markets[0].id')"
# :get_market__

echo "Market found: $marketID"

# __get_accounts_by_market:
# Request a list of accounts for a market on a Vega network
url="$NODE_URL_REST/markets/$marketID/accounts"
response="$(curl -s "$url")"
accounts="$(echo "$response" | jq -r .accounts)"
echo "Market accounts:
$accounts"
# :get_accounts_by_market__

#####################################################################################
#                            P A R T Y   A C C O U N T S                            #
#####################################################################################

# __get_accounts_by_party:
# Request a list of accounts for a party (pubkey) on a Vega network
url="$NODE_URL_REST/parties/$pubkey/accounts"
response="$(curl -s "$url")"
accounts="$(echo "$response" | jq -r .accounts)"
echo "Party accounts:
$accounts"
# :get_accounts_by_party__

#####################################################################################
#                           P A R T Y   P O S I T I O N S                           #
#####################################################################################

# __get_positions_by_party:
# Request a list of positions for a party (pubkey) on a Vega network
url="$NODE_URL_REST/parties/$pubkey/positions"
response="$(curl -s "$url")"
positions="$(echo "$response" | jq -r .positions)"
echo "Party positions:
$positions"
# :get_positions_by_party__
