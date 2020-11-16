#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega wallet (REST)

Apps/Libraries:
- REST: Vega-API-client (https://pypi.org/project/Vega-API-client/)
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
import os

# __import_client:
import vegaapiclient as vac

# :import_client__

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
# Create a new wallet
wallet_client = vac.WalletClient(wallet_server_url)
response = wallet_client.create(wallet_name, wallet_passphrase)
helpers.check_response(response)
# :create_wallet__


# The example below uses the credentials we just created
# and in practice you don't need to log in immediately after
# creating a new wallet, as the response already contains the
# token that you need to authenticate with future requests.


# __login_wallet:
# Log in to an existing wallet
response = wallet_client.login(wallet_name, wallet_passphrase)
helpers.check_response(response)
# :login_wallet__


# __generate_keypair:
# Generate a new keypair
response = wallet_client.generatekey(wallet_passphrase, [])
helpers.check_response(response)
# Print key information. Note that the private key is *not* returned.
keypair = response.json()["key"]
print("Generated new key pair:")
print(json.dumps(keypair, indent=2, sort_keys=True))
# :generate_keypair__


# __get_keys:
# Request all key pairs
response = wallet_client.listkeys()
helpers.check_response(response)
keys = response.json()["keys"]
for key in keys:
    print("List key pairs:")
    print(json.dumps(key, indent=2, sort_keys=True))
# :get_keys__


# __get_key:
# Request a single key pair
response = wallet_client.getkey(keys[0]["pub"])
helpers.check_response(response)
key = response.json()["key"]
print("Get a single key pair:")
print(json.dumps(key, indent=2, sort_keys=True))
# :get_key__


# __sign_tx:
# Sign a transaction
blob = b"data returned from a Vega node 'Prepare<operation>' call"
tx = base64.b64encode(blob).decode("ascii")
response = wallet_client.signtx(tx, keypair["pub"], propagate=False)
helpers.check_response(response)
signedTx = response.json()["signedTx"]
print("Signed transaction:")
print(json.dumps(signedTx, indent=2, sort_keys=True))
# :sign_tx__


# __logout_wallet:
# Log out of a wallet
response = wallet_client.logout()
helpers.check_response(response)
# :logout_wallet__
