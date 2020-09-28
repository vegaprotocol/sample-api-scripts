[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Order by reference

These scripts talk to a Vega node and get an order by its unique `reference` field).  
Please see the documentation on Vega for further information.

## Shell + curl

Get an order by reference using shell scripts and `curl` only [REST API]:

```bash
bash get-order-by-reference/get-order-by-reference.sh
```

## Python + requests

Get an order by reference using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 get-order-by-reference/get-order-by-reference.py
```

## Python + Vega-API-client

Get an order by reference using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [gRPC API]:

```bash
python3 get-order-by-reference/get-order-by-reference-with-Vega-API-client.py
```

---

**[Home](../README.md)**
 
