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
#                           GET STATISTICS                                          #
#####################################################################################

# __get_statistics:
# Request the statistics for a node on Vega
cat >query <<EOF
query getStatistics {
    statistics {
        chainVersion
        appVersion
        status
        totalTrades
        totalOrders
        totalPeers
        totalMarkets
        ordersPerSecond
        tradesPerSecond
        averageOrdersPerBlock
        averageTxBytes
    }
}
EOF
gq $NODE_URL_GRAPHQL --queryFile=query
# :get_statistics__
rm query
