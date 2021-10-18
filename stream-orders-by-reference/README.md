[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Stream orders by reference

These scripts talk to a Vega node and stream a list of orders with the aim of filtering on reference.
Please see the documentation on Vega for further information.

## Shell + graphqurl
[![Graphql - Stream-OrdersByReference](https://img.shields.io/badge/Graphql-Stream--OrdersByReference-2ea44f?logo=GraphQL)](https://graphqlbin.com/v2/L0vkuQ)

Stream using shell scripts and [graphqurl](https://github.com/hasura/graphqurl) only [GraphQL API]:

```bash
bash stream-orders-by-reference/stream-orders.sh
```

## Python + Vega-API-client

Stream orders using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [REST API]:

```bash
python3 stream-orders-by-reference/stream-orders-with-Vega-API-client.py
```

---

**[Home](../README.md)**
