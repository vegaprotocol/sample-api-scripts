#!/usr/bin/env bash

# Script language: bash
#
# Talks to:
# - Vega node (REST)
#
# Apps/Libraries:
# - REST: curl

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

# __get_time:
# Request the latest timestamp in nanoseconds since epoch from the Vega network
url="$NODE_URL_REST/time"
response="$(curl -s "$url")"
vegatime="$(echo "$response" | jq -r .timestamp)"
echo "Vega time:
$vegatime"
# :get_time__