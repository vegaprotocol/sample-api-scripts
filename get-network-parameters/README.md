[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Network parameters

These scripts talk to a Vega node and will return the current set of network parameters.  
Please see the documentation on Vega for further information.

## Shell + curl

Get network parameters using shell scripts and `curl` only [REST API]:

```bash
bash get-network-parameters/get-network-parameters.sh
```

## Python + requests

Get network parameters using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 get-network-parameters/get-network-parameters.py
```

## Python + Vega-API-client

Get network parameters using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [gRPC API]:

```bash
python3 get-network-parameters/get-network-parameters-with-Vega-API-client.py
```

---

**[Home](../README.md)**