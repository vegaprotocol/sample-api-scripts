[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Stream orders and trades

| File | Language | Talks to                        | App/Library |
| :--- | :------- | :------------------------------ | :---------- |
| stream-orders-with-Vega-API-client.py  | python3  | Vega Node (gRPC) | gRPC: [Vega-API-client](https://pypi.org/project/Vega-API-client/) |
| stream-trades-with-Vega-API-client.py  | python3  | Vega Node (gRPC) | gRPC: [Vega-API-client](https://pypi.org/project/Vega-API-client/) |

These example scripts connect to a Vega Node API, and:

1. Subscribe to a stream of **orders** from a valid Market on a Vega network.
1. Subscribe to a stream of **trades** from a valid Market on a Vega network.

Note: Streaming is available on the Vega gRPC API (highest performance) and Vega GraphQL API **only**.  
*The GraphQL streaming protocol uses websockets under the hood, we recommend using a GraphQL client with support for streaming.*

## Shell + graphqurl
[![Graphql - Stream-Orders](https://img.shields.io/badge/Graphql-Stream--Orders-2ea44f?logo=GraphQL)](https://graphqlbin.com/v2/MNJztz)
[![Graphql - Stream-Trades](https://img.shields.io/badge/Graphql-Stream--Trades-2ea44f?logo=GraphQL)](https://graphqlbin.com/v2/KzLqhD)

Stream using shell scripts and [graphqurl](https://github.com/hasura/graphqurl) only [GraphQL API]:

```bash
bash stream-orders-and-trades/stream-orders.sh
bash stream-orders-and-trades/stream-trades.sh
```


---

**[Home](../README.md)**