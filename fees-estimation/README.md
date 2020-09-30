[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Estimate fees

These scripts talk to a Vega node and will calculate the estimated fees for an order.  
Please see the documentation on Vega for further information.

## Shell + curl

Calculate estimated fees using shell scripts and `curl` only [REST API]:

```bash
bash fees-estimation/get-fees-estimate.sh
```

## Python + requests

Calculate estimated fees using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 fees-estimation/get-fees-estimate.py
```

## Python + Vega-API-client

Calculate estimated fees python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [gRPC API]:

```bash
python3 fees-estimation/get-fees-estimate-with-Vega-API-client.py
```

---

**[Home](../README.md)**
 
