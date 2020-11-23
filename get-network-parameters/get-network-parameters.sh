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

#####################################################################################
#                        N E T W O R K   P A R A M E T E R S                        #
#####################################################################################

# __get_network_params:
# Request a list of network parameters configured on a Vega network
url="$NODE_URL_REST/network/parameters"
response="$(curl -s "$url")"
echo "Network Parameters:
$response"
# :get_network_params__
