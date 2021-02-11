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
pubKey="$(echo "$response" | jq -r '.keys[0].pub')"
# :get_pubkey__

test -n "$pubKey" || exit 1
test "$pubKey" == null && exit 1
echo "Selected pubkey for signing"

#####################################################################################
#                               F I N D   M A R K E T                               #
#####################################################################################

# __get_market:
# Request the identifier for the market to place on
url="$NODE_URL_REST/markets"
response="$(curl -s "$url")"
marketID="$(echo "$response" | jq -r '.markets[0].id')"
# :get_market__

echo "Market found: $marketID"

#####################################################################################
#                           F E E   E S T I M A T I O N                             #
#####################################################################################

# __get_fees_estimate:
# Request to estimate trading fees on a Vega network
cat >req.json <<EOF
{
    "order": {
        "marketId": "$marketID",
        "partyId": "$pubKey",
        "price": "100000",
        "size": "100",
        "side": "SIDE_BUY",
        "timeInForce": "TIME_IN_FORCE_GTC",
        "type": "TYPE_LIMIT"
    }
}
EOF
echo "Request for Fee Estimation: $(cat req.json)"
url="$NODE_URL_REST/orders/fee/estimate"
response="$(curl -s -XPOST -d @req.json "$url")"
echo "FeeEstimates:
$response"
# :get_fees_estimate__


#####################################################################################
#                         M A R G I N   E S T I M A T I O N                         #
#####################################################################################

# __get_margins_estimate:
# Request to estimate trading margin on a Vega network
cat >req.json <<EOF
{
    "order": {
        "marketId": "$marketID",
        "partyId": "$pubKey",
        "price": "600000",
        "size": "10",
        "side": "SIDE_BUY",
        "timeInForce": "TIME_IN_FORCE_GTC",
        "type": "TYPE_LIMIT"
    }
}
EOF
echo "Request for Margin Estimation: $(cat req.json)"
url="$NODE_URL_REST/orders/margins/estimate"
response="$(curl -s -XPOST -d @req.json "$url")"
echo "MarginsEstimates:
$response"
# :get_margins_estimate__
