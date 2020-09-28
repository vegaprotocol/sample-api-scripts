[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Vega/blockchain time

These scripts talk to a Vega node and get the latest time on the blockchain. 
Please see the documentation on Vega for further information.

## Shell + curl

Get the latest time on the blockchain using shell scripts and `curl` only [REST API]:

```bash
bash vega-time/get-time.sh
```

## Python + requests

Get the latest time on the blockchain using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 vega-time/get-time.py
```

## Python + Vega-API-client

Get the latest time on the blockchain using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [gRPC API]:

```bash
python3 vega-time/get-time-with-Vega-API-client.py
```

---

**[Home](../README.md)**
 
