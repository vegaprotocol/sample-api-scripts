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

## Go

Get the latest time on the blockchain using go [gRPC API]:

```bash
go run vega-time/get-time.go
```

## GraphQL
[![Graphql - Get-VegaTime](https://img.shields.io/badge/Graphql-Get--VegaTime-2ea44f?logo=GraphQL)](https://graphqlbin.com/v2/JzNMUQ)

Get the latest time on the blockchain using shell scripts and [graphqurl](https://github.com/hasura/graphqurl) only [GraphQL API]:

```bash
bash vega-time/get-time-gql.sh
```



---

**[Home](../README.md)**
 
