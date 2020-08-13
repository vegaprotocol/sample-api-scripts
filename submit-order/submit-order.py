#!/usr/bin/python3

import base64
import binascii
import json
import requests

from credentials import (
    NODE_URL_REST,
    WALLETSERVER_URL,
    WALLET_NAME,
    WALLET_PASSPHRASE,
)

assert NODE_URL_REST.startswith("https://")
assert WALLETSERVER_URL.startswith("https://")


def check(r: requests.Response):
    assert r.status_code == 200, "HTTP {} {}".format(r.status_code, r.text)

# __create_wallet:
CREATE_NEW_WALLET = False
if CREATE_NEW_WALLET:
    # EITHER: Create new wallet
    url = "{base}/api/v1/wallets".format(base=WALLETSERVER_URL)
else:
    # OR: Log in to existing wallet
    url = "{base}/api/v1/auth/token".format(base=WALLETSERVER_URL)

# Make request to create new wallet or log in to existing wallet
req = {"wallet": WALLET_NAME, "passphrase": WALLET_PASSPHRASE}
response = requests.post(url, json=req)
check(response)

# Pull out the token and make a headers dict
token = response.json()["token"]
headers = {"Authorization": "Bearer " + token}
# :create_wallet__

# __generate_keypair:
GENERATE_NEW_KEYPAIR = False
pubKey = ""
if GENERATE_NEW_KEYPAIR:
    # EITHER: Generate a new keypair
    req = {
        "passphrase": WALLET_PASSPHRASE,
        "meta": [{"key": "alias", "value": "my_key_alias"}],
    }
    url = "{base}/api/v1/keys".format(base=WALLETSERVER_URL)
    response = requests.post(url, headers=headers, json=req)
    check(response)
    pubKey = response.json()["key"]["pub"]
else:
    # OR: List existing keypairs
    url = "{base}/api/v1/keys".format(base=WALLETSERVER_URL)
    response = requests.get(url, headers=headers)
    check(response)
    keys = response.json()["keys"]
    assert len(keys) > 0
    pubKey = keys[0]["pub"]
# :generate_keypair__

assert pubKey != ""

# __get_market:
# Next, get a Market ID
url = "{base}/markets".format(base=NODE_URL_REST)
response = requests.get(url)
check(response)
marketID = response.json()["markets"][0]["id"]
# :get_market__

# __prepare_order:
# Next, prepare a SubmitOrder
response = requests.get("{base}/time".format(base=NODE_URL_REST))
check(response)
blockchaintime = int(response.json()["timestamp"])
expiresAt = str(int(blockchaintime + 120 * 1e9))  # expire in 2 minutes

req = {
    "submission": {
        "marketID": marketID,
        "partyID": pubKey,
        "price": "100000",       # Note: price is an integer. For example 123456 
        "size": "100",           # is a price of 1.23456, assuming 5 decimal places.
        "side": "SIDE_BUY",
        "timeInForce": "TIF_GTT",
        "expiresAt": expiresAt,
        "type": "TYPE_LIMIT",
    }
}
print(
    "Request for PrepareSubmitOrder: {}".format(
        json.dumps(req, indent=2, sort_keys=True)
    )
)
url = "{base}/orders/prepare/submit".format(base=NODE_URL_REST)
response = requests.post(url, json=req)
check(response)
preparedOrder = response.json()
# :prepare_order__
print(
    "Response from PrepareSubmitOrder: {}".format(
        json.dumps(preparedOrder, indent=2, sort_keys=True)
    )
)

# __sign_tx:
# Wallet server: Sign the prepared transaction
blob = preparedOrder["blob"]
req = {"tx": blob, "pubKey": pubKey, "propagate": False}
print(
    "Request for SignTx: {}".format(json.dumps(req, indent=2, sort_keys=True))
)
url = "{base}/api/v1/messages".format(base=WALLETSERVER_URL)
response = requests.post(url, headers=headers, json=req)
check(response)
signedTx = response.json()["signedTx"]
# :sign_tx__
print(
    "Response from SignTx: {}".format(
        json.dumps(signedTx, indent=2, sort_keys=True)
    )
)

# __submit_tx:
# Vega node: Submit the signed transaction
req = {
    "tx": signedTx
}
print(
    "Request for SubmitTransaction: {}".format(
        json.dumps(req, indent=2, sort_keys=True)
    )
)
url = "{base}/transaction".format(base=NODE_URL_REST)
response = requests.post(url, json=req)
check(response)
# :submit_tx__

assert response.json()["success"]
print("All is well.")
