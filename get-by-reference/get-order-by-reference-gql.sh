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
#                           GET ORDER BY REFERENCE                                  #
#####################################################################################

# __get_order_by_ref:
# Request an order by reference on a Vega network
# Note: This is an example and order reference will be provided in the response
# from a prepareSubmitOrder request in the field named `submitID` or similar.
cat >query <<EOF
query GetOrderByID(
  $orderID: ID! = "V0000021536-0000000059"
){
  orderByID(orderId:$orderID){
    id
    price
    timeInForce
    side
    size
    market{
      name
    }
    updatedAt
  }
}
EOF
gq $NODE_URL_GRAPHQL --queryFile=query
# :get_order_by_ref__
