#!/usr/bin/env bash

source credentials.sh || exit 1

if test "$MARKET_ID" == AMARKETID ; then
    echo "Please set MARKET_ID in credentials.sh"
    exit 1
fi

if echo "$NODE_URL" | grep -q example.com ; then
    echo "Please set NODE_URL in credentials.sh"
    exit 1
fi

if echo "$WALLETSERVER_URL" | grep -q example.com ; then
    echo "Please set WALLETSERVER_URL in credentials.sh"
    exit 1
fi

if test -z "$WALLET_NAME" -o -z "$WALLET_PASSPHRASE" ; then
    echo "Please set WALLET_NAME and WALLET_PASSPHRASE in credentials.sh"
    exit 1
fi

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


GENERATE_NEW_KEYPAIR=yes
pubKey=""
if test "$GENERATE_NEW_KEYPAIR" == yes ; then
    ### EITHER: Generate a new keypair
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

test -n "$pubKey" || exit 1
test "$pubKey" == null && exit 1

### Next, prepare a SubmitOrder ###
cat >req.json <<EOF
{
    "submission": {
        "marketID": "$MARKET_ID",
        "partyID": "$pubKey",
        "price": "100000",
        "size": "100",
        "side": "Buy",
        "timeInForce": "GTT",
        "expiresAt": "2000000000000000000",
        "type": "LIMIT"
    }
}
EOF
echo "Request for PrepareSubmitOrder: $(cat req.json)"
url="$NODE_URL/orders/prepare"
response="$(curl -s -XPOST -d "$(cat req.json)" "$url")"
echo "Response from PrepareSubmitOrder: $response"

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
url="$WALLETSERVER_URL/api/v1/messages"
response="$(curl -s -XPOST -H "$hdr" -d "$(cat req.json)" "$url")"
signedTx="$(echo "$response" | jq .signedTx)"
echo "Response from SignTx: $signedTx"
test "$signedTx" == null && exit 1

### Vega node: Submit the signed transaction ###
sig="$(echo "$signedTx" | jq -r .sig)"
test "$sig" == null && exit 1
base64encodedPubKey="$(echo -n "$pubKey" | xxd -r -p | base64)"
cat >req.json <<EOF
{
	"tx": {
		"data": "$blob",
		"sig": "$sig",
		"pubKey": "$base64encodedPubKey"
	}
}
EOF
echo "Request for SubmitTransaction: $(cat req.json)"
url="$NODE_URL/transaction"
response="$(curl -s -XPOST -d "$(cat req.json)" "$url")"

if ! echo "$response" | jq -r .success | grep -q '^true$' ; then
    echo "Failed"
    exit 1
fi
echo "All is well."
