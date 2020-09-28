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

---

**[Home](../README.md)**