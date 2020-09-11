[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts

This repo contains sample scripts in various languages. These scripts use the
Vega core and wallet APIs to interact with Vega core nodes and wallet servers.

# Gitpod

Get started with the sample API scripts with zero configuration. Click on the
"Gitpod ready-to-code" button above.

# Getting started

1. Copy the credentials file from template: `cp credentials-template credentials`
1. Edit the credentials file. (Use `nano` or `vim` or the built-in Gitpod text editor.)
1. Set variables in local environment: `source credentials`

And you're good to go. Now choose a sample program to run from the following:

# Stream market data

This Python script talks to a Vega node and:

- (REST) gets a list of markets
- (GraphQL) streams market data for the first market found

```bash
python3 stream-marketdata/stream-marketdata.py
```

# Wallet

This test script contains sample code for interacting with a Vega Wallet server.

```bash
python3 wallet/wallet.py
```

# Submit Order

| Language | Talks to                        | App/Library |
| :------- | :------------------------------ | :---------- |
| bash     | wallet (REST), Vega node (REST) | REST: curl  |
| python3  | wallet (REST), Vega node (REST) | REST: [requests](https://pypi.org/project/requests/) |
| python3  | wallet (REST), Vega node (gRPC) | REST: [requests](https://pypi.org/project/requests/); gRPC: [Vega-API-client](https://pypi.org/project/Vega-API-client/) |

These test scripts connect to a Vega Wallet server and a Vega API node, and does the following:

1. Wallet server: create a new wallet, or logs in to an existing one
1. Wallet server: create a keypair, if one has not already been created
1. Vega node: call `PrepareSubmitOrder`
   - send: the order details
   - receive: a `PreparedOrder` object
1. Wallet server: calls `SignTx`
   - send:
     - the `PreparedOrder` object
     - the public key associated with the logged-in wallet
   - receive: a `SignedBundle`
1. Vega node: calls `SubmitTransaction`
   - send: the `SignedBundle`
   - receive: a simple acknowledgement (success true/false), which indicates
     that the transaction has been received, but _not_ that the transaction has
     been added to the blockchain yet.

## Shell + curl

```bash
bash submit-order/submit-order.sh
```

## Python + requests

```bash
python3 submit-order/submit-order.py
```

## Python + Vega-API-client

```bash
python3 submit-order/submit-order-with-Vega-API-client.py
```
