#!/usr/bin/python3

import base64
import binascii
import json
import requests

from credentials import (
    MARKET_ID,
    NODE_URL,
    WALLETSERVER_URL,
    WALLET_NAME,
    WALLET_PASSPHRASE,
)


def check(r: requests.Response):
    assert r.status_code == 200, "HTTP {} {}".format(r.status_code, r.text)


CREATE_NEW_WALLET = False
if CREATE_NEW_WALLET:
    ### EITHER: Create new wallet ###
    url = "{base}/api/v1/wallets".format(base=WALLETSERVER_URL)
else:
    ### OR: Log in to existing wallet ###
    url = "{base}/api/v1/auth/token".format(base=WALLETSERVER_URL)

# Make request to create new wallet or log in to existing wallet
req = {"wallet": WALLET_NAME, "passphrase": WALLET_PASSPHRASE}
response = requests.post(url, json=req)
check(response)

### Pull out the token and make a headers dict ###
token = response.json()["token"]
headers = {"Authorization": "Bearer " + token}

GENERATE_NEW_KEYPAIR = False
pubKey = ""
if GENERATE_NEW_KEYPAIR:
    ### EITHER: Generate a new keypair
    req = {
        "passphrase": WALLET_PASSPHRASE,
        "meta": [{"key": "alias", "value": "my_key_alias"}],
    }
    url = "{base}/api/v1/keys".format(base=WALLETSERVER_URL)
    response = requests.post(url, headers=headers, json=req)
    check(response)
    pubKey = response.json()["key"]["pub"]
else:
    ### OR: List existing keypairs ###
    url = "{base}/api/v1/keys".format(base=WALLETSERVER_URL)
    response = requests.get(url, headers=headers)
    check(response)
    keys = response.json()["keys"]
    assert len(keys) > 0
    pubKey = keys[0]["pub"]

assert pubKey != ""

### Next, prepare a SubmitOrder ###
req = {
    "submission": {
        "marketID": MARKET_ID,
        "partyID": pubKey,
        "price": "100000",
        "size": "100",
        "side": "Buy",
        "timeInForce": "GTT",
        "expiresAt": "2000000000000000000",
        "type": "LIMIT",
    }
}
print(
    "Request for PrepareSubmitOrder: {}".format(
        json.dumps(req, indent=2, sort_keys=True)
    )
)
url = "{base}/orders/prepare".format(base=NODE_URL)
response = requests.post(url, json=req)
check(response)
preparedOrder = response.json()
print(
    "Response from PrepareSubmitOrder: {}".format(
        json.dumps(preparedOrder, indent=2, sort_keys=True)
    )
)

### Wallet server: Sign the prepared transaction ###
blob = preparedOrder["blob"]
req = {"tx": blob, "pubKey": pubKey, "propagate": False}
print("Request for SignTx: {}".format(json.dumps(req, indent=2, sort_keys=True)))
url = "{base}/api/v1/messages".format(base=WALLETSERVER_URL)
response = requests.post(url, headers=headers, json=req)
check(response)
signedTx = response.json()["signedTx"]
print("Response from SignTx: {}".format(json.dumps(signedTx, indent=2, sort_keys=True)))

### Vega node: Submit the signed transaction ###
req = {
    "tx": {
        "data": blob,
        "sig": signedTx["sig"],
        "pubKey": base64.b64encode(binascii.unhexlify(pubKey)).decode("ascii"),
    }
}
print(
    "Request for SubmitTransaction: {}".format(
        json.dumps(req, indent=2, sort_keys=True)
    )
)
url = "{base}/transaction".format(base=NODE_URL)
response = requests.post(url, json=req)
check(response)

assert response.json()["success"]
print("All is well.")
