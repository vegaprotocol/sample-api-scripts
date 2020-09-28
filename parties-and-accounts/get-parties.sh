#!/usr/bin/env bash

# Script language: bash
#
# Talks to:
# - Vega node (REST)
#
# Apps/Libraries:
# - REST: curl
#
# Responses:
# - response-examples.txt

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__

source helpers.sh

check_url "NODE_URL_REST" || exit 1

# __get_parties:
# Request a list of parties trading on a Vega network
url="$NODE_URL_REST/parties"
response="$(curl -s "$url")"
parties="$(echo "$response" | jq -r .parties)"
echo "Parties:
$parties"
# :get_parties__