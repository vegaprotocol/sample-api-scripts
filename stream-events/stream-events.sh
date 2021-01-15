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
check_url "NODE_URL_REST" || exit 1
check_url "NODE_URL_GRAPHQL" || exit 1

# __get_market:
# Request the identifier for a market
url="$NODE_URL_REST/markets"
response="$(curl -s "$url")"
marketID="$(echo "$response" | jq -r '.markets[0].id')"
echo $marketID
# :get_market__

# __stream_events:
# Subscribe to the events bus stream for the marketID specified, 
# Required: type field - Switch the event type with '... on [TYPE]' syntax, NOTE: All event is not supported by GraphQL API.
# Required: batchSize field - Default: 0 - Total number of events to batch on server before sending to client.
# Optional: Market identifier - filter by market
#           Party identifier - filter by party
# By default, all events on all markets for all parties will be returned on the stream.
# Event types and schema can be found here: https://docs.testnet.vega.xyz/docs/api-howtos/event-stream/
gq $NODE_URL_GRAPHQL -q 'subscription { busEvents(batchSize: 0, types: [Order], marketID: "'$marketID'" ) { 
    type 
    event
    { 
        ... on Order {
              id
              side
              price
              timeInForce
              side
              market { id }
              size
              remaining
              party { id }
              createdAt
              expiresAt
              status
              reference
              trades { id, size, aggressor }
              type
              rejectionReason
              version
              updatedAt
        }
        ... on TimeUpdate {
              timestamp
        }
    }
}}'
# :stream_events__

# Another example, with even deeper graphql nesting would be to select on Governance Proposals:
#
# gq $NODE_URL_GRAPHQL -q 'subscription { busEvents(batchSize: 0, types: [Proposal] ) { 
#     type 
#     event
#     { 
#         ... on Proposal {
#                 id
#                 datetime
#                 yesVotes {
#                   value
#                   party { id }
#                 }
#                 noVotes {
#                   value
#                   party { id }
#                 }
#                 party {
#                   id
#                 }
#                 reference
#                 state
#                 terms {
#                   closingDatetime
#                   enactmentDatetime
#                   change {
#                     ... on NewMarket {
#                       instrument {
#                         code
#                       }
#                       decimalPlaces
#                       tradingMode {
#                         ... on ContinuousTrading {
#                           tickSize
#                         }
#                         ... on DiscreteTrading {
#                           tickSize
#                           duration
#                         }
#                       }
#                       riskParameters {
#                         ... on LogNormalRiskModel {
#                           tau
#                           riskAversionParameter
#                           params {
#                             r
#                             sigma
#                             mu
#                           }
#                         }
#                       }
#                     }
#                     ... on NewAsset {
#                       source {
#                         ... on BuiltinAsset {
#                           id
#                         }
#                       }
#                     }
#                   }
#                }
#             }
#         }
#     }
# }'
