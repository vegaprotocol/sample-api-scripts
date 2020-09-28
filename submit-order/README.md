[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Submit Order

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

Submit an order using shell scripts and `curl` [REST API]:

```bash
bash submit-order/submit-order.sh
```

## Python + requests

Submit an order using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 submit-order/submit-order.py
```

## Python + Vega-API-client

Submit an order using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [REST/gRPC API]:

```bash
python3 submit-order/submit-order-with-Vega-API-client.py
```

---

**[Home](../README.md)**
 
