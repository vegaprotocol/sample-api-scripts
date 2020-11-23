[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - List orders and trades

These scripts perform the following actions:

- Get a list of orders and trades for a market on Vega
- Get a list of orders and trades for a party on Vega
- Get a list of trades for a specific order on Vega
 
Please see the documentation on Vega for further information.

## Shell + curl

Get orders and trades using shell scripts and `curl` only [REST API]:

```bash
bash get-orders-and-trades/get-orders-and-trades-for-market.sh
```
```bash
bash get-orders-and-trades/get-orders-and-trades-for-party.sh
```
```bash
bash get-orders-and-trades/get-trades-for-order.sh
```

## Python + requests

Get orders and trades using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 get-orders-and-trades/get-orders-and-trades-for-market.py
```
```bash
python3 get-orders-and-trades/get-orders-and-trades-for-party.py
```
```bash
python3 get-orders-and-trades/get-trades-for-order.py
```

## Python + Vega-API-client

Get orders and trades using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [gRPC API]:

```bash
python3 get-orders-and-trades/get-orders-and-trades-for-market-with-Vega-API-client.py
```
```bash
python3 get-orders-and-trades/get-orders-and-trades-for-party-with-Vega-API-client.py
```
```bash
python3 get-orders-and-trades/get-trades-for-order-with-Vega-API-client.py
```

---

**[Home](../README.md)**