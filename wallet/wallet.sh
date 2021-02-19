#!/usr/bin/env bash

# Script language: bash
#
# Talks to:
# - Vega wallet (REST)
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

wallet_name=$(shuf -i 11111111-99999999 -n 1)-$(shuf -i 1111-9999 -n 1)-$(shuf -i 111111111111-999999999999 -n 1)
wallet_passphrase=$(shuf -i 11111111-99999999 -n 1)-$(shuf -i 1111-9999 -n 1)-$(shuf -i 111111111111-999999999999 -n 1)

# __create_wallet:
# Create a new wallet:
req='{"wallet": "'"$wallet_name"'","passphrase": "'"$wallet_passphrase"'"}'
url="$WALLETSERVER_URL/api/v1/wallets"
response="$(curl -s -XPOST -d "$req" "$url")"
token="$(echo "$response" | jq -r .token)"
# :create_wallet__


test "$token" == null && exit 1


# The example below uses the credentials we just created
# and in practice you don't need to log in immediately after
# creating a new wallet, as the response already contains the
# token that you need to authenticate with future requests.


# __login_wallet:
# Log in to an existing wallet
req='{"wallet": "'"$wallet_name"'","passphrase": "'"$wallet_passphrase"'"}'
url="$WALLETSERVER_URL/api/v1/auth/token"
response="$(curl -s -XPOST -d "$req" "$url")"
token="$(echo "$response" | jq -r .token)"
# :login_wallet__


test "$token" == null && exit 1


# __generate_keypair:
# Generate a new key pair
hdr="Authorization: Bearer $token"
req='{"passphrase":"'"$wallet_passphrase"'","meta":[{"key":"alias","value":"my_key_alias"}]}'
url="$WALLETSERVER_URL/api/v1/keys"
response="$(curl -s -XPOST -H "$hdr" -d "$req" "$url")"
# :generate_keypair__


pubKey="$(echo "$response" | jq -r .key.pub)"
test -n "$pubKey" || exit 1
test "$pubKey" == null && exit 1


# __get_keys:
# Request all key pairs
hdr="Authorization: Bearer $token"]
url="$WALLETSERVER_URL/api/v1/keys"
response="$(curl -s -XGET -H "$hdr" "$url")"
# :get_keys__


# __get_key:
# Request a single key pair
hdr="Authorization: Bearer $token"
url="$WALLETSERVER_URL/api/v1/keys/$pubKey"
response="$(curl -s -XGET -H "$hdr" "$url")"
pubKey="$(echo "$response" | jq -r '.keys[0].pub')"
# :get_key__


# __sign_tx:
# Sign a transaction - Note: setting "propagate" to true will also submit the tx to Vega node
hdr="Authorization: Bearer $token"
# blob is an example of base64 data returned from a Vega node 'Prepare<operation>' call
blob="ZGF0YSByZXR1cm5lZCBmcm9tIGEgVmVnYSBub2RlICdQcmVwYXJlPG9wZXJhdGlvbj4nIGNhbGw="
test "$blob" == null && exit 1
cat >req.json <<EOF
{
    "tx": "$blob",
    "pubKey": "$pubKey",
    "propagate": false
}
EOF
url="$WALLETSERVER_URL/api/v1/messages/sync"
response="$(curl -s -XPOST -H "$hdr" -d @req.json "$url")"
signedTx="$(echo "$response" | jq .signedTx)"
# :sign_tx__

test "$signedTx" == null && exit 1

# __logout_wallet:
# Log out of a wallet
hdr="Authorization: Bearer $token"
url="$WALLETSERVER_URL/api/v1/auth/token"
response="$(curl -s -XDELETE -H "$hdr" "$url")"
# :logout_wallet__