#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega data node (REST)
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

import sys
import requests
import time
import os
import helpers

def main():
    node_url_rest = os.getenv("NODE_URL_REST")
    if not helpers.check_url(node_url_rest):
        print("Error: Invalid or missing NODE_URL_REST environment variable.")
        sys.exit(1)

    wallet_server_url = os.getenv("WALLETSERVER_URL")

    wallet_name = os.getenv("WALLET_NAME")
    if not helpers.check_var(wallet_name):
        print("Error: Invalid or missing WALLET_NAME environment variable.")
        sys.exit(1)

    wallet_passphrase = os.getenv("WALLET_PASSPHRASE")
    if not helpers.check_var(wallet_passphrase):
        print("Error: Invalid or missing WALLET_PASSPHRASE environment variable.")
        sys.exit(1)

    # Help guide users against including api version suffix on url
    wallet_server_url = helpers.check_wallet_url(wallet_server_url)

    #####################################################################################
    #                           W A L L E T   S E R V I C E                             #
    #####################################################################################

    print(f"Logging into wallet: {wallet_name}")

    # __login_wallet:
    # Log in to an existing wallet
    req = {"wallet": wallet_name, "passphrase": wallet_passphrase}
    response = requests.post(f"{wallet_server_url}/api/v1/auth/token", json=req)
    helpers.check_response(response)
    token = response.json()["token"]
    # :login_wallet__

    assert token != ""
    print("Logged in to wallet successfully")

    # __get_pubkey:
    # List key pairs and select public key to use
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{wallet_server_url}/api/v1/keys", headers=headers)
    helpers.check_response(response)
    keys = response.json()["keys"]
    pubkey = keys[0]["pub"]
    # :get_pubkey__

    assert pubkey
    print("Selected pubkey for signing")

    #####################################################################################
    #                           F I N D   P R O P O S A L S                             #
    #####################################################################################

    # __get_proposals_for_party:
    # Request a list of proposals available for party/pubkey
    url = f"{node_url_rest}/parties/{pubkey}/proposals"
    response = requests.get(url)
    helpers.check_response(response)
    # :get_proposals_for_party__

    # Debugging
    # print(response.json())

    print(f"Listing proposals for pubkey {pubkey}:")
    
    freeform_total = 0

    proposals = response.json()["data"]
    for proposal in proposals:
        proposal_id = proposal["proposal"]["id"]
        proposal_state = proposal["proposal"]["state"]
        proposal_ref = proposal["proposal"]["reference"]
        proposal_terms = proposal["proposal"]["terms"]
        print(f"\nid: {proposal_id} - state: {proposal_state} - ref: {proposal_ref}")
        print(f"{proposal_terms}")
        if "newFreeform" in proposal_terms:
            freeform_total = freeform_total+1
            print("^^ freeform governance proposal found ^^")

    print(f"\nTotal proposals found: {len(proposals)}")
    print(f" - of which freeform proposals found: {freeform_total}")


if __name__ == "__main__":
    main()