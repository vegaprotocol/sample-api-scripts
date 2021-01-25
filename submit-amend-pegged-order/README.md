[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Submit and Amend Pegged orders

These scripts talk to a Vega node as well as a Vega wallet and:

- Login to existing wallet
- Select key-pair
- Prepare and submit a new pegged order
- Wait for order to be accepted and processed
- Amend the pegged order, demonstrating the different fields for pegged order amendment

Please see the [documentation](https://docs.testnet.vega.xyz) on Vega for further information.

## Shell + curl

Interact with wallet and node API operations using shell scripts and `curl` [REST API]:

```bash
bash submit-amend-pegged-order/submit-amend-pegged-order.sh
```

## Python + requests

Interact with wallet and node API operations using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 submit-amend-pegged-order/submit-amend-pegged-order.py
```

## Python + Vega-API-client

Interact with wallet and node API operations using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [REST API]:

```bash
python3 submit-amend-pegged-order/submit-amend-pegged-order-with-Vega-API-client.py
```
 
---

**[Home](../README.md)**
 
