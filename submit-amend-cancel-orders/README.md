[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Wallet

These scripts talk to a Vega node as well as a Vega wallet and:

- Login to existing wallet
- Select key-pair
- Prepare and submit a new order
- Wait for order to be accepted and processed
- Amend the order [coming soon]
- Cancel the order
- Cancel all orders [coming soon] 

Please see the documentation on Vega for further information.

## Shell + curl

Interact with wallet and node API operations using shell scripts and `curl` [REST API]:

```bash
bash submit-amend-cancel-orders/submit-amend-cancel-orders.sh
```

## Python + requests

Interact with wallet and node API operations using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 submit-amend-cancel-orders/submit-amend-cancel-orders.py
```

## Python + Vega-API-client

Interact with wallet and node API operations using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [REST API]:

```bash
python3 submit-amend-cancel-orders/submit-amend-cancel-orders-with-Vega-API-client.py
```
 
---

**[Home](../README.md)**
 