[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Vega statistics

These scripts talk to a Vega node and get the latest statistics.  
Please see the documentation on Vega for further information.

## Shell + curl

Get the latest statistics using shell scripts and `curl` only [REST API]:

```bash
bash get-statistics/get-statistics.sh
```

## Python + requests

Get the latest statistics using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 get-statistics/get-statistics.py
```

## Python + Vega-API-client

Get the latest statistics using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [gRPC API]:

```bash
python3 get-statistics/get-statistics-with-Vega-API-client.py
```

## GraphQL
[![Graphql - Get-Statistics](https://img.shields.io/badge/Graphql-Get--Statistics-2ea44f?logo=GraphQL)](https://www.graphqlbin.com/v2/g8LlIm)
Get the latest statistics using shell scripts and [graphqurl](https://github.com/hasura/graphqurl) only [GraphQL API]:

```bash
bash get-statistics/get-statistics-gql.sh
```


---

**[Home](../README.md)**
 
