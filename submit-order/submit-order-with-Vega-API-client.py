#!/usr/bin/python3

import base64
import binascii
import requests

from google.protobuf.empty_pb2 import Empty
import vegaapiclient as vac

from credentials import (
    NODE_URL_GRPC,
    WALLETSERVER_URL,
    WALLET_NAME,
    WALLET_PASSPHRASE,
)


def check(r: requests.Response):
    assert r.status_code == 200, "HTTP {} {}".format(r.status_code, r.text)


# Vega node: Create client for accessing public data
datacli = vac.VegaTradingDataClient(NODE_URL_GRPC)

# Vega node: Create client for trading (e.g. submitting orders)
tradingcli = vac.VegaTradingClient(NODE_URL_GRPC)

# Wallet server: Create a walletclient (see above for details)
walletclient = vac.WalletClient(WALLETSERVER_URL)
walletclient.login(WALLET_NAME, WALLET_PASSPHRASE)

# Get a list of markets
markets = datacli.Markets(Empty()).markets
marketID = markets[0].id

GENERATE_NEW_KEYPAIR = False
if GENERATE_NEW_KEYPAIR:
    # If you don't already have a keypair, generate one.
    response = walletclient.generatekey(WALLET_PASSPHRASE, [])
    check(response)
    pubKey = response.json()["key"]["pub"]
else:
    # List keypairs
    response = walletclient.listkeys()
    check(response)
    keys = response.json()["keys"]
    assert len(keys) > 0
    pubKey = keys[0]["pub"]

# Vega node: Prepare the SubmitOrder
order = vac.api.trading.SubmitOrderRequest(
    submission=vac.vega.OrderSubmission(
        marketID=marketID,
        partyID=pubKey,
        # price is an integer. For example 123456 is a price of 1.23456,
        # assuming 5 decimal places.
        price=100000,
        side=vac.vega.Side.SIDE_BUY,
        size=1,
        timeInForce=vac.vega.Order.TimeInForce.TIF_GTC,
        type=vac.vega.Order.Type.TYPE_LIMIT,
    )
)
print(f"Request for PrepareSubmitOrder: {order}")
response = tradingcli.PrepareSubmitOrder(order)
print(f"Response from PrepareSubmitOrder: {response}")

# Wallet server: Sign the prepared transaction
blob_base64 = base64.b64encode(response.blob).decode("ascii")
print(f"Request for SignTx: blob={blob_base64}, pubKey={pubKey}")
response = walletclient.signtx(blob_base64, pubKey)
check(response)
responsejson = response.json()
print(f"Response from SignTx: {responsejson}")
signedTx = responsejson["signedTx"]

# Vega node: Submit the signed transaction
request = vac.api.trading.SubmitTransactionRequest(
    tx=vac.vega.SignedBundle(
        data=base64.b64decode(signedTx["data"]),
        sig=base64.b64decode(signedTx["sig"]),
        pubKey=binascii.unhexlify(signedTx["pubKey"]),
    )
)
print(f"Request for SubmitTransaction: {request}")
response = tradingcli.SubmitTransaction(request)
assert response.success
print("All is well.")
