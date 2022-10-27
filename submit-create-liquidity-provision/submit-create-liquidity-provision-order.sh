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

check_var "VEGA_MARKET" || exit 1

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

### Next, get a Market ID ###
# __get_market:
# url="$NODE_URL_REST/markets"
# echo "get market ID url: $url"
# response="$(curl -s "$url")"
# marketID="$(echo "$response" | jq -r '.markets[0].id')"
# :get_market__
marketID=$VEGA_MARKET

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
# Note: commitment_amount is an integer. For example 1234567891234567890 is a price of 1.234567891234567890,
# for a settlement asset (ERC20) which is configured to have a precision of 18 decimal places.

# __prepare_liquidity_order:
# Compose a submit liquidity provision command
submission=$(cat <<-END
"liquidityProvisionSubmission": {
    "market_id": "$marketID",
    "commitment_amount": "100",
    "fee": "0.01",
    "buys": [
      {
        "offset": "1",
        "proportion": "1",
        "reference": "PEGGED_REFERENCE_MID"
      },
      {
        "offset": "2",
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
END
)
# :prepare_liquidity_order__

echo "Liquidity provision submission: $submission"

# __sign_tx_liquidity_order:
# Sign the transaction with an LP submission
# Note: Setting propagate to true will also submit to a Vega node
cat >req.json <<EOF
{
    $submission,
    "pubKey": "$pubKey",
    "propagate": true
}
EOF
url="$WALLETSERVER_URL/api/v1/command/sync"
response="$(curl -s -XPOST -H "$hdr" -d @req.json "$url")"
# :sign_tx_liquidity_order__

echo "$response"

signedTx="$(echo "$response" | jq .signature)"
test "$signedTx" == null && exit 1

echo "Signed liquidity commitment and sent to Vega"
