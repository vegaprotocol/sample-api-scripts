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
#                            L I S T   P R O P O S A L S                            #
#####################################################################################

# __get_proposals:
# Request a list of proposals on a Vega network
cat >query <<EOF
query {
  proposals {
    id
    datetime
    party { id }
    reference
    state
    terms { closingDatetime, enactmentDatetime}
    yesVotes { value, party { id }, datetime}
    noVotes { value, party { id }, datetime}
  }
}
EOF
gq $NODE_URL_GRAPHQL --queryFile=query
# :get_proposals__

#####################################################################################
#                         P R O P O S A L   D E T A I L S                           #
#####################################################################################

# __get_proposal_detail:
# Request results of a specific proposal on a Vega network
cat >query <<EOF
query {
  proposal(id:"9c45820e31fcd4bbea6a7b15c50006b30c03c850d7acd3a52760a1dfa31b040a") {
    id
    datetime
    party { id }
    reference
    state
    terms { closingDatetime, enactmentDatetime}
    yesVotes { value, party { id }, datetime}
    noVotes { value, party { id }, datetime}
  }
}
EOF
gq $NODE_URL_GRAPHQL --queryFile=query
# :get_proposal_detail

#####################################################################################
#                          P A R T Y   P R O P O S A L S                            #
#####################################################################################

# __get_proposals_by_party:
# Request results of a specific proposal on a Vega network
cat >query <<EOF
query {
  party(id:"bf9bfdf020c8dfdbdf2ae61e3ed1892b83ab47942cd67a04bfd4e70bc8f7ef42") {
    proposals {
      id
      datetime
      reference
      state
      terms { closingDatetime, enactmentDatetime}
      yesVotes { value, party { id }, datetime}
      noVotes { value, party { id }, datetime}
    }
  }
}
EOF
gq $NODE_URL_GRAPHQL --queryFile=query
# :get_proposals_by_party