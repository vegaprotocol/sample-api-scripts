#!/usr/bin/python3

import base64
import requests
import vegaapiclient as vac

from credentials import (
    WALLETSERVER_URL,
    WALLET_NAME,
    WALLET_PASSPHRASE,
)

assert WALLETSERVER_URL.startswith("https://")


def check(r: requests.Response):
    assert r.status_code == 200, "HTTP {} {}".format(r.status_code, r.text)


walletclient = vac.WalletClient(WALLETSERVER_URL)

CREATE_NEW_WALLET = False
if CREATE_NEW_WALLET:
    # If this is your first time: create a new wallet.
    response = walletclient.create(WALLET_NAME, WALLET_PASSPHRASE)
    check(response)
else:
    # If this is *not* your first time: log in to an existing wallet.
    response = walletclient.login(WALLET_NAME, WALLET_PASSPHRASE)
    check(response)

GENERATE_NEW_KEYPAIR = False
if GENERATE_NEW_KEYPAIR:
    # If you don't already have a keypair, generate one.
    response = walletclient.generatekey(WALLET_PASSPHRASE, [])
    check(response)
    # Print key information. Note that the private key is *not* returned.
    print("Key: {}".format(response.json()["key"]))
else:
    # List keypairs
    response = walletclient.listkeys()
    check(response)
    for key in response.json()["keys"]:
        print("Key: {}".format(key))

# Get one keypair
myPubKey = "1122aabb..."  # hex-encoded public key
response = walletclient.getkey(myPubKey)
check(response)
print("Key: {}".format(response.json()["key"]))

# Sign a transaction
blob = b"data returned from a Vega node 'Prepare' call"
tx = base64.b64encode(blob).decode("ascii")
response = walletclient.signtx(tx, myPubKey)
check(response)
print("Signed tx: {}".format(response.json()["signedTx"]))

# When finished with the wallet, log out.
response = walletclient.logout()
check(response)
