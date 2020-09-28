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
from typing import List

import vegaapiclient as vac

import helpers


actions: List[str] = []
walletserver_url = os.getenv("WALLETSERVER_URL")
print(f"Using wallet server: {walletserver_url}")
if not helpers.check_url(walletserver_url):
    print("Error: Invalid WALLETSERVER_URL.")
    exit(1)

for suffix in ["/api/v1/", "/api/v1", "/"]:
    if walletserver_url.endswith(suffix):
        print(
            f"There's no need to add \"{suffix}\" to WALLETSERVER_URL. "
            "Removing it.")
        walletserver_url = walletserver_url[:-len(suffix)]

walletclient = vac.WalletClient(walletserver_url)

#

wallet_name = helpers.random_string()
print(f"Using random wallet name:       {wallet_name}")
wallet_passphrase = helpers.random_string()
print(f"Using random wallet passphrase: {wallet_passphrase}")

print("Creating a new wallet ...")
response = walletclient.create(wallet_name, wallet_passphrase)
# If you want to log in to an existing wallet, use:
# response = walletclient.login(wallet_name, wallet_passphrase)
helpers.check_response(response)
print("OK.")
actions.append(
    f"Created a new wallet (name: \"{wallet_name}\", passphrase: "
    f"\"{wallet_passphrase}\")"
)

#

print("Generating a new keypair ...")
response = walletclient.generatekey(wallet_passphrase, [])
helpers.check_response(response)
print("OK.")
# Print key information. Note that the private key is *not* returned.
key = response.json()["key"]
print("Details for the keypair you just created:")
print(json.dumps(key, indent=2, sort_keys=True))
myPubKey = key["pub"]
actions.append(f"Generated a new keypair (pubkey: {myPubKey})")
#

print("Getting all keypairs ...")
response = walletclient.listkeys()
helpers.check_response(response)
print("OK.")
keys = response.json()["keys"]
count = len(keys)
print(f"Got {count} keys.")
for i in range(count):
    print(f"Details for keypair #{i+1} of {count}:")
    print(json.dumps(keys[i], indent=2, sort_keys=True))
actions.append(f"Got a list of all keypairs (count: {count})")

#

print(f"Getting one keypair ({myPubKey}) ...")
response = walletclient.getkey(myPubKey)
helpers.check_response(response)
print("OK.")
key = response.json()["key"]
print(f"Got keypair ({myPubKey}):")
print(json.dumps(key, indent=2, sort_keys=True))
actions.append(f"Got one keypair (pubkey: {myPubKey})")

#

print("Signing a (fake) transaction ...")
blob = b"data returned from a Vega node 'Prepare' call"
tx = base64.b64encode(blob).decode("ascii")
response = walletclient.signtx(tx, myPubKey)
helpers.check_response(response)
print("OK.")
signedTx = response.json()["signedTx"]
print("Signed transaction:")
print(json.dumps(signedTx, indent=2, sort_keys=True))
actions.append("Signed a (fake) transaction")

#

print("Logging out of the wallet ...")
response = walletclient.logout()
helpers.check_response(response)
print("OK.")
actions.append("Logged out of the wallet")

#

print()
print("This is the end of the demo. Actions completed:")
print(os.linesep.join("- " + action for action in actions))