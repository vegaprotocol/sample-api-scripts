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
#                           GET ASSET                                               #
#####################################################################################

# __get_asset:
# Request a list of assets available on a Vega network
cat >query <<EOF
query getAsset (\$assetId: ID! = "6d9d35f657589e40ddfb448b7ad4a7463b66efb307527fedd2aa7df1bbd5ea61") {
  asset(assetId: \$assetId){
    name
    symbol
    totalSupply
    decimals
		source{
      __typename
    }
  }
}
EOF
gq $NODE_URL_GRAPHQL --queryFile=query
# :get_asset__
