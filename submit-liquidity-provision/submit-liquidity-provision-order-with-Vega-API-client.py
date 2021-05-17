#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega wallet (REST)
- Vega node (gRPC)

Apps/Libraries:
- Vega-API-client (https://pypi.org/project/Vega-API-client/)
"""

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__
#

import base64
import helpers
import time
import os

node_url_grpc = os.getenv("NODE_URL_GRPC")
if not helpers.check_var(node_url_grpc):
    print("Error: Invalid or missing NODE_URL_GRPC environment variable.")
    exit(1)

wallet_server_url = os.getenv("WALLETSERVER_URL")
if not helpers.check_url(wallet_server_url):
    print("Error: Invalid or missing WALLETSERVER_URL environment variable.")
    exit(1)

wallet_name = os.getenv("WALLET_NAME")
if not helpers.check_var(wallet_name):
    print("Error: Invalid or missing WALLET_NAME environment variable.")
    exit(1)

wallet_passphrase = os.getenv("WALLET_PASSPHRASE")
if not helpers.check_var(wallet_passphrase):
    print("Error: Invalid or missing WALLET_PASSPHRASE environment variable.")
    exit(1)

# Help guide users against including api version suffix on url
wallet_server_url = helpers.check_wallet_url(wallet_server_url)

# __import_client:
import vegaapiclient as vac

# Vega gRPC clients for reading/writing data
data_client = vac.VegaTradingDataClient(node_url_grpc)
trading_client = vac.VegaTradingClient(node_url_grpc)
wallet_client = vac.WalletClient(wallet_server_url)
# :import_client__

#####################################################################################
#                           W A L L E T   S E R V I C E                             #
#####################################################################################

print(f"Logging into wallet: {wallet_name}")

# __login_wallet:
# Log in to an existing wallet
response = wallet_client.login(wallet_name, wallet_passphrase)
helpers.check_response(response)
# Note: secret wallet token is stored internally for duration of session
# :login_wallet__

print("Logged in to wallet successfully")

# __get_pubkey:
# List key pairs and select public key to use
response = wallet_client.listkeys()
helpers.check_response(response)
keys = response.json()["keys"]
pubkey = keys[0]["pub"]
# :get_pubkey__

assert pubkey != ""
print("Selected pubkey for signing")

#####################################################################################
#                               F I N D   M A R K E T                               #
#####################################################################################

# __get_market:
# Request the identifier for the market to place on
markets = data_client.Markets(vac.api.trading.MarketsRequest()).markets
marketID = markets[0].id
# :get_market__

assert marketID != ""
marketName = markets[0].tradable_instrument.instrument.name
print(f"Market found: {marketID} {marketName}")

#####################################################################################
#                 L I S T   L I Q U I D I T Y   P R O V I S I O N S                 #
#####################################################################################

# __get_liquidity_provisions:
# Request liquidity provisions for the market
partyID="" # specify party ID if needed, otherwise all liquidity provisions for the market get returned 
liquidityProvisions = data_client.LiquidityProvisions(vac.api.trading.LiquidityProvisionsRequest(
    party=partyID,
    market=marketID
))

print("Liquidity provisions:\n{}".format(liquidityProvisions))
# :get_liquidity_provisions__

#####################################################################################
#              S U B M I T   L I Q U I D I T Y   C O M M I T M E N T                #
#####################################################################################

# Note: commitment_amount is an integer. For example 123456 is a price of 1.23456,
# for a market which is configured to have a precision of 5 decimal places.

# __prepare_liquidity_order:
# Prepare a liquidity commitment transaction message
order = vac.api.trading.PrepareLiquidityProvisionRequest(
    submission=vac.vega.LiquidityProvisionSubmission(
        market_id=marketID,
        commitment_amount=100,
        fee="0.01",
        reference="my-lp-reference",
        buys=[
            vac.vega.LiquidityOrder(
                reference=vac.vega.PEGGED_REFERENCE_MID,
                proportion=1,
                offset=-1
            ),
            vac.vega.LiquidityOrder(
                reference=vac.vega.PEGGED_REFERENCE_MID,
                proportion=2,
                offset=-2
            )
        ],
        sells=[
            vac.vega.LiquidityOrder(
                reference=vac.vega.PEGGED_REFERENCE_MID,
                proportion=1,
                offset=1
            ),
            vac.vega.LiquidityOrder(
                reference=vac.vega.PEGGED_REFERENCE_MID,
                proportion=2,
                offset=2
            ),
            vac.vega.LiquidityOrder(
                reference=vac.vega.PEGGED_REFERENCE_MID,
                proportion=5,
                offset=3
            )
        ]
    )
)
prepared_order = trading_client.PrepareLiquidityProvision(order)
# :prepare_liquidity_order__

print(f"Prepared liquidity commitment for market: {marketID}")

# __sign_tx_liquidity_order:
# Sign the prepared transaction
# Note: Setting propagate to true will submit to a Vega node
blob_base64 = base64.b64encode(prepared_order.blob).decode("ascii")
response = wallet_client.signtx(blob_base64, pubkey, True)
helpers.check_response(response)
signedTx = response.json()["signedTx"]
print(response.json())
# :sign_tx_liquidity_order__

print("Signed order and sent to Vega")

# Comment out the lines below to add a cancellation of the newly created LP commitment
print("To add cancellation step, uncomment line 181 of the script file")
exit(0)

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

#####################################################################################
#               A M E N D    L I Q U I D I T Y   C O M M I T M E N T                #
#####################################################################################

# __amend_liquidity_order:
# Prepare a liquidity commitment order message (it will now serve as an amendment request): modify fields to be amended
order = vac.api.trading.PrepareLiquidityProvisionRequest(
    submission=vac.commands.v1.commands.LiquidityProvisionSubmission(
        market_id=marketID,
        commitment_amount=500,
        fee="0.005",
        reference="my-lp-reference",
        buys=[
            vac.vega.LiquidityOrder(
                reference=vac.vega.PEGGED_REFERENCE_MID,
                proportion=1,
                offset=-1
            )
        ],
        sells=[
            vac.vega.LiquidityOrder(
                reference=vac.vega.PEGGED_REFERENCE_MID,
                proportion=1,
                offset=1
            )
        ]
    )
)
prepared_order = trading_client.PrepareLiquidityProvision(order)
# :amend_liquidity_order__

print(f"Prepared liquidity commitment (amendment)  for market: {marketID}")

# Sign the prepared transaction
# Note: Setting propagate to true will submit to a Vega node
blob_base64 = base64.b64encode(prepared_order.blob).decode("ascii")
response = wallet_client.signtx(blob_base64, pubkey, True)
helpers.check_response(response)
signedTx = response.json()["signedTx"]
print(response.json())

print("Signed order and sent to Vega")

time.sleep(10)

#####################################################################################
#               C A N C E L    L I Q U I D I T Y   C O M M I T M E N T              #
#####################################################################################

# __cancel_liquidity_order:
# Prepare a liquidity commitment order message (it will now serve as a cancellation request): set commitmentAmount to 0, 
# note that transaction may get rejected if removing previously supplied liquidity 
# will result in insufficient liquidity for the market
order = vac.api.trading.PrepareLiquidityProvisionRequest(
    submission=vac.commands.v1.commands.LiquidityProvisionSubmission(
        market_id=marketID,
        commitment_amount=0,
        reference="my-lp-reference",
    )
)
prepared_order = trading_client.PrepareLiquidityProvision(order)
# :cancel_liquidity_order__

print(f"Prepared liquidity commitment (cancellation) for market: {marketID}")

# Sign the prepared transaction
# Note: Setting propagate to true will submit to a Vega node
blob_base64 = base64.b64encode(prepared_order.blob).decode("ascii")
response = wallet_client.signtx(blob_base64, pubkey, True)
helpers.check_response(response)
signedTx = response.json()["signedTx"]
print(response.json())

print("Signed order and sent to Vega")


# Completed.
