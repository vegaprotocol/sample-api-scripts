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
#                              S U B M I T   O R D E R                              #
#####################################################################################

# __prepare_submit_order:
# Compose your submit order command, with desired deal ticket information
# Set your own user specific reference to find the order in next step and
# as a foreign key to your local client/trading application
orderRef=$pubKey-$(shuf -i 11111111-99999999 -n 1)-$(shuf -i 1111-9999 -n 1)-$(shuf -i 111111111111-999999999999 -n 1)

# Note: price is an integer. For example 123456 is a price of 1.23456,
# assuming 5 decimal places.
submission=$(cat <<-END
"orderSubmission": {
    "marketId": "$marketID",
    "price": "1",
    "size": "10",
    "side": "SIDE_BUY",
    "timeInForce": "TIME_IN_FORCE_GTT",
    "expiresAt": "$expiresAt",
    "type": "TYPE_LIMIT",
    "reference": "$orderRef"
}
END
)
# :prepare_submit_order__

echo "Order submission: $submission"

# __sign_tx_order:
# Sign the transaction with an order submission command
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
# :sign_tx_order__

echo "$response"

signedTx="$(echo "$response" | jq .signature)"
test "$signedTx" == null && exit 1

echo "Signed order and sent to Vega"

# Wait for order submission to be included in a block
echo "Waiting for blockchain..."
sleep 4s
url="$NODE_URL_REST/orders/$orderRef"
response="$(curl -s "$url")"
orderID="$(echo "$response" | jq -r '.order.id')"
orderStatus="$(echo "$response" | jq -r '.order.status')"
createVersion="$(echo "$response" | jq -r '.order.version')"

echo "Order processed, ID: $orderID, Status: $orderStatus, Version: $createVersion"

#####################################################################################
#                               A M E N D   O R D E R                               #
#####################################################################################

# __prepare_amend_order:
# Compose your amend order command, with changes to your existing order
amendment=$(cat <<-END
"orderAmendment": {
    "marketId": "$marketID",
    "orderId": "$orderID",
    "price": {
        "value": "2"
    },
    "sizeDelta": "-25",
    "timeInForce": "TIME_IN_FORCE_GTC"
}
END
)
# :prepare_amend_order__

echo "Order amendment: $amendment"

# __sign_tx_amend:
# Sign the transaction with an order amendment command
# Note: Setting propagate to true will also submit to a Vega node
cat >req.json <<EOF
{
    $amendment,
    "pubKey": "$pubKey",
    "propagate": true
}
EOF
url="$WALLETSERVER_URL/api/v1/command/sync"
response="$(curl -s -XPOST -H "$hdr" -d @req.json "$url")"
# :sign_tx_amend__

echo "$response"

signedTx="$(echo "$response" | jq .signature)"
test "$signedTx" == null && exit 1

echo "Signed amendment and sent to Vega"

# Wait for order submission to be included in a block
echo "Waiting for blockchain..."
sleep 4s
url="$NODE_URL_REST/orders/$orderRef"
response="$(curl -s "$url")"
orderID="$(echo "$response" | jq -r '.order.id')"
orderPrice="$(echo "$response" | jq -r '.order.price')"
orderSize="$(echo "$response" | jq -r '.order.size')"
orderTif="$(echo "$response" | jq -r '.order.timeInForce')"
orderStatus="$(echo "$response" | jq -r '.order.status')"
orderVersion="$(echo "$response" | jq -r '.order.version')"

echo "Amended Order:"
echo "ID: $orderID, Status: $orderStatus, Price(Old): 1,"
echo " Price(New): $orderPrice, Size(Old): 100, Size(New): $orderSize,"
echo " TimeInForce(Old): TIME_IN_FORCE_GTT, TimeInForce(New): $orderTif"
echo " Version(Old): $createVersion, Version(New): $orderVersion"

#####################################################################################
#                             C A N C E L   O R D E R S                             #
#####################################################################################

# Select the mode to cancel orders from the following (comment out others), default = 3

# __prepare_cancel_order_req1:
# 1 - Cancel single order for party (pubkey)
#     *** Include market and order identifier fields to cancel single order.
cancellation=$(cat <<-END
"orderCancellation": {
    "marketId": "$marketID",
    "orderId": "$orderID"
}
END
)
# :prepare_cancel_order_req1__

# __prepare_cancel_order_req2:
# 2 - Cancel all orders on market for party (pubkey)
#     *** Only include market identifier field.
cancellation=$(cat <<-END
"orderCancellation": {
    "marketId": "$marketID"
}
END
)
# :prepare_cancel_order_req2__

# __prepare_cancel_order_req3:
# 3 - Cancel all orders on all markets for party (pubkey)
cancellation=$(cat <<-END
"orderCancellation": {}
END
)
# :prepare_cancel_order_req3__

echo "Order cancellation: $cancellation"

# __sign_tx_cancel:
# Sign the transaction for cancellation
# Note: Setting propagate to true will also submit to a Vega node
cat >req.json <<EOF
{
    $cancellation,
    "pubKey": "$pubKey",
    "propagate": true
}
EOF
url="$WALLETSERVER_URL/api/v1/command/sync"
response="$(curl -s -XPOST -H "$hdr" -d @req.json "$url")"
# :sign_tx_cancel__

echo "$response"

signedTx="$(echo "$response" | jq .signature)"
test "$signedTx" == null && exit 1

echo "Signed cancellation and sent to Vega"

# Wait for order submission to be included in a block
echo "Waiting for blockchain..."
sleep 4s
url="$NODE_URL_REST/orders/$orderRef"
response="$(curl -s "$url")"
orderID="$(echo "$response" | jq -r '.order.id')"
orderStatus="$(echo "$response" | jq -r '.order.status')"

test "$orderStatus" != "STATUS_CANCELLED" && exit 1

# Completed.
echo "Cancelled order successfully:"
echo "ID: $orderID, Status: $orderStatus"
