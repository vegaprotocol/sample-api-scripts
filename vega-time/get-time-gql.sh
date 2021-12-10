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
#                           GET VEGA TIME                                           #
#####################################################################################

# __get_time:
# Request the latest timestamp in nanoseconds since epoch from the Vega network
cat >query <<EOF
query GetVegaTime {
  statistics{
    vegaTime
  }
}
EOF
gq $NODE_URL_GRAPHQL --queryFile=query
# :get_time__
rm query
