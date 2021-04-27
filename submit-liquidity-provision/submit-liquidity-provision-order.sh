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

çNext, get a Market ID ###
# __get_market:
url="$NODE_URL_REST/markets"
echo "get market ID url: $url"
response="$(curl -s "$url")"
marketID="$(echo "$response" | jq -r '.markets[0].id')"
# :get_market__



### List liquidity provisions on the specified market
# __get_liquidity_provisions:
# Request liquidity provisions for the market
$partyID="" # specify party ID if needed, otherwise all liquidity provisions for the market get returned 
url="$NODE_URL_REST/liquidity-provisions/party/$partyID/market/$marketID"
echo "get liquidity provisions data for the market: $url"
response="$(curl -s "$url")"
echo "Liquidity provisions: $response"
# :get_liquidity_provisions__

### Submit liquidity commitment for the selected market
# Note: commitment_amount is an integer. For example 123456 is a price of 1.23456,
# for a market which is configured to have a precision of 5 decimal places.

# __prepare_liquidity_order:
# Prepare a liquidity commitment order message
url="$NODE_URL_REST/time"
response="$(curl -s "$url")"
cat >req.json <<EOF
{
    "submission": {
        "market_id": "$marketID",
        "commitment_amount": "100",
        "fee": "0.01",
        "buys": [
          {
            "offset": "-1",
            "proportion": "1",
            "reference": "PEGGED_REFERENCE_MID"
          },
          {
            "offset": "-2",
            "proportion": "2",
            "reference": "PEGGED_REFERENCE_MID"
          }
        ],
        "sells": [
          {
            "offset": "1",
            "proportion": "1",
            "reference": "PEGGED_REFERENCE_MID"
          },
          {
            "offset": "2",
            "proportion": "2",
            "reference": "PEGGED_REFERENCE_MID"
          },
          {
            "offset": "3",
            "proportion": "5",
            "reference": "PEGGED_REFERENCE_MID"
          }
        ]
    }
}
EOF
echo "Request for PrepareLiquidityProvision: $(cat req.json)"
url="$NODE_URL_REST/liquidity-provisions/prepare/submit"
response="$(curl -s -XPOST -d @req.json "$url")"
# :prepare_liquidity_order__

echo "Response from PrepareLiquidityProvision: $response"

# __sign_tx_liquidity_order:
# Sign the prepared liquidity order transaction
# Note: Setting propagate to true will also submit to a Vega node
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
url="$WALLETSERVER_URL/api/v1/messages"
response="$(curl -s -XPOST -H "$hdr" -d @req.json "$url")"
signedTx="$(echo "$response" | jq .signedTx)"
echo "Response from SignTx: $signedTx"
# :sign_tx_liquidity_order__
test "$signedTx" == null && exit 1

# __submit_tx_liquidity_order:
# Submit the signed transaction to Vega network
cat >req.json <<EOF
{
    "tx": $signedTx
}
EOF
echo "Request for SubmitTransaction: $(cat req.json)"
url="$NODE_URL_REST/transaction"
response="$(curl -s -XPOST -d @req.json "$url")"
# :submit_tx_liquidity_order__

### Comment out the lines below to add a cancellation of the newly created LP commitment
echo "To add cancellation step, uncomment line 176 of the script file"
exit 0

### Amend liquidity commitment for the selected market

# __amend_liquidity_order:
# Prepare a liquidity commitment order message (it will now serve as an amendment request): modify fields to be amended
url="$NODE_URL_REST/time"
response="$(curl -s "$url")"
cat >req.json <<EOF
{
    "submission": {
        "market_id": "$marketID",
        "commitment_amount": "500",
        "fee": "0.005",
        "buys": [
          {
            "offset": "-1",
            "proportion": "1",
            "reference": "PEGGED_REFERENCE_MID"
          }
        ],
        "sells": [
          {
            "offset": "1",
            "proportion": "1",
            "reference": "PEGGED_REFERENCE_MID"
          }
        ]
    }
}
EOF
echo "Request for PrepareLiquidityProvision (amendment): $(cat req.json)"
url="$NODE_URL_REST/liquidity-provisions/prepare/submit"
response="$(curl -s -XPOST -d @req.json "$url")"
# :amend_liquidity_order__

echo "Response from PrepareLiquidityProvision (amendment): $response"

# Sign the prepared liquidity order transaction
# Note: Setting propagate to true will also submit to a Vega node
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
url="$WALLETSERVER_URL/api/v1/messages"
response="$(curl -s -XPOST -H "$hdr" -d @req.json "$url")"
signedTx="$(echo "$response" | jq .signedTx)"
echo "Response from SignTx: $signedTx"
test "$signedTx" == null && exit 1

# Submit the signed transaction to Vega network
cat >req.json <<EOF
{
    "tx": $signedTx
}
EOF
echo "Request for SubmitTransaction: $(cat req.json)"
url="$NODE_URL_REST/transaction"
response="$(curl -s -XPOST -d @req.json "$url")"

sleep 10s

### Cancel liquidity commitment for the selected market

sleep 10s

# __cancel_liquidity_order:
# Prepare a liquidity commitment order message (it will now serve as a cancellation request): set commitmentAmount to 0, 
# note that transaction may get rejected if removing previously supplied liquidity 
# will result in insufficient liquidity for the market
url="$NODE_URL_REST/time"
response="$(curl -s "$url")"
cat >req.json <<EOF
{
    "submission": {
        "market_id": "$marketID",
        "commitment_amount": "0"
    }
}
EOF
echo "Request for PrepareLiquidityProvision (cancellation): $(cat req.json)"
url="$NODE_URL_REST/liquidity-provisions/prepare/submit"
response="$(curl -s -XPOST -d @req.json "$url")"
# :cancel_liquidity_order__

echo "Response from PrepareLiquidityProvision (cancellation): $response"

# Sign the prepared liquidity order transaction
# Note: Setting propagate to true will also submit to a Vega node
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
url="$WALLETSERVER_URL/api/v1/messages"
response="$(curl -s -XPOST -H "$hdr" -d @req.json "$url")"
signedTx="$(echo "$response" | jq .signedTx)"
echo "Response from SignTx: $signedTx"
test "$signedTx" == null && exit 1

# Submit the signed transaction to Vega network
cat >req.json <<EOF
{
    "tx": $signedTx
}
EOF
echo "Request for SubmitTransaction: $(cat req.json)"
url="$NODE_URL_REST/transaction"
response="$(curl -s -XPOST -d @req.json "$url")"









if ! echo "$response" | jq -r .success | grep -q '^true$' ; then
	echo "Failed"
	exit 1
fi
echo "All is well."
