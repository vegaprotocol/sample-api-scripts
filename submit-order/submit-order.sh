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

# __create_wallet:
CREATE_NEW_WALLET=no
if test "$CREATE_NEW_WALLET" == yes ; then
	### EITHER: Create new wallet ###
	url="$WALLETSERVER_URL/api/v1/wallets"
else
	### OR: Log in to existing wallet ###
	url="$WALLETSERVER_URL/api/v1/auth/token"
fi

# Make request to create new wallet or log in to existing wallet
req='{"wallet": "'"$WALLET_NAME"'","passphrase": "'"$WALLET_PASSPHRASE"'"}'
response="$(curl -s -XPOST -d "$req" "$url")"

### Pull out the token and make a headers var ###
token="$(echo "$response" | jq -r .token)"
test "$token" == null && exit 1
hdr="Authorization: Bearer $token"
# :create_wallet__

# __generate_keypair:
GENERATE_NEW_KEYPAIR=no
pubKey=""
if test "$GENERATE_NEW_KEYPAIR" == yes ; then
	### EITHER: Generate a new keypair ###
	req='{"passphrase":"'"$WALLET_PASSPHRASE"'","meta":[{"key":"alias","value":"my_key_alias"}]}'
	url="$WALLETSERVER_URL/api/v1/keys"
	response="$(curl -s -XPOST -H "$hdr" -d "$req" "$url")"
	pubKey="$(echo "$response" | jq -r .key.pub)"
else
	### OR: List existing keypairs ###
	url="$WALLETSERVER_URL/api/v1/keys"
	response="$(curl -s -XGET -H "$hdr" "$url")"
	pubKey="$(echo "$response" | jq -r '.keys[0].pub')"
fi
# :generate_keypair__

test -n "$pubKey" || exit 1
test "$pubKey" == null && exit 1

# __get_market:
### Next, get a Market ID ###
url="$NODE_URL_REST/markets"
echo "get market ID url: $url"
response="$(curl -s "$url")"
marketID="$(echo "$response" | jq -r '.markets[0].id')"
# :get_market__

# __prepare_order:
### Next, prepare a SubmitOrder ###

# Note: price is an integer. For example 123456 is a price of 1.23456,
# assuming 5 decimal places.

url="$NODE_URL_REST/time"
response="$(curl -s "$url")"
blockchaintime="$(echo "$response" | jq -r .timestamp)"
expiresAt="$((blockchaintime+120*10**9))" # expire in 2 minutes
cat >req.json <<EOF
{
    "submission": {
        "marketId": "$marketID",
        "partyId": "$pubKey",
        "price": "100000",
        "size": "100",
        "side": "SIDE_BUY",
        "timeInForce": "TIME_IN_FORCE_GTT",
        "expiresAt": "$expiresAt",
        "type": "TYPE_LIMIT"
    }
}
EOF
echo "Request for PrepareSubmitOrder: $(cat req.json)"
url="$NODE_URL_REST/orders/prepare/submit"
response="$(curl -s -XPOST -d @req.json "$url")"
echo "Response from PrepareSubmitOrder: $response"
# :prepare_order__

# __sign_tx:
### Wallet server: Sign the prepared transaction ###
blob="$(echo "$response" | jq -r .blob)"
test "$blob" == null && exit 1
cat >req.json <<EOF
{
    "tx": "$blob",
    "pubKey": "$pubKey",
    "propagate": false
}
EOF
echo "Request for SignTx: $(cat req.json)"
url="$WALLETSERVER_URL/api/v1/messages/sync"
response="$(curl -s -XPOST -H "$hdr" -d @req.json "$url")"
signedTx="$(echo "$response" | jq .signedTx)"
echo "Response from SignTx: $signedTx"
# :sign_tx__
test "$signedTx" == null && exit 1

# __submit_tx:
### Vega node: Submit the signed transaction ###
cat >req.json <<EOF
{
    "tx": $signedTx
}
EOF
echo "Request for SubmitTransaction: $(cat req.json)"
url="$NODE_URL_REST/transaction"
response="$(curl -s -XPOST -d @req.json "$url")"
# :submit_tx__

if ! echo "$response" | jq -r .success | grep -q '^true$' ; then
	echo "Failed"
	exit 1
fi
echo "All is well."
