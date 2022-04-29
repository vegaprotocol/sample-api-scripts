#!/usr/bin/env bash

# Script language: bash

# Talks to:
# - Vega node (GraphQL)
#
# Apps/Libraries:
# - GraphQL: graphqurl (https://github.com/hasura/graphqurl)
# - REST: curl

# Note: this file uses smart-tags in comments to section parts of the code to
# show them as snippets in our documentation. They are not necessary to be
# included when creating your own custom code.
#
# Example of smart-tags:
#  __something:
# some code here
# :something__
#

source helpers.sh
check_url "NODE_URL_GRAPHQL" || exit 1

#####################################################################################
#                           GET NETWORK PARAMETERS                                  #
#####################################################################################

# __get_network_params:
# Request a list of network parameters configured on a Vega network
cat >query <<EOF
query GetNetworkParameters{
  networkParameters{
    key
    value
  }
}
EOF
gq $NODE_URL_GRAPHQL "$GQL_HEADER" --queryFile=query
# :get_network_params__
