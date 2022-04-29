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
#                           STREAM ORDERS                                           #
#####################################################################################

# __stream_orders:
# Subscribe to the Orders stream for the marketID specified
# Optional: Market identifier - filter by market
#            Party identifier - filter by party
# By default, all orders on all markets for all parties will be returned on the stream.
cat >query <<EOF
subscription StreamOrders{
  orders{
    id
    price
    timeInForce
    side
    market{
      name
    }
    size
  }
}
}
EOF
gq $NODE_URL_GRAPHQL "$GQL_HEADER" --queryFile=query
# :stream_orders__