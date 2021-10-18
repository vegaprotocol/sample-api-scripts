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
#                           STREAM MARKET DATA                                      #
#####################################################################################

# __stream_marketdata:
# Subscribe to the Market Data stream for the marketID specified
cat >query <<EOF
subscription StreamMarketData (
  $marketID: ID! = "9b358cb36b63001ae74b9f815c30a58f1db258fa11b17ba082a66abebed75951",
){
  marketData(marketId:$marketID){
    bestBidPrice
    bestBidVolume
    bestOfferPrice
    bestOfferVolume
    midPrice
    timestamp
    marketTradingMode
  }
}
EOF
gq $NODE_URL_GRAPHQL --queryFile=query
# :stream_marketdata__