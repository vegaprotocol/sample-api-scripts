[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Markets and market data

These scripts talk to a Vega node and get market details and market data:

1. Retrieve and display a list of all markets on the connected Vega network.
1. Using a valid Market identifier (e.g. LBXRA65PN4FN5HBWRI2YBCOYDG2PBGYU) load a list of related market data.

Please see the documentation on Vega for further information.

## Shell + curl

Get the market details and market data using shell scripts and `curl` only [REST API]:

```bash
bash get-markets-and-market-data/get-markets-and-marketdata.sh
```

## Python + requests

Get market details and market data using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 get-markets-and-market-data/get-markets-and-marketdata.py
```

## Python + Vega-API-client

Get market details and market data using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [gRPC API]:

```bash
python3 get-markets-and-market-data/get-markets-and-marketdata-with-Vega-API-client.py
```

---

**[Home](../README.md)**
