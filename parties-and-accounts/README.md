[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - List Parties

These scripts perform the following actions:

- Get a list of parties on Vega
- Get a party for a given identifier (pubkey)
- Get a list of accounts for a market on Vega
- Get a list of accounts for a party on Vega

Please see the documentation on Vega for further information.

## Shell + curl

Get parties and accounts on Vega using shell scripts and `curl` only [REST API]:

```bash
bash parties-and-accounts/get-parties.sh
```

```bash
bash parties-and-accounts/get-accounts.sh
```

## Python + requests

Get parties and accounts on Vega using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 parties-and-accounts/get-parties.py
```

```bash
python3 parties-and-accounts/get-accounts.py
```

## Python + Vega-API-client

Get parties and accounts on Vega using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [gRPC API]:

```bash
python3 parties-and-accounts/get-parties-with-Vega-API-client.py
```

```bash
python3 parties-and-accounts/get-accounts-with-Vega-API-client.py
```

---

**[Home](../README.md)**
 
