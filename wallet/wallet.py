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
    assert r.status_code == 200, f"HTTP {r.status_code} {r.text}"


walletclient = vac.WalletClient(WALLETSERVER_URL)

CREATE_NEW_WALLET = False
if CREATE_NEW_WALLET:
    # If this is your first time: create a new wallet.
    response = walletclient.create(WALLET_NAME, WALLET_PASSPHRASE)
else:
    # If this is *not* your first time: log in to an existing wallet.
    response = walletclient.login(WALLET_NAME, WALLET_PASSPHRASE)
check(response)

# Generate a new keypair.
response = walletclient.generatekey(WALLET_PASSPHRASE, [])
check(response)
# Print key information. Note that the private key is *not* returned.
myPubKey = response.json()["key"]
print(f"Generated new keypair: {myPubKey}")

# Get all keypairs
response = walletclient.listkeys()
check(response)
keys = response.json()["keys"]
for key in keys:
    print(f"(listkeys) Key: {key}")

# Get one keypair
response = walletclient.getkey(keys[0]["pub"])
check(response)
key = response.json()["key"]
print(f"(getkey) Key: {key}")

# Sign a transaction
blob = b"data returned from a Vega node 'Prepare' call"
tx = base64.b64encode(blob).decode("ascii")
response = walletclient.signtx(tx, myPubKey["pub"])
check(response)
signedTx = response.json()["signedTx"]
print(f"Signed tx: {signedTx}")

# When finished with the wallet, log out.
response = walletclient.logout()
check(response)
