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
#                          B L O C K C H A I N   T I M E                            #
#####################################################################################

# __get_expiry_time:
# Request the current blockchain time, calculate an expiry time
url="$NODE_URL_REST/time"
response="$(curl -s "$url")"
blockchaintime="$(echo "$response" | jq -r .timestamp)"
expiresAt="$((blockchaintime+120*10**9))" # expire in 2 minutes
# :get_expiry_time__

echo "Blockchain time: $expiresAt"

#####################################################################################
#                      S U B M I T   P E G G E D   O R D E R                        #
#####################################################################################

# __prepare_submit_pegged_order:
# Prepare a submit pegged order message
cat >req.json <<EOF
{
    "submission": {
        "marketId": "$marketID",
        "size": "50",
        "side": "SIDE_BUY",
        "timeInForce": "TIME_IN_FORCE_GTT",
        "expiresAt": "$expiresAt",
        "type": "TYPE_LIMIT",
        "peggedOrder": {
            "offset": "-5",
            "reference": "PEGGED_REFERENCE_MID"
        }
    }
}
EOF
url="$NODE_URL_REST/orders/prepare/submit"
response="$(curl -s -XPOST -d @req.json "$url")"
orderRef="$(echo "$response" | jq -r '.submitId')"
# :prepare_submit_pegged_order__

echo "Prepared pegged order, ref: $orderRef"

# __sign_tx_pegged_order:
# Sign the prepared transaction
# Note: Setting propagate to true will also submit to a Vega node
blob="$(echo "$response" | jq -r .blob)"
test "$blob" == null && exit 1
cat >req.json <<EOF
{
    "tx": "$blob",
    "pubKey": "$pubKey",
    "propagate": true
}
EOF
url="$WALLETSERVER_URL/api/v1/messages/sync"
response="$(curl -s -XPOST -H "$hdr" -d @req.json "$url")"
# :sign_tx_pegged_order__

signedTx="$(echo "$response" | jq .signedTx)"
test "$signedTx" == null && exit 1

echo "Signed pegged order and sent to Vega"

# Wait for order submission to be included in a block
echo "Waiting for blockchain..."
sleep 4s
url="$NODE_URL_REST/orders/$orderRef"
response="$(curl -s "$url")"
orderID="$(echo "$response" | jq -r '.order.id')"
orderStatus="$(echo "$response" | jq -r '.order.status')"
orderPegged="$(echo "$response" | jq -r '.order.peggedOrder')"
createVersion="$(echo "$response" | jq -r '.order.version')"
orderReason="$(echo "$response" | jq -r '.order.reason')"

echo "Order pegged processed, ID: $orderID, Status: $orderStatus, Version: $createVersion"
echo "Reason: $orderReason"
echo "Pegged at: $orderPegged"

#####################################################################################
#                        A M E N D   P E G G E D   O R D E R                        #
#####################################################################################

# __prepare_amend_pegged_order:
# Prepare the amend pegged order message
cat >req.json <<EOF
{
    "amendment": {
        "marketId": "$marketID",
        "orderId": "$orderID",
        "sizeDelta": "-25",
        "timeInForce": "TIME_IN_FORCE_GTC",
        "peggedReference": "PEGGED_REFERENCE_BEST_BID",
        "peggedOffset": "-100"
    }
}
EOF
url="$NODE_URL_REST/orders/prepare/amend"
response="$(curl -s -XPOST -d @req.json "$url")"
# :prepare_amend_pegged_order__

echo "Pegged order amendment prepared for order ID: $orderID"

# __sign_tx_pegged_amend:
# Sign the prepared pegged order transaction for amendment
# Note: Setting propagate to true will also submit to a Vega node
blob="$(echo "$response" | jq -r .blob)"
test "$blob" == null && exit 1
cat >req.json <<EOF
{
    "tx": "$blob",
    "pubKey": "$pubKey",
    "propagate": true
}
EOF
url="$WALLETSERVER_URL/api/v1/messages/sync"
response="$(curl -s -XPOST -H "$hdr" -d @req.json "$url")"
# :sign_tx_pegged_amend__

echo "Signed pegged order amendment and sent to Vega"

# Wait for order submission to be included in a block
echo "Waiting for blockchain..."
sleep 4s
url="$NODE_URL_REST/orders/$orderRef"
response="$(curl -s "$url")"
orderID="$(echo "$response" | jq -r '.order.id')"
orderSize="$(echo "$response" | jq -r '.order.size')"
orderTif="$(echo "$response" | jq -r '.order.timeInForce')"
orderStatus="$(echo "$response" | jq -r '.order.status')"
orderPegged="$(echo "$response" | jq -r '.order.peggedOrder')"
orderVersion="$(echo "$response" | jq -r '.order.version')"
orderReason="$(echo "$response" | jq -r '.order.reason')"

echo "Amended pegged order:"
echo "ID: $orderID, Status: $orderStatus,"
echo " Size(Old): 50, Size(New): $orderSize,"
echo " TimeInForce(Old): TIME_IN_FORCE_GTT, TimeInForce(New): $orderTif"
echo " Version(Old): $createVersion, Version(New): $orderVersion"
echo "Reason: $orderReason"
echo "Pegged at: $orderPegged"

# Completed.
