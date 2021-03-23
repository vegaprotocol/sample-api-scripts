#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega wallet (REST)

Apps/Libraries:
- REST: requests (https://pypi.org/project/requests/)
"""

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__

import base64
import json
import requests
import os

import helpers

wallet_name = helpers.random_string()
wallet_passphrase = helpers.random_string()

wallet_server_url = os.getenv("WALLETSERVER_URL")
if not helpers.check_url(wallet_server_url):
    print("Error: Invalid or missing WALLETSERVER_URL environment variable.")
    exit(1)

# Help guide users against including api version suffix on url
wallet_server_url = helpers.check_wallet_url(wallet_server_url)

print(f"Creating a new wallet on {wallet_server_url}:")
print(f"- name:       {wallet_name}")
print(f"- passphrase: {wallet_passphrase}")


# __create_wallet:
# Create a new wallet:
req = {"wallet": wallet_name, "passphrase": wallet_passphrase}
response = requests.post(f"{wallet_server_url}/api/v1/wallets", json=req)
helpers.check_response(response)
token = response.json()["token"]
# :create_wallet__


# The example below uses the credentials we just created
# and in practice you don't need to log in immediately after
# creating a new wallet, as the response already contains the
# token that you need to authenticate with future requests.


# __login_wallet:
# Log in to an existing wallet
req = {"wallet": wallet_name, "passphrase": wallet_passphrase}
response = requests.post(f"{wallet_server_url}/api/v1/auth/token", json=req)
helpers.check_response(response)
token = response.json()["token"]
# :login_wallet__


# __generate_keypair:
# Generate a new key pair
headers = {"Authorization": f"Bearer {token}"}
req = {
    "passphrase": wallet_passphrase,
    "meta": [{"key": "alias", "value": "my_key_alias"}],
}
response = requests.post(
    f"{wallet_server_url}/api/v1/keys", headers=headers, json=req
)
helpers.check_response(response)
pubkey = response.json()["key"]["pub"]
# Print key information. Note that the private key is *not* returned.
keypair = response.json()["key"]
print("Generated new keypair:")
print(json.dumps(keypair, indent=2, sort_keys=True))
# :generate_keypair__


# __get_keys:
# Request all key pairs
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{wallet_server_url}/api/v1/keys", headers=headers)
helpers.check_response(response)
keys = response.json()["keys"]
for key in keys:
    print("List key pairs:")
    print(json.dumps(key, indent=2, sort_keys=True))
# :get_keys__

pubkey = keys[0]["pub"]

# __get_key:
# Request a single key pair
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    f"{wallet_server_url}/api/v1/keys/{pubkey}", headers=headers
)
helpers.check_response(response)
key = response.json()["key"]
print("Get a single keypair:")
print(json.dumps(key, indent=2, sort_keys=True))
# :get_key__


# __sign_tx:
# Sign a transaction - Note: setting "propagate" to True will also submit the
# tx to Vega node
headers = {"Authorization": f"Bearer {token}"}
blob = b"data returned from a Vega node 'Prepare<operation>' call"
tx = base64.b64encode(blob).decode("ascii")
req = {"tx": tx, "pubKey": pubkey, "propagate": False}
response = requests.post(
    f"{wallet_server_url}/api/v1/messages/sync", headers=headers, json=req
)
helpers.check_response(response)
signedTx = response.json()["signedTx"]
print("Signed transaction:")
print(json.dumps(signedTx, indent=2, sort_keys=True))
# :sign_tx__


# __logout_wallet:
# Log out of a wallet
headers = {"Authorization": f"Bearer {token}"}
response = requests.delete(
    f"{wallet_server_url}/api/v1/auth/token", headers=headers
)
helpers.check_response(response)
# :logout_wallet__
