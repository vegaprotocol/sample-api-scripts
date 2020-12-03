[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Estimate fees and margins

These scripts perform the following actions:

- Calculate the estimated fees for an order on Vega
- Calculate the estimated margins for an order on Vega

Please see the documentation on Vega for further information.

## Shell + curl

Calculate estimated trading fees and margin using shell scripts and `curl` only [REST API]:

```bash
bash fees-margins-estimation/get-fees-margins-estimate.sh
```

## Python + requests

Calculate estimated trading fees and margin using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 fees-margins-estimation/get-fees-margins-estimate.py
```

## Python + Vega-API-client

Calculate estimated trading fees and margin python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [gRPC API]:

```bash
python3 fees-margins-estimation/get-fees-margins-estimate-with-Vega-API-client.py
```

---

**[Home](../README.md)**
 
