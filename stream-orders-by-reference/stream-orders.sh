#!/usr/bin/env bash

# Script language: bash

# Talks to:
# - Vega node (GraphQL)
#
# Apps/Libraries:
# - GraphQL: graphqurl (https://github.com/hasura/graphqurl)

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

# __stream_orders_by_ref:
# Stream orders by reference on a Vega network
# Note: This is an example and order reference will be provided in the response
# from a prepareSubmitOrder request in the field named `submitID` or similar.
reference="4617844f-6fab-4cf6-8852-e29dbd96e5f1"
pubkey="94c21a5bfc212c0b4ee6e3593e8481559972ad31f1fb453491f255e72bdb6fdb"
gq $NODE_URL_GRAPHQL -q 'subscription { orders(partyId: "'$pubkey'") { id, reference } }'
# In target language, filter the result stream and search for orders matching the reference
# :stream_orders_by_ref__
