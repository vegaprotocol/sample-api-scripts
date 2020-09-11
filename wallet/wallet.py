#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega wallet (REST)

Apps/Libraries:
- REST: Vega-API-client (https://pypi.org/project/Vega-API-client/)
"""

import base64
import json
import os

import vegaapiclient as vac

import helpers


walletserver_url = os.getenv("WALLETSERVER_URL")
if not helpers.check_url(walletserver_url):
    print("Error: Invalid WALLETSERVER_URL.")
    exit(1)

walletclient = vac.WalletClient(walletserver_url)

wallet_name = helpers.random_string()
wallet_passphrase = helpers.random_string()

print(f"Creating a new wallet on {walletserver_url}:")
print(f"- name:       {wallet_name}")
print(f"- passphrase: {wallet_passphrase}")
response = walletclient.create(wallet_name, wallet_passphrase)

# If you want to log in to an existing wallet, use:
# response = walletclient.login(wallet_name, wallet_passphrase)

helpers.check_response(response)

# Generate a new keypair.
response = walletclient.generatekey(wallet_passphrase, [])
helpers.check_response(response)
# Print key information. Note that the private key is *not* returned.
myPubKey = response.json()["key"]
print("Generated new keypair:")
print(json.dumps(myPubKey, indent=2, sort_keys=True))

# Get all keypairs
response = walletclient.listkeys()
helpers.check_response(response)
keys = response.json()["keys"]
for key in keys:
    print("List keypairs:")
    print(json.dumps(key, indent=2, sort_keys=True))

# Get one keypair
response = walletclient.getkey(keys[0]["pub"])
helpers.check_response(response)
key = response.json()["key"]
print("Get one keypair:")
print(json.dumps(key, indent=2, sort_keys=True))

# Sign a transaction
blob = b"data returned from a Vega node 'Prepare' call"
tx = base64.b64encode(blob).decode("ascii")
response = walletclient.signtx(tx, myPubKey["pub"])
helpers.check_response(response)
signedTx = response.json()["signedTx"]
print("Signed transaction:")
print(json.dumps(signedTx, indent=2, sort_keys=True))

# When finished with the wallet, log out.
response = walletclient.logout()
helpers.check_response(response)
