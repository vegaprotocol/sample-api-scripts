[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts

This repo contains sample scripts in various languages. These scripts use the
Vega core and wallet APIs to interact with Vega core nodes and wallet servers.

# Gitpod

Get started with the sample API scripts with zero configuration. Click on the
"Gitpod ready-to-code" button above.

# Getting started

1. Copy or rename the `credentials-template` file as `credentials`.  
*Note: When running on Gitpod this is already done for you.*
1. Edit the `credentials` file. (`nano` and `vim` are installed, or use the built-in Gitpod text editor.)
1. Import the credentials into your local environment: `source credentials`

And you're good to go. Now choose a sample program to run from the following (see the link in the **Folder** column to learn how to run each sample script):

# Sample scripts

| Script description            | Languages |   API transport                      | Folder & README |
| :----------------- | :------- | :------------------------------ | :---------- |
| Orders by reference | bash, python3 | Vega node [REST, gRPC]  | / [get-by-reference](get-by-reference) |
| List market details and market data | bash, python3  | Vega node [REST, gRPC]  | / [get-markets-and-market-data](get-markets-and-market-data) |
| List orders and trades | bash, python3 | Vega node [REST, gRPC]  | / [get-orders-and-trades](get-orders-and-trades) |
| Vega statistics | bash, python3 | Vega node [REST, gRPC]  | / [get-statistics](get-statistics) |
| List parties | bash, python3 | Vega node [REST, gRPC]  | / [parties-and-accounts](parties-and-accounts) |
| Stream market data | python3 | Vega node [GraphQL] | / [stream-marketdata](stream-marketdata) |
| Stream orders and trades | python3  | Vega node [GraphQL] | / [stream-orders-and-trades](stream-orders-and-trades) |
| Interact with Vega wallet API | bash, python3 | Vega wallet [REST] | / [wallet](wallet) |
| Submit, amend and cancel orders | bash, python3 | Vega wallet [REST], Vega node [REST, gRPC] | / [submit-amend-cancel-orders](submit-amend-cancel-orders) |
| Submit order (tutorial, inc send tx) | bash, python3 | Vega wallet [REST], Vega node [REST, gRPC] | / [submit-order](submit-order) |
| Vega/blockchain time  | bash, python3 | Vega node [REST, gRPC] | / [vega-time](vega-time) |
| Streaming events | bash, python3 | Vega node [GraphQL, gRPC] | / [stream-events](stream-events) |
| Fees estimation | bash, python3 | Vega node [REST, gRPC] | / [fees-estimation](fees-estimation) |

# Contributing or raising issues

Please reach out to us on the [community forums](https://community.vega.xyz/c/testnet/) or [Discord chat](https://discord.gg/bkAF3Tu) to enquire further about how to get involved with Vega.

If you have found an issue or would like to suggest an improvement with our public code samples, please raise an issue in the [Sample-API-Scripts](https://github.com/vegaprotocol/sample-api-scripts/) repository. If you'd like to submit a PR we welcome additional sample code.